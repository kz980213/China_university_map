"""院校接口（列表/详情/分数线）。"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.school import SchoolListItem, SchoolRead, SchoolQueryParams
from app.schemas.admission import AdmissionScoreQueryParams, AdmissionScoreWithRank
from app.services.school_service import get_schools, get_school_by_id
from app.services.admission_service import get_school_admission_scores_with_rank

router = APIRouter(prefix="/api/schools", tags=["schools"])


@router.get("", response_model=dict)
def list_schools(
    keyword: str | None = Query(None),
    province: str | None = Query(None),
    city: str | None = Query(None),
    level: str | None = Query(None),
    school_type: str | None = Query(None),
    ownership: str | None = Query(None),
    is_985: bool | None = Query(None),
    is_211: bool | None = Query(None),
    is_double_first_class: bool | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """学校列表（分页 + 多条件筛选）。"""
    params = SchoolQueryParams(
        keyword=keyword, province=province, city=city,
        level=level, school_type=school_type, ownership=ownership,
        is_985=is_985, is_211=is_211,
        is_double_first_class=is_double_first_class,
        page=page, page_size=page_size,
    )
    schools, total, counts = get_schools(db, params)
    return {
        "items": [SchoolListItem.model_validate(s) for s in schools],
        "total": total,
        "page": page,
        "page_size": page_size,
        **counts,
    }


@router.get("/{school_id}", response_model=SchoolRead)
def get_school_detail(school_id: int, db: Session = Depends(get_db)):
    """学校详情。"""
    school = get_school_by_id(db, school_id)
    if not school:
        raise HTTPException(status_code=404, detail="学校不存在")
    return school


@router.get("/{school_id}/admission", response_model=list[AdmissionScoreWithRank])
def get_school_admission(
    school_id: int,
    student_province: str | None = Query(None),
    subject_type: str | None = Query(None),
    batch: str | None = Query(None),
    year_from: int | None = Query(None),
    year_to: int | None = Query(None),
    db: Session = Depends(get_db),
):
    """获取指定学校的录取分数线（含一分一段换算位次）。"""
    params = AdmissionScoreQueryParams(
        student_province=student_province,
        subject_type=subject_type,
        batch=batch,
        year_from=year_from,
        year_to=year_to,
    )
    return get_school_admission_scores_with_rank(db, school_id, params)
