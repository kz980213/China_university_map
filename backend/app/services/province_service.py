"""省份归一化服务。

公开接口：
  get_province(db, input_str)           → Province | None
  get_province_tracks(db, name, year)   → list[str]
  get_province_max_score(db, name)      → int
"""

from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.models.province import Province


def get_province(db: Session, input_str: str) -> Province | None:
    """将多种形式的省份输入归一化为 Province 记录。

    接受：
      "河南"         短名
      "河南省"       全称
      "henan"        拼音 / slug
      "41"           2 位数字前缀（行政区划码首两位）
      "410000"       6 位行政区划码
    """
    if not input_str:
        return None
    s = input_str.strip()

    # 先尝试精确匹配（短名、全称、拼音、slug、完整行政区划码）
    province = db.scalar(
        select(Province).where(
            or_(
                Province.name == s,
                Province.name_full == s,
                Province.pinyin == s.lower(),
                Province.slug == s.lower(),
                Province.code == s,
            )
        )
    )
    if province:
        return province

    # 2 位数字前缀 → 匹配 6 位行政区划码（"41" → "410000"）
    if s.isdigit() and len(s) == 2:
        province = db.scalar(
            select(Province).where(Province.code.startswith(s))
        )

    return province


def get_province_tracks(db: Session, province_name: str, year: int) -> list[str]:
    """返回某省在指定年份的有效高考科类。

    三种制度并存的处理规则：
      1. new_gaokao_first_year is None  → 该省从未改革，始终返回 ["理科", "文科"]
      2. year < new_gaokao_first_year   → 该年仍是旧制，返回 ["理科", "文科"]
         （涵盖山西/内蒙古/青海 2025 首届前的历史年份）
      3. year >= new_gaokao_first_year  → 新高考已生效，返回 province.valid_tracks
         3+3 省份（上海、浙江、北京等）：["综合改革"]
         3+1+2 省份（大多数省份）：["物理类", "历史类"]

    valid_tracks 字段存储的是新高考制度下的科类；年份逻辑完全由本函数处理，
    不依赖单一表字段。
    """
    province = get_province(db, province_name)
    if province is None:
        return []

    if province.new_gaokao_first_year is None or year < province.new_gaokao_first_year:
        return ["理科", "文科"]

    return list(province.valid_tracks) if province.valid_tracks else []


def get_province_max_score(db: Session, province_name: str) -> int:
    """返回该省高考满分（750 / 海南 900 / 上海 660）。

    查不到省份时安全回退到 750。
    """
    province = get_province(db, province_name)
    return province.max_score if province else 750
