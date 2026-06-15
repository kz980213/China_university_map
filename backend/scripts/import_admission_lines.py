"""导入院校录取最低分（院校线）。

来源：school-index.json.gz 的 pro_type_min 字段
年份：导入所有可用年份（含 2023/2024/2025），约 240,161 行。

院校匹配：
  school-index.zs_code（5 位部标码） == schools.school_code[-5:]
  命中 → school_id=matched_id, match_status="matched"
  未命中 → school_id=None, match_status="unmatched",
            raw_school_name/raw_school_code 保留原始信息

省份解析：
  pro_type_min 键为 2 位 GB 省代码（"11"→北京）
  经 province_service.get_province() 解析（已支持 2 位前缀查询）

类型码 → subject_type：
  "1"    → 理科
  "2"    → 文科
  "3"    → 综合改革
  "2073" → 物理类
  "2074" → 历史类

CHECK 约束合规：
  is_school_level=True，所有专业级字段（major_id/major_name/
  raw_major_name/raw_major_code/score_subject_req）均为 None。

batch 字段：
  NULL——源数据不含批次信息，不推测。

前置检查：provinces ≥ 31，schools ≥ 2000。

幂等：
  matched 行  → ON CONFLICT (school_id, year, student_province, subject_type)
                 WHERE school_id IS NOT NULL AND is_school_level
                 DO UPDATE SET min_score, import_batch, updated_at
  unmatched 行 → ON CONFLICT (raw_school_code, year, student_province, subject_type)
                 WHERE school_id IS NULL AND is_school_level
                 DO UPDATE SET min_score, import_batch, updated_at

已知跳过记录（2026-06-12 排查确认）：
  类型码 32/33 出现在内蒙古（prov_key=15）下部分学校的 2023 年 type 字段，
  经排查认定为"蒙授文科/蒙授理科"（蒙古语授课特殊招生类别）。
  科类体系和分数与普通高考不可比，补进主数据会污染查询/推荐，不予导入。
  跳过详情（共 6 校，均在 student_province=内蒙古、year=2023）：
    内蒙古建筑职业技术大学 — type=['32','33'], 跳过原因:蒙授特殊类别无标准科类码不补
    新疆农业大学             — type=['32','33'], 跳过原因:蒙授特殊类别无标准科类码不补
    新疆师范大学             — type=['32','33'], 跳过原因:蒙授特殊类别无标准科类码不补
    新疆财经大学             — type=['33'],      跳过原因:蒙授特殊类别无标准科类码不补
    青海大学                 — type=['32','33'], 跳过原因:蒙授特殊类别无标准科类码不补
    青海师范大学             — type=['32','33'], 跳过原因:蒙授特殊类别无标准科类码不补
  以上 6 条不补，可追溯，其余 80 校同记录内另有合法科类码正常导入。

运行（在 backend/ 目录下）：
  python scripts/import_admission_lines.py
"""

import sys
import os
import json
import gzip
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, func, text
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.database import SessionLocal
from app.models.province import Province
from app.models.school import School
from app.models.admission import AdmissionScore

DATA_SCHOOL_INDEX = r"D:\AI_DS\gaokao-pro\cli\data\school-index.json.gz"
BATCH_SIZE = 500

TRACK_CODE_MAP: dict[str, str] = {
    "1": "理科",
    "2": "文科",
    "3": "综合改革",
    "2073": "物理类",
    "2074": "历史类",
}


def import_admission_lines() -> None:
    print("读取 school-index.json.gz…")
    with gzip.open(DATA_SCHOOL_INDEX) as f:
        idx_data = json.loads(f.read().decode("utf-8"))
    idx_rows = idx_data["rows"]

    db = SessionLocal()
    try:
        # ── 前置检查 ─────────────────────────────────────────────────────────
        prov_count = db.scalar(select(func.count()).select_from(Province))
        school_count = db.scalar(select(func.count()).select_from(School))
        if (prov_count or 0) < 31:
            raise SystemExit(
                f"✗ provinces 表只有 {prov_count} 行。请先运行 seed_provinces.py"
            )
        if (school_count or 0) < 2000:
            raise SystemExit(
                f"✗ schools 表只有 {school_count} 行。请先运行 import_schools.py"
            )

        # ── 预加载字典 ───────────────────────────────────────────────────────
        # provinces: 2 位省代码 → (province.id, province.name)
        province_map: dict[str, tuple[int, str]] = {}
        for p in db.scalars(select(Province)).all():
            province_map[p.code[:2]] = (p.id, p.name)

        # schools: zs_code → school_id
        school_map: dict[str, int] = {}
        for s in db.scalars(select(School)).all():
            school_map[s.school_code[-5:]] = s.id

        batch_id = f"gaokao_cn_{date.today().strftime('%Y%m%d')}"
        now = datetime.utcnow()

        total = matched_cnt = unmatched_cnt = 0
        warn_prov: list[str] = []
        warn_type: list[str] = []

        matched_buf: list[dict] = []
        unmatched_buf: list[dict] = []

        def _flush(buf: list[dict], is_matched: bool) -> None:
            if not buf:
                return
            # 去重（源数据同一学校同省同年同科可能出现多次）
            if is_matched:
                key = lambda r: (r["school_id"], r["year"], r["student_province"], r["subject_type"])
            else:
                key = lambda r: (r["raw_school_code"], r["year"], r["student_province"], r["subject_type"])
            seen: set[tuple] = set()
            deduped: list[dict] = []
            for row in buf:
                k = key(row)
                if k not in seen:
                    seen.add(k)
                    deduped.append(row)
            if not deduped:
                buf.clear()
                return
            stmt = pg_insert(AdmissionScore).values(deduped)
            if is_matched:
                stmt = stmt.on_conflict_do_update(
                    index_elements=["school_id", "year", "student_province", "subject_type"],
                    index_where=text("school_id IS NOT NULL AND is_school_level"),
                    set_={
                        "min_score": stmt.excluded.min_score,
                        "import_batch": stmt.excluded.import_batch,
                        "updated_at": stmt.excluded.updated_at,
                    },
                )
            else:
                stmt = stmt.on_conflict_do_update(
                    index_elements=["raw_school_code", "year", "student_province", "subject_type"],
                    index_where=text("school_id IS NULL AND is_school_level"),
                    set_={
                        "min_score": stmt.excluded.min_score,
                        "import_batch": stmt.excluded.import_batch,
                        "updated_at": stmt.excluded.updated_at,
                    },
                )
            db.execute(stmt)
            buf.clear()

        for idx_row in idx_rows:
            zs_code: str = idx_row.get("zs_code", "")
            school_name: str = idx_row.get("name", "")
            matched_id = school_map.get(zs_code) if zs_code else None
            is_matched = matched_id is not None

            for prov_id_str, entries in idx_row.get("pro_type_min", {}).items():
                prov_info = province_map.get(prov_id_str)
                if prov_info is None:
                    warn_prov.append(prov_id_str)
                    continue
                province_db_id, province_name = prov_info

                for entry in entries:
                    year: int = entry["year"]
                    for type_code, score_str in entry["type"].items():
                        subject_type = TRACK_CODE_MAP.get(type_code)
                        if subject_type is None:
                            warn_type.append(type_code)
                            continue

                        row: dict = {
                            "school_id": matched_id,
                            "major_id": None,
                            "year": year,
                            "student_province": province_name,
                            "subject_type": subject_type,
                            "batch": None,          # 源数据无批次信息
                            "major_name": None,
                            "min_score": int(score_str),
                            "min_rank": None,
                            "is_school_level": True,
                            "match_status": "matched" if is_matched else "unmatched",
                            "raw_school_name": None if is_matched else school_name,
                            "raw_school_code": None if is_matched else zs_code,
                            # 专业级字段全部 None → 满足 CHECK 约束
                            "raw_major_name": None,
                            "raw_major_code": None,
                            "score_subject_req": None,
                            "import_batch": batch_id,
                            "created_at": now,
                            "updated_at": now,
                        }

                        total += 1
                        if is_matched:
                            matched_cnt += 1
                            matched_buf.append(row)
                            if len(matched_buf) >= BATCH_SIZE:
                                _flush(matched_buf, True)
                        else:
                            unmatched_cnt += 1
                            unmatched_buf.append(row)
                            if len(unmatched_buf) >= BATCH_SIZE:
                                _flush(unmatched_buf, False)

        # 刷尾批
        _flush(matched_buf, True)
        _flush(unmatched_buf, False)

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    match_rate = matched_cnt / total * 100 if total else 0
    print(f"✓ 院校线导入完成: {total} 行")
    print(f"  matched   : {matched_cnt} ({match_rate:.1f}%)")
    print(f"  unmatched : {unmatched_cnt} ({100-match_rate:.1f}%) — school_id=NULL, 见 raw_school_name/code")
    print(f"  import_batch: {batch_id}")
    if warn_prov:
        print(f"  ⚠ 未知省份代码（跳过）: {sorted(set(warn_prov))}")
    if warn_type:
        print(f"  ⚠ 未知科类码（跳过）: {sorted(set(warn_type))}")


if __name__ == "__main__":
    import_admission_lines()
