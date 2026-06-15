"""导入专业目录数据。

来源：all_majors.json（教育部本科专业目录，821 条）

字段映射：
  id       → id（保留源稳定 id，显式指定）
  门类     → discipline（12 个大类，如"工学"）
  专业类   → category（93 个中类，如"计算机类"）
  专业名称 → name
  code     → ""（占位，专业代码待专业线阶段从分数线数据回填）
  degree   → "学士"（教育部本科目录，全部本科学位）
  duration → "4年"（默认学制）

运行（在 backend/ 目录下）：
  python scripts/import_majors.py

幂等：ON CONFLICT (id) DO UPDATE
导入后自动 reset PostgreSQL sequence（防止后续自增冲突）。
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.database import SessionLocal
from app.models.major import Major

DATA_MAJORS = r"D:\AI_DS\gaoxiao\gaokao-universities-data\majors\all_majors.json"
BATCH_SIZE = 500


def import_majors() -> None:
    print("读取专业目录…")
    with open(DATA_MAJORS, encoding="utf-8") as f:
        raw = json.load(f)

    now = datetime.utcnow()
    records: list[dict] = []

    for m in raw:
        records.append({
            "id": m["id"],
            "name": m["专业名称"],
            "code": "",                   # 占位，待专业线阶段回填
            "category": m["专业类"],      # 93 个中类
            "discipline": m["门类"],      # 12 个大类
            "degree": "学士",
            "duration": "4年",
            "created_at": now,
            "updated_at": now,
        })

    db = SessionLocal()
    try:
        for i in range(0, len(records), BATCH_SIZE):
            batch = records[i : i + BATCH_SIZE]
            stmt = pg_insert(Major).values(batch)
            stmt = stmt.on_conflict_do_update(
                index_elements=["id"],
                set_={
                    "name": stmt.excluded.name,
                    "category": stmt.excluded.category,
                    "discipline": stmt.excluded.discipline,
                    "degree": stmt.excluded.degree,
                    "duration": stmt.excluded.duration,
                    "updated_at": stmt.excluded.updated_at,
                },
            )
            db.execute(stmt)

        # reset sequence，防止后续 ORM 自增 id 与已有行冲突
        db.execute(text("SELECT setval('majors_id_seq', (SELECT MAX(id) FROM majors))"))
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    print(f"✓ 专业目录导入完成: {len(records)} 行")
    print("  code 字段已留空（待专业线阶段回填）")


if __name__ == "__main__":
    import_majors()
