"""学校服务层。"""

from sqlalchemy import select, func, or_, case
from sqlalchemy.orm import Session
from typing import Sequence

from app.models.school import School
from app.schemas.school import SchoolQueryParams
from app.services import province_service


def get_schools(db: Session, params: SchoolQueryParams) -> tuple[Sequence[School], int, dict]:
    """获取学校列表，同时返回当前筛选条件下的分类计数。"""
    stmt = select(School)

    if params.keyword:
        kw = f"%{params.keyword}%"
        stmt = stmt.where(
            (School.name.ilike(kw))
            | (School.province.ilike(kw))
            | (School.city.ilike(kw))
        )
    if params.province:
        normalized = province_service.get_province(db, params.province)
        if normalized:
            stmt = stmt.where(
                or_(
                    School.province == normalized.name,
                    School.province == normalized.name_full,
                )
            )
        else:
            stmt = stmt.where(School.province == params.province)
    if params.level:
        levels = [l.strip() for l in params.level.split(',') if l.strip()]
        stmt = stmt.where(School.level.in_(levels))
    if params.school_type:
        stmt = stmt.where(School.school_type == params.school_type)
    if params.ownership:
        stmt = stmt.where(School.ownership == params.ownership)
    if params.is_985 is not None:
        stmt = stmt.where(School.is_985 == params.is_985)
    if params.is_211 is not None:
        stmt = stmt.where(School.is_211 == params.is_211)
    if params.is_double_first_class is not None:
        stmt = stmt.where(School.is_double_first_class == params.is_double_first_class)

    # 一次聚合查询同时取总数和各分类计数，避免额外 count 查询
    sub = stmt.subquery()
    agg = db.execute(
        select(
            func.count().label("total"),
            func.sum(case((sub.c.is_985, 1), else_=0)).label("n985"),
            func.sum(case((sub.c.is_211, 1), else_=0)).label("n211"),
            func.sum(case((sub.c.is_double_first_class, 1), else_=0)).label("ndfc"),
            func.sum(case((sub.c.level == "本科", 1), else_=0)).label("undergrad"),
            func.sum(case((sub.c.level != "本科", 1), else_=0)).label("junior"),
        ).select_from(sub)
    ).one()

    total = int(agg.total or 0)
    counts = {
        "undergraduate_count": int(agg.undergrad or 0),
        "junior_college_count": int(agg.junior or 0),
        "count_985": int(agg.n985 or 0),
        "count_211": int(agg.n211 or 0),
        "double_first_class_count": int(agg.ndfc or 0),
    }

    # 分页
    offset = (params.page - 1) * params.page_size
    paginated_stmt = stmt.offset(offset).limit(params.page_size).order_by(School.id)
    schools = db.scalars(paginated_stmt).all()

    return schools, total, counts


def get_school_by_id(db: Session, school_id: int) -> School | None:
    """获取学校详情。"""
    return db.get(School, school_id)