"""省批次控制线模型（高考分数线）。

每行代表：某省 · 某年 · 某科类 · 某批次 的控制分数线。

track 取值：
  历史类 / 物理类 —— 新高考 3+1+2 省份
  综合改革          —— 新高考 3+3 省份（沪/津/京/浙/琼/鲁）
  文科 / 理科       —— 未改革省份（新疆、西藏）

batch 取值：
  特殊类型          —— 强基/保送/艺体特招控制线
  本科 / 一本 / 二本 —— 本科批（各省叫法不同）
  一段 / 二段       —— 浙江/山东分段
  专科 / 高职       —— 专科/高职批
"""

from datetime import datetime
from sqlalchemy import Integer, String, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ProvinceCutline(Base):
    __tablename__ = "province_cutlines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    province_id: Mapped[int] = mapped_column(ForeignKey("provinces.id"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    track: Mapped[str] = mapped_column(String(20), nullable=False)   # 历史类/物理类/综合改革/文科/理科
    batch: Mapped[str] = mapped_column(String(20), nullable=False)   # 特殊类型/本科/一本/二本/专科/一段/二段
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    import_batch: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    province = relationship("Province")

    __table_args__ = (
        UniqueConstraint(
            "province_id", "year", "track", "batch",
            name="uq_province_cutline",
        ),
    )
