"""省份维度表幂等 seed 脚本。

用法（在 backend/ 目录下）：
  python scripts/seed_provinces.py

数据说明：
  - 改革年份、满分、科类均为公开政策事实，不含任何分数/位次数据
  - 西藏、新疆均已启动 3+1+2 改革，首届新高考 2027 年（2024 级学生）
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.database import SessionLocal
from app.models.province import Province

# ---------------------------------------------------------------------------
# 省份元数据（31 个省级行政区，不含港澳）
# gaokao_reform_type: "3+3" | "3+1+2" | "old"
# valid_tracks: 新高考生效后的科类；旧制年份由 get_province_tracks() 动态返回 ["理科","文科"]
# ---------------------------------------------------------------------------
PROVINCES: list[dict] = [
    # ── 华北 ──────────────────────────────────────────────────────────────
    {
        "name": "北京", "name_full": "北京市", "pinyin": "beijing", "slug": "beijing",
        "code": "110000", "gaokao_reform_type": "3+3", "new_gaokao_first_year": 2020,
        "max_score": 750, "valid_tracks": ["综合改革"], "region": "华北",
    },
    {
        "name": "天津", "name_full": "天津市", "pinyin": "tianjin", "slug": "tianjin",
        "code": "120000", "gaokao_reform_type": "3+3", "new_gaokao_first_year": 2020,
        "max_score": 750, "valid_tracks": ["综合改革"], "region": "华北",
    },
    {
        "name": "河北", "name_full": "河北省", "pinyin": "hebei", "slug": "hebei",
        "code": "130000", "gaokao_reform_type": "3+1+2", "new_gaokao_first_year": 2021,
        "max_score": 750, "valid_tracks": ["物理类", "历史类"], "region": "华北",
    },
    {
        # 2025 年首届新高考
        "name": "山西", "name_full": "山西省", "pinyin": "shanxi", "slug": "shanxi",
        "code": "140000", "gaokao_reform_type": "3+1+2", "new_gaokao_first_year": 2025,
        "max_score": 750, "valid_tracks": ["物理类", "历史类"], "region": "华北",
    },
    {
        # 2025 年首届新高考
        "name": "内蒙古", "name_full": "内蒙古自治区", "pinyin": "neimenggu", "slug": "neimenggu",
        "code": "150000", "gaokao_reform_type": "3+1+2", "new_gaokao_first_year": 2025,
        "max_score": 750, "valid_tracks": ["物理类", "历史类"], "region": "华北",
    },
    # ── 东北 ──────────────────────────────────────────────────────────────
    {
        "name": "辽宁", "name_full": "辽宁省", "pinyin": "liaoning", "slug": "liaoning",
        "code": "210000", "gaokao_reform_type": "3+1+2", "new_gaokao_first_year": 2021,
        "max_score": 750, "valid_tracks": ["物理类", "历史类"], "region": "东北",
    },
    {
        "name": "吉林", "name_full": "吉林省", "pinyin": "jilin", "slug": "jilin",
        "code": "220000", "gaokao_reform_type": "3+1+2", "new_gaokao_first_year": 2024,
        "max_score": 750, "valid_tracks": ["物理类", "历史类"], "region": "东北",
    },
    {
        "name": "黑龙江", "name_full": "黑龙江省", "pinyin": "heilongjiang", "slug": "heilongjiang",
        "code": "230000", "gaokao_reform_type": "3+1+2", "new_gaokao_first_year": 2024,
        "max_score": 750, "valid_tracks": ["物理类", "历史类"], "region": "东北",
    },
    # ── 华东 ──────────────────────────────────────────────────────────────
    {
        # 首批改革 2017；满分 660（语数外各 150 + 3 选考各 70）
        "name": "上海", "name_full": "上海市", "pinyin": "shanghai", "slug": "shanghai",
        "code": "310000", "gaokao_reform_type": "3+3", "new_gaokao_first_year": 2017,
        "max_score": 660, "valid_tracks": ["综合改革"], "region": "华东",
    },
    {
        "name": "江苏", "name_full": "江苏省", "pinyin": "jiangsu", "slug": "jiangsu",
        "code": "320000", "gaokao_reform_type": "3+1+2", "new_gaokao_first_year": 2021,
        "max_score": 750, "valid_tracks": ["物理类", "历史类"], "region": "华东",
    },
    {
        # 首批改革 2017；满分 750（语数外各 150 + 3 选考各 100）
        "name": "浙江", "name_full": "浙江省", "pinyin": "zhejiang", "slug": "zhejiang",
        "code": "330000", "gaokao_reform_type": "3+3", "new_gaokao_first_year": 2017,
        "max_score": 750, "valid_tracks": ["综合改革"], "region": "华东",
    },
    {
        "name": "安徽", "name_full": "安徽省", "pinyin": "anhui", "slug": "anhui",
        "code": "340000", "gaokao_reform_type": "3+1+2", "new_gaokao_first_year": 2024,
        "max_score": 750, "valid_tracks": ["物理类", "历史类"], "region": "华东",
    },
    {
        "name": "福建", "name_full": "福建省", "pinyin": "fujian", "slug": "fujian",
        "code": "350000", "gaokao_reform_type": "3+1+2", "new_gaokao_first_year": 2021,
        "max_score": 750, "valid_tracks": ["物理类", "历史类"], "region": "华东",
    },
    {
        "name": "江西", "name_full": "江西省", "pinyin": "jiangxi", "slug": "jiangxi",
        "code": "360000", "gaokao_reform_type": "3+1+2", "new_gaokao_first_year": 2024,
        "max_score": 750, "valid_tracks": ["物理类", "历史类"], "region": "华东",
    },
    {
        # 3+3（6 选 3，无首选科目限制）
        "name": "山东", "name_full": "山东省", "pinyin": "shandong", "slug": "shandong",
        "code": "370000", "gaokao_reform_type": "3+3", "new_gaokao_first_year": 2020,
        "max_score": 750, "valid_tracks": ["综合改革"], "region": "华东",
    },
    # ── 华中 ──────────────────────────────────────────────────────────────
    {
        "name": "河南", "name_full": "河南省", "pinyin": "henan", "slug": "henan",
        "code": "410000", "gaokao_reform_type": "3+1+2", "new_gaokao_first_year": 2025,
        "max_score": 750, "valid_tracks": ["物理类", "历史类"], "region": "华中",
    },
    {
        "name": "湖北", "name_full": "湖北省", "pinyin": "hubei", "slug": "hubei",
        "code": "420000", "gaokao_reform_type": "3+1+2", "new_gaokao_first_year": 2021,
        "max_score": 750, "valid_tracks": ["物理类", "历史类"], "region": "华中",
    },
    {
        "name": "湖南", "name_full": "湖南省", "pinyin": "hunan", "slug": "hunan",
        "code": "430000", "gaokao_reform_type": "3+1+2", "new_gaokao_first_year": 2021,
        "max_score": 750, "valid_tracks": ["物理类", "历史类"], "region": "华中",
    },
    # ── 华南 ──────────────────────────────────────────────────────────────
    {
        "name": "广东", "name_full": "广东省", "pinyin": "guangdong", "slug": "guangdong",
        "code": "440000", "gaokao_reform_type": "3+1+2", "new_gaokao_first_year": 2021,
        "max_score": 750, "valid_tracks": ["物理类", "历史类"], "region": "华南",
    },
    {
        "name": "广西", "name_full": "广西壮族自治区", "pinyin": "guangxi", "slug": "guangxi",
        "code": "450000", "gaokao_reform_type": "3+1+2", "new_gaokao_first_year": 2024,
        "max_score": 750, "valid_tracks": ["物理类", "历史类"], "region": "华南",
    },
    {
        # 满分 900（语数外各 150 + 6 门选考各 75）
        "name": "海南", "name_full": "海南省", "pinyin": "hainan", "slug": "hainan",
        "code": "460000", "gaokao_reform_type": "3+3", "new_gaokao_first_year": 2020,
        "max_score": 900, "valid_tracks": ["综合改革"], "region": "华南",
    },
    # ── 西南 ──────────────────────────────────────────────────────────────
    {
        "name": "重庆", "name_full": "重庆市", "pinyin": "chongqing", "slug": "chongqing",
        "code": "500000", "gaokao_reform_type": "3+1+2", "new_gaokao_first_year": 2021,
        "max_score": 750, "valid_tracks": ["物理类", "历史类"], "region": "西南",
    },
    {
        "name": "四川", "name_full": "四川省", "pinyin": "sichuan", "slug": "sichuan",
        "code": "510000", "gaokao_reform_type": "3+1+2", "new_gaokao_first_year": 2025,
        "max_score": 750, "valid_tracks": ["物理类", "历史类"], "region": "西南",
    },
    {
        "name": "贵州", "name_full": "贵州省", "pinyin": "guizhou", "slug": "guizhou",
        "code": "520000", "gaokao_reform_type": "3+1+2", "new_gaokao_first_year": 2024,
        "max_score": 750, "valid_tracks": ["物理类", "历史类"], "region": "西南",
    },
    {
        "name": "云南", "name_full": "云南省", "pinyin": "yunnan", "slug": "yunnan",
        "code": "530000", "gaokao_reform_type": "3+1+2", "new_gaokao_first_year": 2025,
        "max_score": 750, "valid_tracks": ["物理类", "历史类"], "region": "西南",
    },
    {
        # 3+1+2，首届新高考 2027 年（2024 级学生）
        "name": "西藏", "name_full": "西藏自治区", "pinyin": "xizang", "slug": "xizang",
        "code": "540000", "gaokao_reform_type": "3+1+2", "new_gaokao_first_year": 2027,
        "max_score": 750, "valid_tracks": ["物理类", "历史类"], "region": "西南",
    },
    # ── 西北 ──────────────────────────────────────────────────────────────
    {
        "name": "陕西", "name_full": "陕西省", "pinyin": "shaanxi", "slug": "shaanxi",
        "code": "610000", "gaokao_reform_type": "3+1+2", "new_gaokao_first_year": 2025,
        "max_score": 750, "valid_tracks": ["物理类", "历史类"], "region": "西北",
    },
    {
        "name": "甘肃", "name_full": "甘肃省", "pinyin": "gansu", "slug": "gansu",
        "code": "620000", "gaokao_reform_type": "3+1+2", "new_gaokao_first_year": 2024,
        "max_score": 750, "valid_tracks": ["物理类", "历史类"], "region": "西北",
    },
    {
        # 2025 年首届新高考
        "name": "青海", "name_full": "青海省", "pinyin": "qinghai", "slug": "qinghai",
        "code": "630000", "gaokao_reform_type": "3+1+2", "new_gaokao_first_year": 2025,
        "max_score": 750, "valid_tracks": ["物理类", "历史类"], "region": "西北",
    },
    {
        "name": "宁夏", "name_full": "宁夏回族自治区", "pinyin": "ningxia", "slug": "ningxia",
        "code": "640000", "gaokao_reform_type": "3+1+2", "new_gaokao_first_year": 2025,
        "max_score": 750, "valid_tracks": ["物理类", "历史类"], "region": "西北",
    },
    {
        # 3+1+2，首届新高考 2027 年（2024 级学生）
        "name": "新疆", "name_full": "新疆维吾尔自治区", "pinyin": "xinjiang", "slug": "xinjiang",
        "code": "650000", "gaokao_reform_type": "3+1+2", "new_gaokao_first_year": 2027,
        "max_score": 750, "valid_tracks": ["物理类", "历史类"], "region": "西北",
    },
]


def seed_provinces() -> None:
    db = SessionLocal()
    try:
        for data in PROVINCES:
            stmt = pg_insert(Province).values(**data)
            stmt = stmt.on_conflict_do_update(
                index_elements=["code"],
                set_={k: v for k, v in data.items() if k != "code"},
            )
            db.execute(stmt)
        db.commit()
        print(f"✓ 已插入/更新 {len(PROVINCES)} 条省份记录")
    except Exception as exc:
        db.rollback()
        print(f"✗ seed 失败：{exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_provinces()
