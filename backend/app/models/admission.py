"""录取分数线模型。

字段填充规则（导入脚本负责）：
  is_school_level: True=院校线（批次控制线），False=专业线（某专业的录取线）。
  match_status: "matched"=精确匹配到 schools 表，
                "partial"=模糊匹配，
                "unmatched"=未匹配（此时 school_id=None，raw_school_name 保留原始文本）。
"""

from datetime import datetime
from sqlalchemy import String, Integer, Boolean, CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AdmissionScore(Base):
    __tablename__ = "admission_scores"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # nullable：约 7.5% 的数据无法精确匹配到 schools 表
    school_id: Mapped[int | None] = mapped_column(ForeignKey("schools.id"))
    major_id: Mapped[int | None] = mapped_column(ForeignKey("majors.id"))
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    student_province: Mapped[str] = mapped_column(String(50), nullable=False)
    subject_type: Mapped[str] = mapped_column(String(20), nullable=False)
    # nullable：pro_type_min 等源数据不含批次信息，NULL 诚实表达"批次未知"
    batch: Mapped[str | None] = mapped_column(String(50))
    major_name: Mapped[str | None] = mapped_column(String(200))
    min_score: Mapped[int] = mapped_column(Integer, nullable=False)
    # nullable：部分数据源缺失位次字段
    min_rank: Mapped[int | None] = mapped_column(Integer)
    avg_score: Mapped[int | None] = mapped_column(Integer)
    max_score: Mapped[int | None] = mapped_column(Integer)
    enrollment_count: Mapped[int | None] = mapped_column(Integer)
    remark: Mapped[str | None] = mapped_column(String(500))

    # ── 原始文本字段（导入时保留，用于审计和二次匹配）────────────────────────
    raw_school_name: Mapped[str | None] = mapped_column(String(200))
    raw_school_code: Mapped[str | None] = mapped_column(String(20))
    raw_major_name: Mapped[str | None] = mapped_column(String(200))
    raw_major_code: Mapped[str | None] = mapped_column(String(20))

    # ── 录取附加信息 ───────────────────────────────────────────────────────────
    # 招生组/选考要求（各省格式差异大，存原始文本）
    admission_group: Mapped[str | None] = mapped_column(String(20))
    score_subject_req: Mapped[str | None] = mapped_column(String(100))

    # ── 匹配元数据（由导入脚本填充，ORM 不设 default）───────────────────────
    # NOT NULL：is_school_level 是唯一真相源，不允许为空。
    # 源数据结构可在入库时区分院校线与专业线，无需两步填写。
    # major_id IS NULL 不能代替 is_school_level 推断院校线（未匹配专业线也有 NULL major_id）。
    is_school_level: Mapped[bool] = mapped_column(Boolean, nullable=False)
    match_status: Mapped[str | None] = mapped_column(String(20))

    import_batch: Mapped[str | None] = mapped_column(String(50))

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    school = relationship("School", back_populates="admission_scores")

    __table_args__ = (
        # 院校线不携带任何专业级字段。
        # admission_group 不在约束内（部分省份院校线确有招生组编号）。
        CheckConstraint(
            "NOT is_school_level OR ("
            "major_id IS NULL AND major_name IS NULL AND "
            "raw_major_name IS NULL AND raw_major_code IS NULL AND "
            "score_subject_req IS NULL"
            ")",
            name="ck_school_level_no_major_fields",
        ),
    )