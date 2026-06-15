"""志愿推荐服务。

算法（基于位次，小位次 = 成绩更好）：
  user_rank  = 考生位次（由分数经一分一段换算）
  school_rank = 院校往年录取最低分对应位次（同一分一段表换算）

  冲 (reach) ：school_rank ∈ (user_rank/1.3, user_rank)
              → 院校录取线优于考生，差距在 30% 以内，有一搏机会
  稳 (target)：school_rank ∈ [user_rank, user_rank * 1.3]
              → 考生位次优于录取线，把握较大
  保 (safety)：school_rank ∈ (user_rank * 1.3, user_rank * 2.5]
              → 考生位次远优于录取线，录取有把握

rank_diff = school_rank - user_rank
  负值 → 冲（考生差距），正值 → 稳/保（考生余量）
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.admission import AdmissionScore
from app.services.score_rank_service import score_to_rank


def get_volunteer_recommendations(
    db: Session,
    score: int,
    province: str,
    year: int,
    subject_type: str,
    reach_limit: int = 20,
    target_limit: int = 20,
    safety_limit: int = 20,
) -> dict:
    from app.models.school import School as SchoolModel
    from app.models.score_rank import ScoreRankEntry
    from app.models.province import Province

    base_meta = {
        "score": score, "province": province,
        "year": year, "subject_type": subject_type,
    }

    # ── 1. 考生分数 → 位次 ───────────────────────────────────────────────────
    conv = score_to_rank(db, province, year, subject_type, score)
    if conv.value is None:
        return {**base_meta, "user_rank": None, "user_rank_reason": conv.reason,
                "error": conv.reason, "reach": [], "target": [], "safety": []}

    user_rank = conv.value

    # ── 2. 省份 ID（关联子查询所需） ─────────────────────────────────────────
    prov_id = db.scalar(
        select(Province.id).where(
            (Province.name == province) | (Province.name_full == province)
        )
    )
    if prov_id is None:
        return {**base_meta, "user_rank": user_rank, "user_rank_reason": conv.reason,
                "error": "no_province", "reach": [], "target": [], "safety": []}

    # ── 3. 关联子查询：院校录取最低分 → 对应位次（floor 策略） ────────────────
    rank_subq = (
        select(ScoreRankEntry.cumulative_rank)
        .where(
            ScoreRankEntry.province_id == prov_id,
            ScoreRankEntry.year == year,
            ScoreRankEntry.track == subject_type,
            ScoreRankEntry.score <= AdmissionScore.min_score,
        )
        .order_by(ScoreRankEntry.score.desc())
        .limit(1)
        .correlate(AdmissionScore)
        .scalar_subquery()
    )

    # ── 4. 内层子查询（院校基本信息 + school_rank） ───────────────────────────
    inner = (
        select(
            AdmissionScore.school_id,
            SchoolModel.name.label("school_name"),
            SchoolModel.province.label("school_province"),
            SchoolModel.city.label("school_city"),
            SchoolModel.is_985,
            SchoolModel.is_211,
            SchoolModel.is_double_first_class,
            AdmissionScore.min_score,
            rank_subq.label("school_rank"),
        )
        .join(SchoolModel, AdmissionScore.school_id == SchoolModel.id)
        .where(
            AdmissionScore.student_province == province,
            AdmissionScore.year == year,
            AdmissionScore.subject_type == subject_type,
            AdmissionScore.is_school_level == True,
            AdmissionScore.school_id.is_not(None),
        )
    ).subquery()

    # ── 5. 区间阈值 ──────────────────────────────────────────────────────────
    reach_lo = int(user_rank / 1.3)
    reach_hi = user_rank - 1
    target_lo = user_rank
    target_hi = int(user_rank * 1.3)
    safety_lo = int(user_rank * 1.3) + 1
    safety_hi = int(user_rank * 2.5)

    # ── 6. 分类查询 ──────────────────────────────────────────────────────────
    def fetch(lo: int, hi: int, limit: int, asc: bool) -> list[dict]:
        stmt = (
            select(inner)
            .where(
                inner.c.school_rank.isnot(None),
                inner.c.school_rank >= lo,
                inner.c.school_rank <= hi,
            )
            .order_by(
                inner.c.school_rank.asc() if asc else inner.c.school_rank.desc()
            )
            .limit(limit)
        )
        result = []
        for r in db.execute(stmt).mappings().all():
            d = dict(r)
            d["rank_diff"] = int(d["school_rank"]) - user_rank
            result.append(d)
        return result

    return {
        **base_meta,
        "user_rank": user_rank,
        "user_rank_reason": conv.reason,
        "error": None,
        # 冲：最接近考生水平的院校排在最前（school_rank DESC）
        "reach": fetch(reach_lo, reach_hi, reach_limit, asc=False),
        # 稳/保：最接近考生水平的排在最前（school_rank ASC）
        "target": fetch(target_lo, target_hi, target_limit, asc=True),
        "safety": fetch(safety_lo, safety_hi, safety_limit, asc=True),
    }
