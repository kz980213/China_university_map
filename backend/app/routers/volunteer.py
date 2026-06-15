"""志愿推荐接口。"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.volunteer import VolunteerResult
from app.services.volunteer_service import get_volunteer_recommendations

router = APIRouter(prefix="/api/volunteer", tags=["volunteer"])


@router.get("/recommend", response_model=VolunteerResult)
def recommend_schools(
    score: int = Query(..., ge=100, le=750, description="高考总分"),
    province: str = Query(..., description="生源省份"),
    year: int = Query(..., description="年份，如 2024"),
    subject_type: str = Query(..., description="科类，如 物理类 / 历史类 / 理科 / 文科"),
    db: Session = Depends(get_db),
):
    """冲/稳/保志愿推荐。基于一分一段表换算位次后按区间分类。"""
    return get_volunteer_recommendations(db, score, province, year, subject_type)
