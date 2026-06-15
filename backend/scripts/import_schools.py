"""导入院校数据。

来源：
  主：all_universities.json（教育部高校名录，2919 条）
  辅：school-index.json.gz（gaokao.cn 院校索引，补全 school_type / is_985 / is_211 / is_dfc）

运行（在 backend/ 目录下）：
  python scripts/import_schools.py

匹配逻辑：学校标识码[-5:] == zs_code
幂等：ON CONFLICT (school_code) DO UPDATE
"""

import sys
import os
import json
import gzip
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.database import SessionLocal
from app.models.school import School

# ── 数据文件路径 ──────────────────────────────────────────────────────────────
DATA_UNIVERSITIES = r"D:\AI_DS\gaoxiao\gaokao-universities-data\universities\all_universities.json"
DATA_SCHOOL_INDEX = r"D:\AI_DS\gaokao-pro\cli\data\school-index.json.gz"
BATCH_SIZE = 500


def _map_ownership(bei_zhu: str) -> str:
    if not bei_zhu:
        return "公办"
    if bei_zhu == "民办":
        return "民办"
    if "中外合作" in bei_zhu:
        return "中外合作"
    return "境外"


def _load_school_index(path: str) -> dict[str, dict]:
    with gzip.open(path) as f:
        data = json.loads(f.read().decode("utf-8"))
    # zs_code → row；若有重复 zs_code 取最后一条（极少数分校情况）
    return {row["zs_code"]: row for row in data["rows"]}


def import_schools() -> None:
    print("读取数据文件…")
    with open(DATA_UNIVERSITIES, encoding="utf-8") as f:
        unis = json.load(f)
    idx = _load_school_index(DATA_SCHOOL_INDEX)

    now = datetime.utcnow()
    records: list[dict] = []
    attr_matched = attr_unmatched = 0

    for u in unis:
        zs_code = u["学校标识码"][-5:]
        idx_row = idx.get(zs_code)

        if idx_row:
            school_type = idx_row.get("type") or "综合类"
            is_985 = bool(idx_row.get("f985"))
            is_211 = bool(idx_row.get("f211"))
            is_dfc = idx_row.get("dual_class") == "双一流"
            attr_matched += 1
        else:
            school_type = "综合类"
            is_985 = is_211 = is_dfc = False
            attr_unmatched += 1

        records.append({
            "name": u["学校名称"],
            "school_code": u["学校标识码"],
            "province": u["省份"],
            "city": u["所在地"],
            "level": u["办学层次"],
            "school_type": school_type,
            "ownership": _map_ownership(u.get("备注", "")),
            "is_985": is_985,
            "is_211": is_211,
            "is_double_first_class": is_dfc,
            "created_at": now,
            "updated_at": now,
        })

    db = SessionLocal()
    try:
        for i in range(0, len(records), BATCH_SIZE):
            batch = records[i : i + BATCH_SIZE]
            stmt = pg_insert(School).values(batch)
            stmt = stmt.on_conflict_do_update(
                index_elements=["school_code"],
                set_={
                    "name": stmt.excluded.name,
                    "province": stmt.excluded.province,
                    "city": stmt.excluded.city,
                    "level": stmt.excluded.level,
                    "school_type": stmt.excluded.school_type,
                    "ownership": stmt.excluded.ownership,
                    "is_985": stmt.excluded.is_985,
                    "is_211": stmt.excluded.is_211,
                    "is_double_first_class": stmt.excluded.is_double_first_class,
                    "updated_at": stmt.excluded.updated_at,
                },
            )
            db.execute(stmt)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    total = len(records)
    print(f"✓ 院校导入完成: {total} 行")
    print(f"  school-index 属性补全: {attr_matched}/{total} ({attr_matched/total*100:.1f}%)")
    print(f"  未从 school-index 补全（仅名录信息）: {attr_unmatched}")


if __name__ == "__main__":
    import_schools()
