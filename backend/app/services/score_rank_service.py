"""分数⇄位次换算服务。

基于一分一段表（score_rank_tables）实现，纯领域服务，不含路由逻辑。

公开接口：
  score_to_rank(db, province, year, track, score) -> ConversionResult
  rank_to_score(db, province, year, track, rank)  -> ConversionResult

内部接口（供单元测试直接调用，跳过省份归一化）：
  _score_to_rank_by_id(db, province_id, year, track, score) -> ConversionResult
  _rank_to_score_by_id(db, province_id, year, track, rank)  -> ConversionResult

reason 取值：
  "ok"           — 精确命中表中记录
  "floored"      — 分数落在两档之间，向下取整（取更低分档的位次，保守）
  "interpolated" — 保留，供将来线性插值升级使用（当前未启用）
  "out_of_range" — 超出本表记录范围（分数或位次越界）
  "no_data"      — 该省 / 年份 / 科类 在表中无任何记录
"""

from dataclasses import dataclass

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.score_rank import ScoreRankEntry


@dataclass
class ConversionResult:
    value: int | None
    reason: str  # "ok" | "interpolated" | "out_of_range" | "no_data"


# ─────────────────────────────────────────────────────────────────────────────
# 公开接口（带省份归一化）
# ─────────────────────────────────────────────────────────────────────────────

def score_to_rank(
    db: Session, province: str, year: int, track: str, score: int
) -> ConversionResult:
    """将分数转换为该省该年该科类的位次。"""
    from app.services.province_service import get_province
    prov = get_province(db, province)
    if prov is None:
        return ConversionResult(value=None, reason="no_data")
    return _score_to_rank_by_id(db, prov.id, year, track, score)


def rank_to_score(
    db: Session, province: str, year: int, track: str, rank: int
) -> ConversionResult:
    """将位次反查对应的分数。"""
    from app.services.province_service import get_province
    prov = get_province(db, province)
    if prov is None:
        return ConversionResult(value=None, reason="no_data")
    return _rank_to_score_by_id(db, prov.id, year, track, rank)


# ─────────────────────────────────────────────────────────────────────────────
# 内部实现（接受 province_id，供测试直接调用）
# ─────────────────────────────────────────────────────────────────────────────

def _score_to_rank_by_id(
    db: Session, province_id: int, year: int, track: str, score: int
) -> ConversionResult:
    """
    逻辑：
      1. 无数据 → no_data
      2. 分数超出表范围 → out_of_range
      3. 精确命中 → cumulative_rank，reason="ok"
      4. 落在两档之间 → 取紧邻「更低分档」的 cumulative_rank，reason="floored"
         （向下取整：位次靠后，不高估排名，对冲稳保推荐安全；线性插值留 TODO）
    """
    where = (
        ScoreRankEntry.province_id == province_id,
        ScoreRankEntry.year == year,
        ScoreRankEntry.track == track,
    )

    has_data = db.scalar(select(func.count()).where(*where)) or 0
    if not has_data:
        return ConversionResult(value=None, reason="no_data")

    min_s, max_s = db.execute(
        select(func.min(ScoreRankEntry.score), func.max(ScoreRankEntry.score)).where(*where)
    ).one()
    if score < min_s or score > max_s:
        return ConversionResult(value=None, reason="out_of_range")

    exact = db.scalar(
        select(ScoreRankEntry.cumulative_rank).where(*where, ScoreRankEntry.score == score)
    )
    if exact is not None:
        return ConversionResult(value=exact, reason="ok")

    # 分数落在两档之间：取紧邻「更低分档」的 cumulative_rank（floor，位次靠后）
    # 理由：745 分的真实位次 = 得分≥745 的人数 > 得分≥748 的人数（next_higher 偏乐观）。
    # 取 next_lower 确保不高估学生排名，对冲稳保推荐时更安全。
    # TODO: 如将来需要线性插值（用上下两档的 cumulative_rank 按分数线性内插），
    #       在此替换为加权计算，同时把 reason 改为 "interpolated"。
    lower_rank = db.scalar(
        select(ScoreRankEntry.cumulative_rank)
        .where(*where, ScoreRankEntry.score < score)
        .order_by(ScoreRankEntry.score.desc())
        .limit(1)
    )
    return ConversionResult(value=lower_rank, reason="floored")


def _rank_to_score_by_id(
    db: Session, province_id: int, year: int, track: str, rank: int
) -> ConversionResult:
    """
    三类边界处理：
      边界 1 — rank <= 0（无效位次）
               → value=None, reason="out_of_range"
      边界 2 — rank > max(cumulative_rank)（超出表底端，低于最低档记录）
               → value=None, reason="out_of_range"
      边界 3 — 该省 / 年份 / 科类 无数据
               → value=None, reason="no_data"

    正常情况：
      取 cumulative_rank >= rank 中最高分，同时取 count 做空档检测。
      某档覆盖范围 [cumulative_rank - count + 1, cumulative_rank]：
        rank 落在区间内 → "ok"；落在区间下方（空档）→ "floored"。
      当 rank < min(cumulative_rank) 时所有行均满足，返回最高分（正确行为）。
    """
    # 边界 1：无效位次
    if rank <= 0:
        return ConversionResult(value=None, reason="out_of_range")

    where = (
        ScoreRankEntry.province_id == province_id,
        ScoreRankEntry.year == year,
        ScoreRankEntry.track == track,
    )

    # 边界 3：无数据
    has_data = db.scalar(select(func.count()).where(*where)) or 0
    if not has_data:
        return ConversionResult(value=None, reason="no_data")

    # 边界 2：位次超出记录下限
    max_cum = db.scalar(select(func.max(ScoreRankEntry.cumulative_rank)).where(*where))
    if rank > max_cum:
        return ConversionResult(value=None, reason="out_of_range")

    # 正常情况：取 cumulative_rank >= rank 中分数最高的那档，
    # 同时获取 count 以判断 rank 是否真正落在该档的并列区间内。
    # 某档覆盖的 rank 范围：[cumulative_rank - count + 1, cumulative_rank]
    # 若 rank 在此区间内 → "ok"（精确命中或并列）
    # 若 rank < (cumulative_rank - count + 1) → rank 落在空档 → "floored"
    row = db.execute(
        select(ScoreRankEntry.score, ScoreRankEntry.cumulative_rank, ScoreRankEntry.count)
        .where(*where, ScoreRankEntry.cumulative_rank >= rank)
        .order_by(ScoreRankEntry.score.desc())
        .limit(1)
    ).one_or_none()
    if row is None:
        return ConversionResult(value=None, reason="out_of_range")
    score, actual_cum, count = row
    reason = "ok" if rank > actual_cum - count else "floored"
    return ConversionResult(value=score, reason=reason)
