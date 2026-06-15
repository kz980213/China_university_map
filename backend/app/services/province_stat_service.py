from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.school import School
from app.schemas.common import ProvinceStatRead
from app.services import province_service


def get_province_stats(db: Session) -> list[ProvinceStatRead]:
    """各省院校数量统计（归一化到 provinces 维度表短名）。

    schools.province 存全称（"北京市"/"河南省"），省份维度表 name 为短名（"北京"/"河南"），
    通过 province_service.get_province 归一化后分组，确保与 /api/filters/provinces 短名一致。
    归一化失败的学校回退使用原始值，避免漏计。
    """
    schools = db.scalars(select(School)).all()
    stats: dict[str, dict] = {}
    for s in schools:
        prov = province_service.get_province(db, s.province)
        key = prov.name if prov else s.province
        if key not in stats:
            stats[key] = {
                "total": 0, "undergraduate": 0, "junior": 0,
                "n985": 0, "n211": 0, "double": 0,
            }
        st = stats[key]
        st["total"] += 1
        if s.level == "本科":
            st["undergraduate"] += 1
        else:
            st["junior"] += 1
        if s.is_985:
            st["n985"] += 1
        if s.is_211:
            st["n211"] += 1
        if s.is_double_first_class:
            st["double"] += 1
    return [
        ProvinceStatRead(
            province=p,
            total=v["total"],
            undergraduate_count=v["undergraduate"],
            junior_college_count=v["junior"],
            count_985=v["n985"],
            count_211=v["n211"],
            double_first_class_count=v["double"],
        )
        for p, v in sorted(stats.items(), key=lambda x: x[1]["total"], reverse=True)
    ]
