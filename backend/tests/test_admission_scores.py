"""分数线接口契约测试。

使用 SQLite in-memory 数据库（StaticPool 共享），不依赖 PostgreSQL。
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.admission import AdmissionScore
from app.models.province import Province
from app.models.score_rank import ScoreRankEntry

_SCHOOL_ID = 5
_YEAR_WITH_DATA = 2024
_YEAR_NO_DATA = 2023


@pytest.fixture(scope="module")
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        db.add(Province(
            id=1, name="北京", name_full="北京市", pinyin="beijing", slug="beijing",
            code="110000", gaokao_reform_type="3+3", new_gaokao_first_year=2020,
            max_score=750, valid_tracks=["综合改革"], region="华北",
        ))
        db.add_all([
            ScoreRankEntry(province_id=1, year=_YEAR_WITH_DATA, track="综合改革", score=700, count=5, cumulative_rank=10),
            ScoreRankEntry(province_id=1, year=_YEAR_WITH_DATA, track="综合改革", score=680, count=10, cumulative_rank=50),
        ])
        db.add_all([
            AdmissionScore(
                school_id=_SCHOOL_ID, year=_YEAR_WITH_DATA, student_province="北京",
                subject_type="综合改革", min_score=680, min_rank=5000,
                is_school_level=True, match_status="matched",
            ),
            AdmissionScore(
                school_id=_SCHOOL_ID, year=_YEAR_NO_DATA, student_province="北京",
                subject_type="综合改革", min_score=660, min_rank=None,
                is_school_level=True, match_status="matched",
            ),
        ])
        db.commit()

    def override_get_db():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


class TestAdmissionEndpoint:
    def test_returns_200(self, client):
        resp = client.get(f"/api/schools/{_SCHOOL_ID}/admission")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 2

    def test_min_rank_preserved_not_overwritten_by_estimated(self, client):
        resp = client.get(f"/api/schools/{_SCHOOL_ID}/admission?year_from={_YEAR_WITH_DATA}&year_to={_YEAR_WITH_DATA}")
        assert resp.status_code == 200
        data = resp.json()
        row = data[0]
        assert row["min_rank"] == 5000, "源数据 min_rank 应保持 5000"
        assert row["estimated_rank"] is not None, "2024 有一分一段，estimated_rank 应有值"
        assert row["estimated_rank"] != 5000, "estimated_rank 不应等于 min_rank"

    def test_2023_no_data_reason(self, client):
        resp = client.get(f"/api/schools/{_SCHOOL_ID}/admission?year_from={_YEAR_NO_DATA}&year_to={_YEAR_NO_DATA}")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        row = data[0]
        assert row["year"] == _YEAR_NO_DATA
        assert row["estimated_rank"] is None, "2023 无一分一段，estimated_rank 应为 None"
        assert row["estimated_rank_reason"] == "no_data", "2023 应返回 reason=no_data"

    def test_unknown_school_returns_empty(self, client):
        resp = client.get("/api/schools/99999/admission")
        assert resp.status_code == 200
        assert resp.json() == []