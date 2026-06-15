"""专业接口。"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.major import MajorRead, SchoolMajorRead
from app.services.major_service import get_school_majors, get_majors

router = APIRouter(prefix="/api/majors", tags=["majors"])


@router.get("", response_model=dict)
def list_majors(
    keyword: str | None = Query(None),
    category: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """专业目录列表（分页 + 关键词/门类筛选）。"""
    majors, total = get_majors(db, keyword=keyword, category=category, page=page, page_size=page_size)
    return {
        "items": [MajorRead.model_validate(m) for m in majors],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/school/{school_id}", response_model=list[SchoolMajorRead])
def list_school_majors(school_id: int, db: Session = Depends(get_db)):
    """获取某校开设的专业列表。"""
    return [SchoolMajorRead.model_validate(sm) for sm in get_school_majors(db, school_id)]