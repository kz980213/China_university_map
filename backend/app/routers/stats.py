"""省份统计接口。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import ProvinceStatRead
from app.services.province_stat_service import get_province_stats

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/provinces", response_model=list[ProvinceStatRead])
def province_stats(db: Session = Depends(get_db)):
    """各省院校数量统计（总量/本科/专科/985/211/双一流）。"""
    return get_province_stats(db)