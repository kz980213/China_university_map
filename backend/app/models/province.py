"""省份维度表。"""

from sqlalchemy import String, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSON

from app.database import Base


class Province(Base):
    __tablename__ = "provinces"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # 短名（用于匹配用户输入 "北京"）
    name: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    # 全称（"北京市" / "广西壮族自治区"）
    name_full: Mapped[str] = mapped_column(String(30), nullable=False)
    # 汉语拼音（用于拼音匹配 "beijing"）
    pinyin: Mapped[str] = mapped_column(String(50), nullable=False)
    # URL-friendly slug（山西=shanxi / 陕西=shaanxi 保持唯一）
    slug: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    # GB/T 2260 行政区划码 6 位 "110000"
    code: Mapped[str] = mapped_column(String(6), nullable=False, unique=True)
    # 高考改革类型：3+3 / 3+1+2 / old
    gaokao_reform_type: Mapped[str] = mapped_column(String(10), nullable=False)
    # 首届新高考年份；None = 该省仍在旧制（西藏、新疆等）
    new_gaokao_first_year: Mapped[int | None] = mapped_column(Integer)
    # 高考满分（大多数 750；海南 900；上海 660）
    max_score: Mapped[int] = mapped_column(Integer, nullable=False, default=750)
    # 新高考制度下该省有效科类；旧制年份由 get_province_tracks() 返回 ["理科","文科"]
    valid_tracks: Mapped[list] = mapped_column(JSON, nullable=False)
    # 地理大区（华北 / 东北 / 华东 / 华中 / 华南 / 西南 / 西北）
    region: Mapped[str | None] = mapped_column(String(20))
