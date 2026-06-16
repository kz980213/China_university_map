"""地图下钻接口：省级城市聚合 + 市级学校点位。"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.school import School

router = APIRouter(prefix="/api/map", tags=["map"])


@router.get("/cities")
def get_province_cities(province: str, db: Session = Depends(get_db)):
    """返回指定省份各市的高校数量。province 传完整名称（如"江苏省"）。"""
    rows = (
        db.query(School.city, func.count(School.id).label("count"))
        .filter(School.province == province)
        .group_by(School.city)
        .order_by(func.count(School.id).desc())
        .all()
    )
    return [{"city": r.city, "count": r.count} for r in rows]


@router.get("/schools")
def get_map_markers(
    province: str = Query(None),
    city: str = Query(None),
    db: Session = Depends(get_db),
):
    """返回指定省/市的学校坐标列表（仅含有坐标的学校）。"""
    q = db.query(
        School.id,
        School.name,
        School.longitude,
        School.latitude,
        School.is_985,
        School.is_211,
        School.is_double_first_class,
        School.level,
    ).filter(
        School.longitude.isnot(None),
        School.latitude.isnot(None),
    )

    if city:
        q = q.filter(School.city == city)
    elif province:
        q = q.filter(School.province == province)

    return [
        {
            "id": s.id,
            "name": s.name,
            "lng": s.longitude,
            "lat": s.latitude,
            "is985": s.is_985,
            "is211": s.is_211,
            "isDoubleFirstClass": s.is_double_first_class,
            "level": s.level,
        }
        for s in q.all()
    ]
