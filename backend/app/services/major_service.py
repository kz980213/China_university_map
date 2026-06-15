"""专业服务层。"""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.major import Major, SchoolMajor


def get_school_majors(db: Session, school_id: int) -> list[SchoolMajor]:
    stmt = (
        select(SchoolMajor)
        .options(joinedload(SchoolMajor.major))
        .where(SchoolMajor.school_id == school_id)
    )
    return list(db.scalars(stmt).all())


def get_majors(db: Session, keyword: str | None = None, category: str | None = None, page: int = 1, page_size: int = 50) -> tuple[list[Major], int]:
    from sqlalchemy import func
    stmt = select(Major)
    if keyword:
        stmt = stmt.where(Major.name.ilike(f"%{keyword}%"))
    if category:
        stmt = stmt.where(Major.category == category)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    return list(db.scalars(stmt).all()), total