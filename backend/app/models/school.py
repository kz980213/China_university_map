"""学校模型。"""

from datetime import datetime
from sqlalchemy import String, Boolean, Float, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSON

from app.database import Base


class School(Base):
    __tablename__ = "schools"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    english_name: Mapped[str | None] = mapped_column(String(300))
    school_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    province: Mapped[str] = mapped_column(String(50), nullable=False)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    district: Mapped[str | None] = mapped_column(String(50))
    address: Mapped[str | None] = mapped_column(String(500))
    longitude: Mapped[float | None] = mapped_column(Float)
    latitude: Mapped[float | None] = mapped_column(Float)
    level: Mapped[str] = mapped_column(String(20), nullable=False)
    school_type: Mapped[str] = mapped_column(String(20), nullable=False)
    ownership: Mapped[str] = mapped_column(String(20), nullable=False)
    is_985: Mapped[bool] = mapped_column(Boolean, default=False)
    is_211: Mapped[bool] = mapped_column(Boolean, default=False)
    is_double_first_class: Mapped[bool] = mapped_column(Boolean, default=False)
    website: Mapped[str | None] = mapped_column(String(500))
    admission_website: Mapped[str | None] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    popular_majors: Mapped[list | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    school_majors = relationship("SchoolMajor", back_populates="school", lazy="selectin")
    admission_scores = relationship("AdmissionScore", back_populates="school", lazy="selectin")