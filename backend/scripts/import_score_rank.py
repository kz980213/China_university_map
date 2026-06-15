"""导入一分一段数据。

来源：yifenyiduan/*.json（108 个文件，30 省 × 2024/2025，部分省有 2023）

字段映射：
  province_name → province_id（经 provinces 表归一化）
  track_cn      → track（规范化，见 TRACK_NORMALIZE 映射）
  rows[i].score → score
  rows[i].count → count
  rows[i].cumulative → cumulative_rank（直接映射，绝不重算）

track_cn 规范化规则：
  物理类         → 物理类（标准 3+1+2）
  历史类         → 历史类
  理科           → 理科（旧制）
  文科           → 文科（旧制）
  综合改革       → 综合改革（3+3）
  "" + combined  → 综合改革（北京 3 个文件 fallback）
  物理等科目类   → 物理类（江苏 2025 官方用语，归一化保证与 get_province_tracks() 一致）

前置检查：provinces 表 ≥ 31 行（否则中止，需先跑 seed_provinces.py）。
幂等：ON CONFLICT (uq_score_rank_entry) DO NOTHING。
批次标记：import_batch = "eol_yfyd_{YYYYMMDD}"

运行（在 backend/ 目录下）：
  python scripts/import_score_rank.py
"""

import sys
import os
import json
import glob
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.database import SessionLocal
from app.models.province import Province
from app.models.score_rank import ScoreRankEntry

YFYD_DIR = r"D:\AI_DS\gaokao-pro\cli\data\yifenyiduan"
BATCH_SIZE = 500

# track_cn → 统一存储值
TRACK_NORMALIZE: dict[str, str] = {
    "物理类": "物理类",
    "历史类": "历史类",
    "理科": "理科",
    "文科": "文科",
    "综合改革": "综合改革",
    "物理等科目类": "物理类",   # 江苏 2025 官方用语归一化
}


def _normalize_track(track_cn: str, track_en: str) -> str | None:
    if not track_cn and track_en == "combined":
        return "综合改革"
    return TRACK_NORMALIZE.get(track_cn)


def import_score_rank() -> None:
    db = SessionLocal()
    try:
        # ── 前置检查 ─────────────────────────────────────────────────────────
        prov_count = db.scalar(select(func.count()).select_from(Province))
        if (prov_count or 0) < 31:
            raise SystemExit(
                f"✗ provinces 表只有 {prov_count} 行（需 ≥31）。"
                "请先运行 python scripts/seed_provinces.py"
            )

        # ── 预加载省份字典 ───────────────────────────────────────────────────
        provinces = {p.name: p.id for p in db.scalars(select(Province)).all()}
        # 扩充别名：name_full（如"安徽省" → 安徽 id）
        for p in db.scalars(select(Province)).all():
            provinces.setdefault(p.name_full, p.id)

        batch_id = f"eol_yfyd_{date.today().strftime('%Y%m%d')}"
        now = datetime.utcnow()

        files = sorted(
            f for f in glob.glob(os.path.join(YFYD_DIR, "*.json"))
            if not os.path.basename(f).startswith("_")
        )
        print(f"文件数: {len(files)}")

        total_rows = 0
        warn_prov: list[str] = []
        warn_track: list[str] = []

        for fpath in files:
            fname = os.path.basename(fpath)
            with open(fpath, encoding="utf-8") as f:
                data = json.load(f)

            prov_name: str = data.get("province_name", "")
            province_id = provinces.get(prov_name)
            if province_id is None:
                warn_prov.append(f"{fname}: province_name={prov_name!r}")
                continue

            track_cn: str = data.get("track_cn", "")
            track_en: str = data.get("track", "")
            track = _normalize_track(track_cn, track_en)
            if track is None:
                warn_track.append(f"{fname}: track_cn={track_cn!r}")
                continue

            year: int = data["year"]
            rows_data: list[dict] = data.get("rows", [])

            # 分批插入
            for i in range(0, len(rows_data), BATCH_SIZE):
                batch = [
                    {
                        "province_id": province_id,
                        "year": year,
                        "track": track,
                        "score": r["score"],
                        "count": r["count"],
                        "cumulative_rank": r["cumulative"],  # 直接映射，不重算
                        "import_batch": batch_id,
                    }
                    for r in rows_data[i : i + BATCH_SIZE]
                ]
                stmt = pg_insert(ScoreRankEntry).values(batch)
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=["province_id", "year", "track", "score"]
                )
                db.execute(stmt)

            total_rows += len(rows_data)

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    print(f"✓ 一分一段导入完成: {total_rows} 行（来自 {len(files)} 个文件）")
    print(f"  import_batch: {batch_id}")
    if warn_prov:
        print(f"  ⚠ 省份未命中（跳过）: {warn_prov}")
    if warn_track:
        print(f"  ⚠ track 未知（跳过）: {warn_track}")


if __name__ == "__main__":
    import_score_rank()
