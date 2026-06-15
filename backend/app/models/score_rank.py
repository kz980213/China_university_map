"""一分一段表模型。

每行代表：某省 · 某年 · 某科类 · 某分数 的人数与累计位次。
cumulative_rank 直接存储源数据，不在入库时重算。
"""

from sqlalchemy import Integer, String, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ScoreRankEntry(Base):
    __tablename__ = "score_rank_tables"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # 关联省份维度表
    province_id: Mapped[int] = mapped_column(ForeignKey("provinces.id"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    # 科类：物理类 / 历史类 / 综合改革 / 理科 / 文科
    track: Mapped[str] = mapped_column(String(20), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    # 该分数的考生人数
    count: Mapped[int] = mapped_column(Integer, nullable=False)
    # 该分数对应的累计位次（直接映射源数据，含义：score 及以上的考生总数）
    cumulative_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    import_batch: Mapped[str | None] = mapped_column(String(50))

    province = relationship("Province")

    __table_args__ = (
        UniqueConstraint(
            "province_id", "year", "track", "score",
            name="uq_score_rank_entry",
        ),
    )
