"""专业接口契约测试。"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.major import Major, SchoolMajor


@pytest.fixture(scope="module")
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        # 专业目录
        db.add_all([
            Major(id=1, name="计算机科学与技术", code="080901", category="工学", discipline="计算机类",
                  degree="工学学士", duration="四年"),
            Major(id=2, name="软件工程", code="080902", category="工学", discipline="计算机类",
                  degree="工学学士", duration="四年"),
            Major(id=3, name="汉语言文学", code="050101", category="文学", discipline="中国语言文学类",
                  degree="文学学士", duration="四年"),
        ])
        # 学校专业关联
        db.add_all([
            SchoolMajor(id=1, school_id=1, major_id=1, college_name="信息学院", duration="四年",
                        is_national_first_class=True, is_provincial_first_class=False),
            SchoolMajor(id=2, school_id=1, major_id=2, college_name="软件学院", duration="四年",
                        is_national_first_class=True, is_provincial_first_class=False),
        ])
        db.commit()

    def override_get_db():
        with Session(engine) as session:
            yield session
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


class TestMajors:
    def test_list_all(self, client):
        resp = client.get("/api/majors")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3

    def test_keyword_filter(self, client):
        resp = client.get("/api/majors?keyword=软件")
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "软件工程"

    def test_category_filter(self, client):
        resp = client.get("/api/majors?category=文学")
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "汉语言文学"

    def test_pagination(self, client):
        resp = client.get("/api/majors?page_size=2&page=1")
        data = resp.json()
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert data["total"] == 3
        assert len(data["items"]) == 2

    def test_school_majors(self, client):
        resp = client.get("/api/majors/school/1")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["school_id"] == 1
        assert data[0]["major"]["name"] == "计算机科学与技术"

    def test_school_majors_empty(self, client):
        resp = client.get("/api/majors/school/99999")
        assert resp.status_code == 200
        assert resp.json() == []