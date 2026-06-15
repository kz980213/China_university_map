"""
从 gaokao-universities-data/mcp_results/ 命名批次 JSON 导入百科数据到 schools 表。

映射：
  官网        → schools.website
  双一流学科    → schools.popular_majors (拆分为列表)
  A+学科/Aplus学科 → 如果 popular_majors 为空则使用此字段

匹配方式：优先 school_code，次选 name。

运行：
  cd backend
  python scripts/import_baike_data.py --dry-run
  python scripts/import_baike_data.py
  python scripts/import_baike_data.py --all   # 覆盖已有值
"""

import argparse
import io
import json
import os
import re
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import SessionLocal
from app.models.school import School
from sqlalchemy import select, update

BAIKE_DIR = r"D:\AI_DS\gaoxiao\gaokao-universities-data\mcp_results"
SPLIT_RE = re.compile(r"[/\\、，,；;]+")


def is_empty(val: str) -> bool:
    return not val or val.strip() in {"未提及", "暂无", "无", "-", "N/A", ""}


_COUNT_RE = re.compile(r"^\d+个|^[一二三四五六七八九十百]+个|个学科$|个一级")
_IGNORE_PARTS = {"学科", "一级", "博士点", "硕士点", "入选", "等", "工程"}


def parse_majors(raw: str) -> list[str]:
    """'哲学/数学/化学/...' → ['哲学', '数学', '化学', ...]"""
    if is_empty(raw):
        return []
    # 去掉括号内补充说明
    raw = re.sub(r"（[^）]*）|\([^)]*\)", "", raw)
    parts = [p.strip() for p in SPLIT_RE.split(raw) if p.strip()]
    result = []
    for p in parts:
        if _COUNT_RE.search(p):          # 跳过"5个""三个"等计数词
            continue
        if p in _IGNORE_PARTS:           # 跳过无意义单词
            continue
        if not (2 <= len(p) <= 18):      # 长度过滤
            continue
        if re.search(r"\d", p):          # 含数字的通常不是学科名
            continue
        result.append(p)
    return result[:15]


def load_named_batches(baike_dir: str) -> dict[str, dict]:
    """读取所有命名批次文件，返回 {school_code_or_name: data} 字典。"""
    records: dict[str, dict] = {}   # key = code (优先) or name
    skipped_files = 0

    for fname in sorted(os.listdir(baike_dir)):
        if not fname.endswith(".json"):
            continue
        # 跳过编号批次（batch_0001 ~ batch_0292），它们全是"未提及"
        if re.match(r"batch_\d{4}\.json$", fname):
            continue

        fpath = os.path.join(baike_dir, fname)
        try:
            with open(fpath, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"  [skip] {fname}: {e}")
            skipped_files += 1
            continue

        # 支持两种格式：
        # 格式A: 直接数组 [{name, code, 官网, ...}, ...]
        # 格式B: {batch, schools:[...], result:[...]}
        items = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            result = data.get("result", [])
            schools = data.get("schools", [])
            if result and isinstance(result, list) and isinstance(result[0], dict):
                # 把 schools 的 code 合并进 result
                code_map = {s["name"]: s.get("code", "") for s in schools}
                for r in result:
                    name = r.get("学校名称", r.get("name", ""))
                    if name and name not in r:
                        r["name"] = name
                    if "code" not in r and name in code_map:
                        r["code"] = code_map[name]
                items = result

        for item in items:
            name = item.get("name") or item.get("学校名称", "")
            code = item.get("code", "")
            website_raw = item.get("官网", "")
            dfc_raw = item.get("双一流学科") or item.get("双一流", "")
            aplus_raw = (item.get("A+学科") or item.get("Aplus学科")
                         or item.get("Aplus") or "")

            # 过滤无用条目（全"未提及"）
            if is_empty(website_raw) and is_empty(dfc_raw) and is_empty(aplus_raw):
                continue

            website = website_raw.strip() if not is_empty(website_raw) else ""
            majors = parse_majors(dfc_raw) or parse_majors(aplus_raw)

            key = code if code else name
            if key:
                # 同一学校可能出现在多个批次，保留有更多信息的版本
                existing = records.get(key, {})
                if (website or majors) and (
                    not existing
                    or (website and not existing.get("website"))
                    or (majors and not existing.get("majors"))
                ):
                    records[key] = {"name": name, "code": code,
                                    "website": website, "majors": majors}

    if skipped_files:
        print(f"[!] 跳过 {skipped_files} 个损坏文件")
    return records


def run(dry_run: bool, all_schools: bool) -> None:
    print("读取百科数据文件…")
    records = load_named_batches(BAIKE_DIR)
    print(f"共解析到 {len(records)} 条有效记录（有官网或有学科）")

    db = SessionLocal()
    schools = db.scalars(select(School)).all()

    # 建立两个索引：code → school, name → school
    by_code: dict[str, School] = {s.school_code: s for s in schools}
    by_name: dict[str, School] = {s.name: s for s in schools}

    web_updated = maj_updated = not_found = already_ok = 0

    for key, rec in records.items():
        # 匹配 DB 中的学校
        school = by_code.get(rec["code"]) or by_name.get(rec["name"])
        if not school:
            not_found += 1
            continue

        updates: dict[str, object] = {}

        if rec["website"] and (all_schools or school.website is None):
            updates["website"] = rec["website"]
            web_updated += 1

        if rec["majors"] and (all_schools or school.popular_majors is None):
            updates["popular_majors"] = rec["majors"]
            maj_updated += 1

        if updates:
            tag = "[dry]" if dry_run else "✓"
            web_str = updates.get("website", "")
            maj_str = ",".join(rec["majors"][:3]) + "…" if rec["majors"] else ""
            print(f"  {tag} {school.name:<28} "
                  f"{'官网:' + str(web_str)[:30] if web_str else ''}"
                  f"{'  院系:' + maj_str if maj_str else ''}")
            if not dry_run:
                db.execute(update(School).where(School.id == school.id).values(**updates))
        else:
            already_ok += 1

    if not dry_run:
        db.commit()
    db.close()

    print()
    print("=" * 72)
    print(f"官网更新: {web_updated}  |  学科更新: {maj_updated}  "
          f"|  无需更新: {already_ok}  |  未匹配: {not_found}")
    print(f"（共处理 {len(records)} 条记录）")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--all", action="store_true", help="覆盖已有值")
    args = parser.parse_args()
    run(dry_run=args.dry_run, all_schools=args.__dict__["all"])
