"""学校列表/详情接口契约测试。

使用 SQLite in-memory + StaticPool。
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.school import School
from app.models.province import Province
from app.models.admission import AdmissionScore


@pytest.fixture(scope="module")
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        # 省份
        db.add_all([
            Province(id=1, name="北京", name_full="北京市", pinyin="beijing", slug="beijing",
                     code="110000", gaokao_reform_type="3+3", new_gaokao_first_year=2020,
                     max_score=750, valid_tracks=["综合改革"], region="华北"),
            Province(id=2, name="江苏", name_full="江苏省", pinyin="jiangsu", slug="jiangsu",
                     code="320000", gaokao_reform_type="3+1+2", new_gaokao_first_year=2021,
                     max_score=750, valid_tracks=["物理类", "历史类"], region="华东"),
        ])
        # 学校 — 足够覆盖分页和筛选
        for i in range(1, 31):
            db.add(School(
                id=i, name=f"测试大学{i}", school_code=f"1000{i}",
                province="北京" if i <= 20 else "江苏",
                city="朝阳区" if i <= 15 else "海淀区",
                level="本科" if i % 3 != 0 else "专科",
                school_type="综合" if i % 2 == 0 else "理工",
                ownership="公办" if i <= 25 else "民办",
                is_985=(i <= 3), is_211=(i <= 10), is_double_first_class=(i <= 5),
                longitude=116.0, latitude=40.0,
            ))
        # 分数线（供某校详情/admission接口用）
        db.add(AdmissionScore(
            school_id=1, year=2024, student_province="北京", subject_type="综合改革",
            min_score=680, is_school_level=True, match_status="matched",
        ))
        db.commit()

    def override_get_db():
        with Session(engine) as session:
            yield session
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


class TestSchoolList:
    def test_default_page_20(self, client):
        resp = client.get("/api/schools")
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert data["total"] == 30
        assert len(data["items"]) == 20

    def test_page_2(self, client):
        resp = client.get("/api/schools?page=2&page_size=10")
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"] == 2
        assert data["page_size"] == 10
        assert data["total"] == 30
        assert len(data["items"]) == 10

    def test_province_filter(self, client):
        resp = client.get("/api/schools?province=北京")
        data = resp.json()
        assert data["total"] == 20  # 前 20 条是北京
        for item in data["items"]:
            assert item["province"] == "北京"

    def test_985_filter(self, client):
        resp = client.get("/api/schools?is_985=true")
        data = resp.json()
        assert data["total"] == 3
        for item in data["items"]:
            assert item["is_985"] is True

    def test_level_filter(self, client):
        resp = client.get("/api/schools?level=专科")
        data = resp.json()
        assert data["total"] == 10  # 30 条中 i%3==0 → 专科 10 条

    def test_keyword_filter(self, client):
        resp = client.get("/api/schools?keyword=大学1")
        data = resp.json()
        assert data["total"] == 11  # 测试大学1,10,11,12,...,19

    def test_combined_filters(self, client):
        """省份=北京 + 985 + 本科 → ID 3 虽是985但是专科，应被level过滤掉"""
        resp = client.get("/api/schools?province=北京&is_985=true&level=本科")
        data = resp.json()
        assert data["total"] == 2

    def test_empty_result(self, client):
        resp = client.get("/api/schools?province=西藏")
        data = resp.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_page_size_exceed(self, client):
        resp = client.get("/api/schools?page_size=100")
        data = resp.json()
        assert len(data["items"]) == 30

    def test_school_detail(self, client):
        resp = client.get("/api/schools/1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "测试大学1"
        assert data["is_985"] is True

    def test_school_detail_404(self, client):
        resp = client.get("/api/schools/99999")
        assert resp.status_code == 404