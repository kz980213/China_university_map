"""
从百度百科爬取高校官网、招生网址、主要院系（热门专业）。

目标字段：
  school.website          ← 百科 infobox「官方网站」
  school.admission_website ← 百科 infobox「招生网站 / 招生网址」
  school.popular_majors   ← 百科 infobox「主要院系 / 重点学科 / 特色专业 / 优势专业」

运行：
  cd backend
  python scripts/scrape_baike.py                   # 只处理三个字段均为空的学校
  python scripts/scrape_baike.py --all             # 所有学校（覆盖已有值）
  python scripts/scrape_baike.py --dry-run         # 不写库，只打印
  python scripts/scrape_baike.py --limit 50        # 限制处理数量（测试用）
  python scripts/scrape_baike.py --start-id 1000   # 从指定 id 开始
"""

import argparse
import io
import json
import os
import re
import sys
import time
import random
from urllib.parse import quote

# Windows GBK 终端下强制 UTF-8 输出
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import requests
from bs4 import BeautifulSoup
from sqlalchemy import select, update, or_

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import SessionLocal
from app.models.school import School

# ── 配置 ────────────────────────────────────────────────────────────────────
BASE_URL = "https://baike.baidu.com/item/{name}"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xhtml+xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://baike.baidu.com/",
}
REQUEST_INTERVAL = (1.5, 3.0)   # 随机延迟区间（秒）
SESSION_RESET_EVERY = 80        # 每处理 N 条重建 requests.Session（绕过 cookie 积累）

# ── infobox 字段映射 ────────────────────────────────────────────────────────
WEBSITE_KEYS = {"官方网站", "学校网站", "院校网址", "网址", "官网", "院校网站"}
ADMISSION_KEYS = {"招生网站", "招生网址", "招生信息网", "招生信息", "报考地址", "招生办公室网站"}
MAJORS_KEYS = {
    "主要院系", "院系专业", "重点学科", "特色专业", "优势专业",
    "主要专业", "知名专业", "院校专业", "学科专业",
}

SPLIT_RE = re.compile(r"[、，,；;/\\|]+")


def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update(HEADERS)
    return s


def fetch_baike(name: str, session: requests.Session) -> BeautifulSoup | None:
    url = BASE_URL.format(name=quote(name))
    try:
        r = session.get(url, timeout=12, allow_redirects=True)
        if r.status_code != 200:
            return None
        return BeautifulSoup(r.content, "lxml")
    except Exception as e:
        print(f"    ↳ 网络错误: {e}")
        return None


def extract_infobox(soup: BeautifulSoup) -> dict[str, str]:
    """解析 basicInfo infobox，返回 {字段名: 文本值} 字典。"""
    result: dict[str, str] = {}

    # 百度百科 infobox 结构：dt.basicInfo-item.name / dd.basicInfo-item.value
    names = soup.select("dt.basicInfo-item.name")
    for dt in names:
        key = dt.get_text(strip=True)
        dd = dt.find_next_sibling("dd")
        if dd:
            # 优先取 <a> 链接 href（网址字段）
            links = dd.find_all("a", href=True)
            href_val = ""
            for a in links:
                href = a["href"]
                # 过滤内部百科链接（/item/... 或 #...）
                if href.startswith("//") or href.startswith("http"):
                    href_val = href.lstrip("/")
                    if not href_val.startswith("http"):
                        href_val = "https://" + href_val
                    break
            text_val = dd.get_text(" ", strip=True)
            result[key] = href_val or text_val
    return result


def parse_school_info(soup: BeautifulSoup) -> dict:
    """从解析好的 soup 提取目标字段。"""
    info = extract_infobox(soup)

    website = ""
    admission = ""
    majors: list[str] = []

    for k, v in info.items():
        if k in WEBSITE_KEYS and not website:
            website = v.strip()
        if k in ADMISSION_KEYS and not admission:
            admission = v.strip()
        if k in MAJORS_KEYS and not majors:
            raw = v.strip()
            parts = [p.strip() for p in SPLIT_RE.split(raw) if p.strip()]
            if parts:
                majors = parts[:12]   # 最多保留 12 个

    return {"website": website, "admission_website": admission, "popular_majors": majors or None}


def run(dry_run: bool, all_schools: bool, limit: int | None, start_id: int) -> None:
    db = SessionLocal()

    stmt = select(School).where(School.id >= start_id).order_by(School.id)
    if not all_schools:
        stmt = stmt.where(
            or_(
                School.website.is_(None),
                School.admission_website.is_(None),
                School.popular_majors.is_(None),
            )
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

    session = make_session()
    success = failed = skipped = 0
    changed_fields: dict[int, dict] = {}

    for i, school in enumerate(schools, 1):
        if i % SESSION_RESET_EVERY == 0:
            session = make_session()

        print(f"[{i}/{total}] {school.name}", end="  ", flush=True)
        soup = fetch_baike(school.name, session)
        delay = random.uniform(*REQUEST_INTERVAL)

        if soup is None:
            print("✗ 请求失败")
            failed += 1
            time.sleep(delay)
            continue

        # 检查是否是消歧义页（词条列表页而非实际词条）
        # 消歧义页通常没有 basicInfo-item
        if not soup.select("dt.basicInfo-item.name"):
            # 尝试加 "大学" 或 "学院" 等辅助词
            print("→ 消歧义，重试+学校名", end="  ", flush=True)
            time.sleep(0.5)
            soup2 = fetch_baike(school.name + " 学校", session)
            if soup2 and soup2.select("dt.basicInfo-item.name"):
                soup = soup2
            elif soup2 is None:
                print("✗ 重试失败")
                failed += 1
                time.sleep(delay)
                continue
            else:
                print("⚠ 未找到 infobox，跳过")
                skipped += 1
                time.sleep(delay)
                continue

        parsed = parse_school_info(soup)

        # 构造实际要写入的变化（不覆盖已有数据，除非 --all）
        updates: dict[str, object] = {}
        for field, val in parsed.items():
            if not val:
                continue
            current = getattr(school, field)
            if all_schools or current is None:
                updates[field] = val

        if updates:
            summary = []
            if "website" in updates:
                summary.append(f"官网={updates['website'][:40]}")
            if "admission_website" in updates:
                summary.append(f"招生={updates['admission_website'][:40]}")
            if "popular_majors" in updates:
                majors_list = updates["popular_majors"]
                summary.append(f"专业={','.join(majors_list[:4])}…")
            print("✓ " + " | ".join(summary))
            if not dry_run:
                db.execute(update(School).where(School.id == school.id).values(**updates))
                if i % 30 == 0:
                    db.commit()
            success += 1
        else:
            print("— 无新字段")
            skipped += 1

        time.sleep(delay)

    if not dry_run:
        db.commit()
    db.close()

    print()
    print("=" * 72)
    print(f"完成: {success} 更新 / {skipped} 跳过 / {failed} 失败，共 {total} 所")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="不写库")
    parser.add_argument("--all", action="store_true", help="覆盖已有值")
    parser.add_argument("--limit", type=int, default=None, help="最多处理 N 条")
    parser.add_argument("--start-id", type=int, default=1, help="从 school.id >= N 开始")
    args = parser.parse_args()
    run(
        dry_run=args.dry_run,
        all_schools=args.__dict__["all"],
        limit=args.limit,
        start_id=args.start_id,
    )
