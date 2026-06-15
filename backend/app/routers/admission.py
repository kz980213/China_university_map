"""跨院校分数线查询接口。"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.admission import AdmissionListItem
from app.services.admission_service import get_admission_list

router = APIRouter(prefix="/api/admission", tags=["admission"])


@router.get("", response_model=dict)
def list_admission_scores(
    student_province: str = Query(..., description="生源省份，如 北京"),
    year: int | None = Query(None),
    subject_type: str | None = Query(None),
    batch: str | None = Query(None),
    keyword: str | None = Query(None),
    is_985: bool | None = Query(None),
    is_211: bool | None = Query(None),
    is_double_first_class: bool | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """跨院校分数线列表（仅院校线，分页）。"""
    items, total = get_admission_list(
        db,
        student_province=student_province,
        year=year,
        subject_type=subject_type,
        batch=batch,
        keyword=keyword,
        is_985=is_985,
        is_211=is_211,
        is_double_first_class=is_double_first_class,
        page=page,
        page_size=page_size,
    )
    return {
        "items": [AdmissionListItem.model_validate(item) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
