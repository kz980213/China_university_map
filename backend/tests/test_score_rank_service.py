"""score_rank_service 单元测试。

运行方式（在 backend/ 目录下）：
  pytest tests/test_score_rank_service.py -v

使用 SQLite in-memory 数据库，不需要 PostgreSQL 连接。

测试数据（物理类 · 2024 · province_id=1）：
  score 750  count=2  cumulative_rank=2   ← 2 人得 750 分及以上
  score 749  count=5  cumulative_rank=7   ← 7 人得 749 分及以上
  score 748  count=10 cumulative_rank=17  ← 17 人得 748 分及以上
  score 700  count=20 cumulative_rank=50  ← 50 人得 700 分及以上
  （701-747 无记录，模拟真实一分一段可能存在的空档）

覆盖三类场景：正常命中 / 边界处理 / 缺数据。
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base
from app.models.province import Province
from app.models.score_rank import ScoreRankEntry
from app.services.score_rank_service import (
    _rank_to_score_by_id,
    _score_to_rank_by_id,
    ConversionResult,
)

# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

_PROVINCE_ID = 1
_YEAR = 2024
_TRACK = "物理类"


@pytest.fixture(scope="module")
def db():
    """SQLite in-memory 数据库，整个测试模块共享一个实例。"""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        # 测试省份（id 手动指定，方便测试）
        prov = Province(
            id=_PROVINCE_ID,
            name="测试省",
            name_full="测试省",
            pinyin="test",
            slug="test",
            code="990000",
            gaokao_reform_type="3+1+2",
            new_gaokao_first_year=2021,
            max_score=750,
            valid_tracks=[_TRACK, "历史类"],
            region="测试区",
        )
        session.add(prov)

        # 一分一段测试数据
        session.add_all([
            ScoreRankEntry(province_id=_PROVINCE_ID, year=_YEAR, track=_TRACK,
                           score=750, count=2, cumulative_rank=2),
            ScoreRankEntry(province_id=_PROVINCE_ID, year=_YEAR, track=_TRACK,
                           score=749, count=5, cumulative_rank=7),
            ScoreRankEntry(province_id=_PROVINCE_ID, year=_YEAR, track=_TRACK,
                           score=748, count=10, cumulative_rank=17),
            ScoreRankEntry(province_id=_PROVINCE_ID, year=_YEAR, track=_TRACK,
                           score=700, count=20, cumulative_rank=50),
            # 701-747 无记录，模拟空档
        ])
        session.commit()
        yield session


# ─────────────────────────────────────────────────────────────────────────────
# score_to_rank
# ─────────────────────────────────────────────────────────────────────────────

class TestScoreToRank:
    # ── 正常：精确命中 ────────────────────────────────────────────────────────

    def test_top_score_exact_match(self, db):
        r = _score_to_rank_by_id(db, _PROVINCE_ID, _YEAR, _TRACK, 750)
        assert r.value == 2 and r.reason == "ok"

    def test_middle_score_exact_match(self, db):
        r = _score_to_rank_by_id(db, _PROVINCE_ID, _YEAR, _TRACK, 749)
        assert r.value == 7 and r.reason == "ok"

    def test_bottom_score_exact_match(self, db):
        r = _score_to_rank_by_id(db, _PROVINCE_ID, _YEAR, _TRACK, 700)
        assert r.value == 50 and r.reason == "ok"

    # ── 边界：分数落在两档空档之间 ────────────────────────────────────────────

    def test_score_in_gap_floored_to_lower_rank(self, db):
        # 745 在 748-700 空档内。
        # next_higher(748) 的 cumulative_rank=17 偏乐观（真实位次 > 17，因为 745-747 还有人）。
        # 保守取 next_lower(700) 的 cumulative_rank=50，向下取整（floored）。
        r = _score_to_rank_by_id(db, _PROVINCE_ID, _YEAR, _TRACK, 745)
        assert r.value == 50 and r.reason == "floored"

    def test_score_just_above_bottom_entry_is_gap(self, db):
        # 701 刚好在最低档 700 之上，next_lower 仍是 700（cumulative_rank=50）。
        r = _score_to_rank_by_id(db, _PROVINCE_ID, _YEAR, _TRACK, 701)
        assert r.value == 50 and r.reason == "floored"

    # ── 边界：超出范围 ────────────────────────────────────────────────────────

    def test_score_above_max_out_of_range(self, db):
        r = _score_to_rank_by_id(db, _PROVINCE_ID, _YEAR, _TRACK, 751)
        assert r.value is None and r.reason == "out_of_range"

    def test_score_below_min_out_of_range(self, db):
        r = _score_to_rank_by_id(db, _PROVINCE_ID, _YEAR, _TRACK, 699)
        assert r.value is None and r.reason == "out_of_range"

    # ── 边界：缺数据 ──────────────────────────────────────────────────────────

    def test_missing_track_no_data(self, db):
        r = _score_to_rank_by_id(db, _PROVINCE_ID, _YEAR, "历史类", 700)
        assert r.value is None and r.reason == "no_data"

    def test_missing_year_no_data(self, db):
        r = _score_to_rank_by_id(db, _PROVINCE_ID, 2099, _TRACK, 700)
        assert r.value is None and r.reason == "no_data"

    def test_missing_province_no_data(self, db):
        r = _score_to_rank_by_id(db, 999, _YEAR, _TRACK, 700)
        assert r.value is None and r.reason == "no_data"


# ─────────────────────────────────────────────────────────────────────────────
# rank_to_score
# ─────────────────────────────────────────────────────────────────────────────

class TestRankToScore:
    # ── 正常：位次精确落在某档累计值上 ───────────────────────────────────────

    def test_rank_equals_top_cumulative(self, db):
        # rank=2 = cumulative_rank(750)，750 分的并列最后一名
        r = _rank_to_score_by_id(db, _PROVINCE_ID, _YEAR, _TRACK, 2)
        assert r.value == 750 and r.reason == "ok"

    def test_rank_equals_second_tier_cumulative(self, db):
        # rank=7 = cumulative_rank(749)
        r = _rank_to_score_by_id(db, _PROVINCE_ID, _YEAR, _TRACK, 7)
        assert r.value == 749 and r.reason == "ok"

    def test_rank_equals_bottom_cumulative(self, db):
        # rank=50 = cumulative_rank(700)，表内最低档
        r = _rank_to_score_by_id(db, _PROVINCE_ID, _YEAR, _TRACK, 50)
        assert r.value == 700 and r.reason == "ok"

    def test_rank_1_returns_top_score(self, db):
        # rank=1 < min_cum(=2)，查询仍正确返回 750（前 2 名并列最高分）
        r = _rank_to_score_by_id(db, _PROVINCE_ID, _YEAR, _TRACK, 1)
        assert r.value == 750 and r.reason == "ok"

    def test_rank_within_second_tier(self, db):
        # rank=5，在 749 分的并列段内（cumulative_rank 3-7）
        r = _rank_to_score_by_id(db, _PROVINCE_ID, _YEAR, _TRACK, 5)
        assert r.value == 749 and r.reason == "ok"

    def test_rank_within_third_tier(self, db):
        # rank=10，在 748 分段内（cumulative_rank 8-17）
        r = _rank_to_score_by_id(db, _PROVINCE_ID, _YEAR, _TRACK, 10)
        assert r.value == 748 and r.reason == "ok"

    def test_rank_in_gap_floored_to_lower_score(self, db):
        # rank=30 落在空档（ranks 18-49 对应真实分数 701-747，但表中无此段记录）。
        # MAX(score) WHERE cumulative_rank >= 30：
        #   cumulative_rank(750)=2, (749)=7, (748)=17 均 < 30，排除。
        #   cumulative_rank(700)=50 >= 30，满足 → MAX(score)=700。
        # 返回 700（下档 floor），与 score_to_rank 的 floored 方向自洽：
        # 两者都向低分方向取整，从学生视角均偏保守。
        # rank=30 不在任何一档的并列区间内（700 分的区间是 [31, 50]），
        # 空档检测：actual_cum=50, count=20 → 30 > 50-20=30 不成立 → "floored"。
        r = _rank_to_score_by_id(db, _PROVINCE_ID, _YEAR, _TRACK, 30)
        assert r.value == 700 and r.reason == "floored"

    # ── 边界 1：rank <= 0（无效位次）────────────────────────────────────────

    def test_rank_zero_out_of_range(self, db):
        r = _rank_to_score_by_id(db, _PROVINCE_ID, _YEAR, _TRACK, 0)
        assert r.value is None and r.reason == "out_of_range"

    def test_rank_negative_out_of_range(self, db):
        r = _rank_to_score_by_id(db, _PROVINCE_ID, _YEAR, _TRACK, -10)
        assert r.value is None and r.reason == "out_of_range"

    # ── 边界 2：rank > max(cumulative_rank)（超出表底端）─────────────────────

    def test_rank_just_beyond_max_out_of_range(self, db):
        # max_cum = 50，rank=51 越界
        r = _rank_to_score_by_id(db, _PROVINCE_ID, _YEAR, _TRACK, 51)
        assert r.value is None and r.reason == "out_of_range"

    def test_rank_far_beyond_max_out_of_range(self, db):
        r = _rank_to_score_by_id(db, _PROVINCE_ID, _YEAR, _TRACK, 10000)
        assert r.value is None and r.reason == "out_of_range"

    # ── 边界 3：缺数据（no_data）────────────────────────────────────────────

    def test_missing_track_no_data(self, db):
        r = _rank_to_score_by_id(db, _PROVINCE_ID, _YEAR, "历史类", 10)
        assert r.value is None and r.reason == "no_data"

    def test_missing_year_no_data(self, db):
        r = _rank_to_score_by_id(db, _PROVINCE_ID, 2099, _TRACK, 10)
        assert r.value is None and r.reason == "no_data"

    def test_missing_province_no_data(self, db):
        r = _rank_to_score_by_id(db, 999, _YEAR, _TRACK, 10)
        assert r.value is None and r.reason == "no_data"
