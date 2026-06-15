"""筛选器接口契约测试。

使用 SQLite in-memory 数据库（StaticPool 共享）。
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


@pytest.fixture(scope="module")
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        db.add_all([
            Province(id=1, name="北京", name_full="北京市", pinyin="beijing", slug="beijing",
                     code="110000", gaokao_reform_type="3+3", new_gaokao_first_year=2020,
                     max_score=750, valid_tracks=["综合改革"], region="华北"),
            Province(id=2, name="江苏", name_full="江苏省", pinyin="jiangsu", slug="jiangsu",
                     code="320000", gaokao_reform_type="3+1+2", new_gaokao_first_year=2021,
                     max_score=750, valid_tracks=["物理类", "历史类"], region="华东"),
            Province(id=3, name="西藏", name_full="西藏自治区", pinyin="xizang", slug="xizang",
                     code="540000", gaokao_reform_type="old", new_gaokao_first_year=None,
                     max_score=750, valid_tracks=[], region="西南"),
        ])
        db.add_all([
            AdmissionScore(
                school_id=1, year=2023, student_province="北京", subject_type="综合改革",
                min_score=660, is_school_level=True, match_status="matched",
            ),
            AdmissionScore(
                school_id=1, year=2025, student_province="北京", subject_type="综合改革",
                min_score=680, is_school_level=True, match_status="matched",
            ),
        ])
        db.commit()

    def override_get_db():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


class TestFilters:
    def test_provinces_non_empty(self, client):
        resp = client.get("/api/filters/provinces")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 3
        names = [p["name"] for p in data]
        assert "北京" in names
        assert "江苏" in names

    def test_subjects_3plus3_province(self, client):
        resp = client.get("/api/filters/subjects?province=北京&year=2024")
        assert resp.status_code == 200
        data = resp.json()
        assert data["tracks"] == ["综合改革"]

    def test_subjects_old_province(self, client):
        resp = client.get("/api/filters/subjects?province=西藏&year=2024")
        assert resp.status_code == 200
        data = resp.json()
        assert data["tracks"] == ["理科", "文科"]

    def test_years_range_covers_2023_to_2025(self, client):
        resp = client.get("/api/filters/years")
        assert resp.status_code == 200
        data = resp.json()
        assert data["min_year"] == 2023
        assert data["max_year"] == 2025