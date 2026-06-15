"""筛选器下拉选项接口。"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.province import Province
from app.schemas.school import ProvinceRead
from app.services.admission_service import get_admission_year_range
from app.services.province_service import get_province_tracks

router = APIRouter(prefix="/api/filters", tags=["filters"])


@router.get("/provinces", response_model=list[ProvinceRead])
def list_provinces(db: Session = Depends(get_db)):
    """返回全部省份列表（从 provinces 维度表）。"""
    from sqlalchemy import select
    return [
        ProvinceRead.model_validate(p) for p in db.scalars(select(Province)).all()
    ]


@router.get("/subjects")
def list_subject_types(
    province: str = Query(..., description="省份名称，如 北京"),
    year: int = Query(..., description="年份，如 2024"),
    db: Session = Depends(get_db),
):
    """返回某省某年的有效高考科类列表。

    省份制度改革判定由 province_service.get_province_tracks 处理：
    - 旧制年份 → ["理科", "文科"]
    - 新制省份 → ["物理类", "历史类"] 或 ["综合改革"]
    """
    tracks = get_province_tracks(db, province, year)
    return {"province": province, "year": year, "tracks": tracks}


@router.get("/years")
def list_years(db: Session = Depends(get_db)):
    """从 admission_scores 表获取年份范围（含 2023/2024/2025）。"""
    y_min, y_max = get_admission_year_range(db)
    return {"min_year": y_min, "max_year": y_max}