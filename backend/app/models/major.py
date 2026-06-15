"""专业模型。"""

from datetime import datetime
from sqlalchemy import String, Boolean, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSON

from app.database import Base


class Major(Base):
    __tablename__ = "majors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    category: Mapped[str] = mapped_column(String(50))
    discipline: Mapped[str] = mapped_column(String(50))
    degree: Mapped[str] = mapped_column(String(50))
    duration: Mapped[str] = mapped_column(String(20))
    description: Mapped[str | None] = mapped_column(String(2000))
    employment_direction: Mapped[list | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    school_majors = relationship("SchoolMajor", back_populates="major", lazy="selectin")


class SchoolMajor(Base):
    __tablename__ = "school_majors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"), nullable=False)
    major_id: Mapped[int] = mapped_column(ForeignKey("majors.id"), nullable=False)
    college_name: Mapped[str] = mapped_column(String(200))
    tuition: Mapped[int | None] = mapped_column(Integer)
    duration: Mapped[str] = mapped_column(String(20))
    subject_requirement: Mapped[str | None] = mapped_column(String(100))
    is_national_first_class: Mapped[bool] = mapped_column(Boolean, default=False)
    is_provincial_first_class: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    school = relationship("School", back_populates="school_majors")
    major = relationship("Major", back_populates="school_majors")