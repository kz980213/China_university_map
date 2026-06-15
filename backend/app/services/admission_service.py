"""录取分数线服务层。"""

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.admission import AdmissionScore
from app.models.province import Province
from app.schemas.admission import AdmissionScoreQueryParams, AdmissionScoreRead, AdmissionScoreWithRank
from app.services.score_rank_service import score_to_rank, ConversionResult


def get_school_admission_scores(
    db: Session, school_id: int, params: AdmissionScoreQueryParams
) -> list[AdmissionScore]:
    stmt = select(AdmissionScore).where(AdmissionScore.school_id == school_id)
    if params.student_province:
        stmt = stmt.where(AdmissionScore.student_province == params.student_province)
    if params.subject_type:
        stmt = stmt.where(AdmissionScore.subject_type == params.subject_type)
    if params.batch:
        stmt = stmt.where(AdmissionScore.batch == params.batch)
    if params.major_id:
        stmt = stmt.where(AdmissionScore.major_id == params.major_id)
    if params.year_from:
        stmt = stmt.where(AdmissionScore.year >= params.year_from)
    if params.year_to:
        stmt = stmt.where(AdmissionScore.year <= params.year_to)
    stmt = stmt.order_by(AdmissionScore.year.desc(), AdmissionScore.min_score.desc())
    return list(db.scalars(stmt).all())


def get_school_admission_scores_with_rank(
    db: Session, school_id: int, params: AdmissionScoreQueryParams
) -> list[AdmissionScoreWithRank]:
    """获取学校分数线列表，并附加由一分一段换算的 estimated_rank。

    每条记录调用 score_to_rank 换算位次，按 (省份, 年份, 科类) 缓存避免重复查表。
    源数据 min_rank 字段不受影响，独立于 estimated_rank。
    """
    rows = get_school_admission_scores(db, school_id, params)
    if not rows:
        return []

    rank_cache: dict[tuple[str, int, str], ConversionResult] = {}

    results: list[AdmissionScoreWithRank] = []
    for row in rows:
        key = (row.student_province, row.year, row.subject_type)
        if key not in rank_cache:
            rank_cache[key] = score_to_rank(
                db, row.student_province, row.year, row.subject_type, row.min_score
            )
        conv = rank_cache[key]
        base = AdmissionScoreRead.model_validate(row).model_dump()
        results.append(
            AdmissionScoreWithRank(
                **base,
                estimated_rank=conv.value,
                estimated_rank_reason=conv.reason,
            )
        )
    return results


def get_admission_list(
    db: Session,
    student_province: str,
    year: int | None = None,
    subject_type: str | None = None,
    batch: str | None = None,
    keyword: str | None = None,
    is_985: bool | None = None,
    is_211: bool | None = None,
    is_double_first_class: bool | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[dict], int]:
    """跨院校分数线查询（院校线，JOIN schools 表，含关联子查询估算位次）。"""
    from app.models.school import School as SchoolModel
    from app.models.score_rank import ScoreRankEntry
    from app.models.province import Province
    from sqlalchemy import literal

    # 解析省份 ID，用于关联子查询（找不到则不算位次）
    prov_id = db.scalar(
        select(Province.id).where(
            (Province.name == student_province) | (Province.name_full == student_province)
        )
    )

    # 关联子查询：取分数 ≤ min_score 中最接近的累计位次（floor 策略，与 score_to_rank 一致）
    if prov_id is not None:
        rank_subq = (
            select(ScoreRankEntry.cumulative_rank)
            .where(
                ScoreRankEntry.province_id == prov_id,
                ScoreRankEntry.year == AdmissionScore.year,
                ScoreRankEntry.track == AdmissionScore.subject_type,
                ScoreRankEntry.score <= AdmissionScore.min_score,
            )
            .order_by(ScoreRankEntry.score.desc())
            .limit(1)
            .correlate(AdmissionScore)
            .scalar_subquery()
        )
    else:
        rank_subq = literal(None)

    base = (
        select(
            AdmissionScore.id,
            AdmissionScore.school_id,
            SchoolModel.name.label("school_name"),
            SchoolModel.province.label("school_province"),
            SchoolModel.city.label("school_city"),
            SchoolModel.is_985,
            SchoolModel.is_211,
            SchoolModel.is_double_first_class,
            AdmissionScore.year,
            AdmissionScore.batch,
            AdmissionScore.subject_type,
            AdmissionScore.min_score,
            rank_subq.label("estimated_rank"),
        )
        .join(SchoolModel, AdmissionScore.school_id == SchoolModel.id)
        .where(
            AdmissionScore.student_province == student_province,
            AdmissionScore.is_school_level == True,
            AdmissionScore.school_id.is_not(None),
        )
    )

    if year is not None:
        base = base.where(AdmissionScore.year == year)
    if subject_type:
        base = base.where(AdmissionScore.subject_type == subject_type)
    if batch:
        base = base.where(AdmissionScore.batch == batch)
    if keyword:
        base = base.where(SchoolModel.name.ilike(f"%{keyword}%"))
    if is_985 is not None:
        base = base.where(SchoolModel.is_985 == is_985)
    if is_211 is not None:
        base = base.where(SchoolModel.is_211 == is_211)
    if is_double_first_class is not None:
        base = base.where(SchoolModel.is_double_first_class == is_double_first_class)

    # COUNT 用不含 rank 子查询的 base（仅统计行数，不需要算位次）
    count_base = (
        select(AdmissionScore.id)
        .join(SchoolModel, AdmissionScore.school_id == SchoolModel.id)
        .where(
            AdmissionScore.student_province == student_province,
            AdmissionScore.is_school_level == True,
            AdmissionScore.school_id.is_not(None),
        )
    )
    if year is not None:
        count_base = count_base.where(AdmissionScore.year == year)
    if subject_type:
        count_base = count_base.where(AdmissionScore.subject_type == subject_type)
    if batch:
        count_base = count_base.where(AdmissionScore.batch == batch)
    if keyword:
        count_base = count_base.where(SchoolModel.name.ilike(f"%{keyword}%"))
    if is_985 is not None:
        count_base = count_base.where(SchoolModel.is_985 == is_985)
    if is_211 is not None:
        count_base = count_base.where(SchoolModel.is_211 == is_211)
    if is_double_first_class is not None:
        count_base = count_base.where(SchoolModel.is_double_first_class == is_double_first_class)

    total = db.scalar(select(func.count()).select_from(count_base.subquery())) or 0

    rows = db.execute(
        base.order_by(AdmissionScore.year.desc(), AdmissionScore.min_score.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).mappings().all()

    return [dict(r) for r in rows], total


def get_admission_year_range(db: Session) -> tuple[int | None, int | None]:
    """从 admission_scores 表获取年份范围（含 2023/2024/2025）。"""
    row = db.execute(
        select(
            func.min(AdmissionScore.year),
            func.max(AdmissionScore.year),
        )
    ).one()
    return (row[0], row[1])
