"""
从 Wikipedia/Wikidata 批量获取高校官方网站 + 主要院系。

字段映射：
  school.website        ← Wikidata P856（官方网站）
  school.popular_majors ← Wikidata P527（hasPart / 主要院系），去掉学校名前缀后存为列表

原理（每批 45 所）：
  1. 批量查 zh.Wikipedia → Wikidata QID
  2. 批量查 Wikidata claims（P856 + P527）
  3. 写入数据库

运行：
  cd backend
  python scripts/scrape_wikidata.py              # 只处理 website=NULL 的学校
  python scripts/scrape_wikidata.py --all        # 覆盖所有
  python scripts/scrape_wikidata.py --dry-run    # 不写库，仅打印
  python scripts/scrape_wikidata.py --limit 100  # 限制条数（测试）
"""

import argparse
import io
import os
import re
import sys
import time

import requests
from sqlalchemy import select, update, or_

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import SessionLocal
from app.models.school import School

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ChinaUniversityMapBot/1.0; personal-project)"}
BATCH = 45       # Wikipedia/Wikidata 每次最多 50 条
DELAY = 1.5      # 批次间延迟（秒）
MAX_MAJORS = 15  # 每所学校最多保留 N 个院系名


def _get(url: str, timeout: int = 15) -> dict | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"  [HTTP] {e}")
        return None


def batch_get_qids(names: list[str]) -> dict[str, str]:
    """学校名列表 → {wikipedia_title: wikidata_qid}"""
    data = _get(
        "https://zh.wikipedia.org/w/api.php?action=query&prop=pageprops"
        "&ppprop=wikibase_item&format=json&formatversion=2"
        "&titles=" + requests.utils.quote("|".join(names))
    )
    if not data:
        return {}
    result: dict[str, str] = {}
    for page in data.get("query", {}).get("pages", []):
        qid = page.get("pageprops", {}).get("wikibase_item", "")
        if qid:
            result[page["title"]] = qid
    return result


def batch_get_claims(qids: list[str]) -> dict[str, dict]:
    """QID 列表 → {qid: {website, p527_qids}}"""
    data = _get(
        "https://www.wikidata.org/w/api.php?action=wbgetentities"
        "&props=claims&format=json"
        "&ids=" + "|".join(qids)
    )
    if not data:
        return {}
    result: dict[str, dict] = {}
    for qid, entity in data.get("entities", {}).items():
        claims = entity.get("claims", {})

        # P856 = 官方网站
        website = ""
        for c in claims.get("P856", []):
            try:
                website = c["mainsnak"]["datavalue"]["value"]
                break
            except (KeyError, TypeError):
                pass

        # P527 = hasPart（各学院 QID）
        p527_qids: list[str] = []
        for c in claims.get("P527", []):
            try:
                p527_qids.append(c["mainsnak"]["datavalue"]["value"]["id"])
            except (KeyError, TypeError):
                pass

        result[qid] = {"website": website, "p527_qids": p527_qids}
    return result


def batch_get_labels(qids: list[str]) -> dict[str, str]:
    """QID 列表 → {qid: 中文标签}（每次最多 50 个）"""
    if not qids:
        return {}
    data = _get(
        "https://www.wikidata.org/w/api.php?action=wbgetentities"
        "&props=labels&languages=zh&format=json"
        "&ids=" + "|".join(qids[:50])
    )
    if not data:
        return {}
    result: dict[str, str] = {}
    for qid, entity in data.get("entities", {}).items():
        label = entity.get("labels", {}).get("zh", {}).get("value", "")
        if label:
            result[qid] = label
    return result


# 匹配「XX学院」「XX系」「XX部」格式的学院名（不含通用词）
_DEPT_RE = re.compile(
    r"[一-鿿]{2,12}"
    r"(?:学院|学部|研究院|研究所|系|学校|中心)"
)
_SKIP_LABELS = {"大学", "职业技术学院", "学院", "研究院", "研究所", "系"}


def _get_with_retry(url: str, retries: int = 3) -> dict | None:
    """带指数退避重试的 GET（主要处理 429）。"""
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code == 429:
                wait = 3 * (2 ** attempt)
                print(f"  [429] 限速，等待 {wait}s…")
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt == retries - 1:
                print(f"  [HTTP] {e}")
    return None


# 明确指向"当前院系设置"的段落标题关键词（严格匹配）
_DEPT_SECTION_KWS = ["院系设置", "学院设置", "院系组成", "院系专业", "院系与专业", "主要院系", "开设院系"]
# 放宽的备用关键词（排除含"历史"的段落）
_DEPT_SECTION_LOOSE = ["院系", "学科", "专业设置"]
_EXCLUDE_SECTION_KWS = ["历史", "沿革", "发展", "成立", "合并", "改名", "前身"]


def fetch_dept_from_wiki(school_name: str) -> list[str]:
    """从 Wikipedia 院系段落解析院系名（P527 无数据时的备用）。"""
    time.sleep(1.0)   # 避免触发 429
    data = _get_with_retry(
        f"https://zh.wikipedia.org/w/api.php?action=parse"
        f"&page={requests.utils.quote(school_name)}"
        "&prop=sections&format=json"
    )
    if not data:
        return []

    sections = data.get("parse", {}).get("sections", [])

    # 优先找精确匹配的院系段落
    target = next(
        (s for s in sections if any(k in s.get("line", "") for k in _DEPT_SECTION_KWS)),
        None,
    )
    # 备用：宽松匹配但排除历史段落
    if not target:
        target = next(
            (
                s for s in sections
                if any(k in s.get("line", "") for k in _DEPT_SECTION_LOOSE)
                and not any(ex in s.get("line", "") for ex in _EXCLUDE_SECTION_KWS)
            ),
            None,
        )
    if not target:
        return []

    time.sleep(0.8)
    data2 = _get_with_retry(
        f"https://zh.wikipedia.org/w/api.php?action=parse"
        f"&page={requests.utils.quote(school_name)}"
        f"&prop=wikitext&section={target['index']}&format=json"
    )
    if not data2:
        return []

    wikitext = data2.get("parse", {}).get("wikitext", {}).get("*", "")

    # 只提取 [[链接]] 中明确的学院/系名（更可靠）
    linked = re.findall(r"\[\[(?:[^\]|]*\|)?([^\]]+(?:学院|学部|研究院|系))\]\]", wikitext)

    candidates: list[str] = []
    seen: set[str] = set()
    for name in linked:
        name = name.strip()
        short = name[len(school_name):] if name.startswith(school_name) else name
        if (short and len(short) >= 3 and short not in seen
                and short not in _SKIP_LABELS
                and not any(ex in short for ex in ["大学", "高校", "旧"])):
            seen.add(short)
            candidates.append(short)

    return candidates[:MAX_MAJORS]


# 学院/系名常见前缀（去掉"北京大学"/"清华大学"等前缀）
_SCHOOL_PREFIX_RE = re.compile(r"^[一-龥]{2,8}(?:大学|学院|大專|高校)")

def strip_school_prefix(name: str, school_name: str) -> str:
    """'北京大学数学科学学院' → '数学科学学院'"""
    if name.startswith(school_name):
        return name[len(school_name):]
    # 通用: 去掉开头的学校名部分（最多 8 个汉字+大学/学院）
    m = _SCHOOL_PREFIX_RE.match(name)
    if m and m.end() < len(name):
        return name[m.end():]
    return name


def resolve_p527_to_names(p527_qids: list[str], school_name: str) -> list[str]:
    """将 P527 QID 列表解析为中文学院名（已去掉学校名前缀）。"""
    if not p527_qids:
        return []
    labels = batch_get_labels(p527_qids)
    names: list[str] = []
    for qid in p527_qids[:MAX_MAJORS]:
        label = labels.get(qid, "")
        if label:
            short = strip_school_prefix(label, school_name)
            if short and len(short) >= 2:
                names.append(short)
    return names[:MAX_MAJORS]


def run(dry_run: bool, all_schools: bool, limit: int | None) -> None:
    db = SessionLocal()

    stmt = select(School).order_by(School.id)
    if not all_schools:
        stmt = stmt.where(
            or_(School.website.is_(None), School.popular_majors.is_(None))
        )
    if limit:
        stmt = stmt.limit(limit)

    schools = db.scalars(stmt).all()
    total = len(schools)
    if total == 0:
        print("✓ 无待处理学校")
        db.close()
        return

    mode_tag = "(dry-run)" if dry_run else ""
    print(f"待处理: {total} 所 {mode_tag}")
    print("-" * 72)

    web_updated = maj_updated = not_found = 0

    for batch_start in range(0, total, BATCH):
        batch = schools[batch_start: batch_start + BATCH]
        batch_num = batch_start // BATCH + 1
        total_batches = (total + BATCH - 1) // BATCH
        print(f"\n[批次 {batch_num}/{total_batches}] {len(batch)} 所学校…")

        # ── Step1: Wikipedia → QID ──
        name_to_qid = batch_get_qids([s.name for s in batch])
        time.sleep(0.6)

        if not name_to_qid:
            print("  [!] Wikipedia 批次失败，跳过")
            not_found += len(batch)
            time.sleep(DELAY)
            continue

        # ── Step2: Wikidata claims (P856 + P527) ──
        qid_to_claims = batch_get_claims(list(name_to_qid.values()))
        time.sleep(0.6)

        # ── Step3: 收集所有 P527 QID 一次性查标签 ──
        all_p527: list[str] = []
        for claims in qid_to_claims.values():
            all_p527.extend(claims.get("p527_qids", []))
        p527_labels: dict[str, str] = {}
        if all_p527:
            p527_labels = batch_get_labels(list(dict.fromkeys(all_p527)))
            time.sleep(0.3)

        # ── Step4: 写入 ──
        for school in batch:
            qid = name_to_qid.get(school.name, "")
            if not qid:
                print(f"  - {school.name:<28} (无维基条目)")
                not_found += 1
                continue

            claims = qid_to_claims.get(qid, {})
            website = claims.get("website", "")
            p527_qids = claims.get("p527_qids", [])

            # 从已获取的标签里解析院系名（优先 P527，备用 Wikipedia 段落）
            majors: list[str] = []
            for pqid in p527_qids[:MAX_MAJORS]:
                label = p527_labels.get(pqid, "")
                if label:
                    short = strip_school_prefix(label, school.name)
                    if short and len(short) >= 2:
                        majors.append(short)

            updates: dict[str, object] = {}
            if website and (all_schools or school.website is None):
                updates["website"] = website
                web_updated += 1
            if majors and (all_schools or school.popular_majors is None):
                updates["popular_majors"] = majors
                maj_updated += 1

            if updates:
                tag = "[dry]" if dry_run else "✓"
                web_str = updates.get("website", school.website or "-")
                maj_str = ",".join(majors[:3]) + ("…" if len(majors) > 3 else "") if majors else "-"
                print(f"  {tag} {school.name:<26} 官网:{str(web_str)[:35]}  院系:{maj_str}")
                if not dry_run:
                    db.execute(update(School).where(School.id == school.id).values(**updates))
            else:
                print(f"  - {school.name:<28} (无新字段)")
                not_found += 1

        if not dry_run and (batch_start // BATCH) % 5 == 4:
            db.commit()

        time.sleep(DELAY)

    if not dry_run:
        db.commit()
    db.close()

    print()
    print("=" * 72)
    print(f"完成: 官网 {web_updated} 个 | 院系 {maj_updated} 个 | 无数据 {not_found} 个 | 共 {total} 所")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    run(dry_run=args.dry_run, all_schools=args.__dict__["all"], limit=args.limit)
