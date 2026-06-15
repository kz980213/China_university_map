"""省份统计接口契约测试。"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.province import Province
from app.models.school import School


@pytest.fixture(scope="module")
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        # 省份维度表（短名）
        db.add_all([
            Province(id=1, name="北京", name_full="北京市", pinyin="beijing", slug="beijing",
                     code="110000", gaokao_reform_type="3+3", new_gaokao_first_year=2020,
                     max_score=750, valid_tracks=["综合改革"], region="华北"),
            Province(id=2, name="江苏", name_full="江苏省", pinyin="jiangsu", slug="jiangsu",
                     code="320000", gaokao_reform_type="3+1+2", new_gaokao_first_year=2021,
                     max_score=750, valid_tracks=["物理类", "历史类"], region="华东"),
            Province(id=3, name="广西", name_full="广西壮族自治区", pinyin="guangxi", slug="guangxi",
                     code="450000", gaokao_reform_type="3+1+2", new_gaokao_first_year=2024,
                     max_score=750, valid_tracks=["物理类", "历史类"], region="华南"),
        ])
        # 学校 — 模拟真实库的"脏"数据：全称 province 和短名 province 混合
        # 北京：1条短名 + 1条全称 → 归一化后合并为 2
        # 江苏：1条短名 + 2条全称（"江苏省"）→ 归并为 3
        # 广西：仅全称"广西壮族自治区"1条 → 归一化后 1
        db.add_all([
            School(id=1, name="北大", school_code="10001", province="北京", city="海淀",
                   level="本科", school_type="综合", ownership="公办",
                   is_985=True, is_211=True, is_double_first_class=True,
                   longitude=116.0, latitude=40.0),
            School(id=2, name="清华", school_code="10002", province="北京市", city="海淀",
                   level="本科", school_type="综合", ownership="公办",
                   is_985=True, is_211=True, is_double_first_class=True,
                   longitude=116.0, latitude=40.0),
            School(id=3, name="江苏大学", school_code="10299", province="江苏", city="镇江",
                   level="本科", school_type="综合", ownership="公办",
                   is_985=False, is_211=True, is_double_first_class=False,
                   longitude=119.0, latitude=32.0),
            School(id=4, name="常州职业学院", school_code="11001", province="江苏省", city="常州",
                   level="专科", school_type="理工", ownership="公办",
                   is_985=False, is_211=False, is_double_first_class=False,
                   longitude=120.0, latitude=31.0),
            School(id=5, name="南京大学", school_code="10284", province="江苏省", city="南京",
                   level="本科", school_type="综合", ownership="公办",
                   is_985=True, is_211=True, is_double_first_class=True,
                   longitude=118.0, latitude=32.0),
            School(id=6, name="广西职业技术学院", school_code="11773", province="广西壮族自治区",
                   city="南宁", level="专科", school_type="综合", ownership="公办",
                   is_985=False, is_211=False, is_double_first_class=False,
                   longitude=108.0, latitude=23.0),
        ])
        db.commit()

    def override_get_db():
        with Session(engine) as session:
            yield session
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


class TestProvinceStats:
    def test_structure_is_list(self, client):
        resp = client.get("/api/stats/provinces")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_each_record_has_required_fields(self, client):
        resp = client.get("/api/stats/provinces")
        data = resp.json()
        for item in data:
            assert "province" in item
            assert "total" in item
            assert "undergraduate_count" in item
            assert "junior_college_count" in item
            assert "count_985" in item
            assert "count_211" in item
            assert "double_first_class_count" in item
            assert isinstance(item["total"], int)
            assert isinstance(item["undergraduate_count"], int)

    def test_full_name_normalization_beijing(self, client):
        """北京：短名"北京"1条 + 全称"北京市"1条 → 归一化后合并为 2 条，不分裂。"""
        resp = client.get("/api/stats/provinces")
        data = resp.json()
        beijing = [p for p in data if p["province"] == "北京"][0]
        assert beijing["total"] == 2
        assert beijing["undergraduate_count"] == 2
        assert beijing["junior_college_count"] == 0
        assert beijing["count_985"] == 2
        assert beijing["count_211"] == 2
        assert beijing["double_first_class_count"] == 2

    def test_full_name_normalization_jiangsu(self, client):
        """江苏：短名 1 + 全称 2 → 归并为 3 条，不出现短名/全称两行。"""
        resp = client.get("/api/stats/provinces")
        data = resp.json()
        jiangsu = [p for p in data if p["province"] == "江苏"]
        assert len(jiangsu) == 1, "江苏不应分裂为两行"
        row = jiangsu[0]
        assert row["total"] == 3
        assert row["undergraduate_count"] == 2
        assert row["junior_college_count"] == 1
        assert row["count_985"] == 1
        assert row["count_211"] == 2
        assert row["double_first_class_count"] == 1

    def test_full_name_normalization_guangxi(self, client):
        """广西：仅全称"广西壮族自治区"1条 → 归一化后列为短名"广西"。"""
        resp = client.get("/api/stats/provinces")
        data = resp.json()
        guangxi = [p for p in data if p["province"] == "广西"][0]
        assert guangxi["total"] == 1
        assert guangxi["junior_college_count"] == 1

    def test_no_full_name_leak(self, client):
        """确保输出中不出现任何全称省份字符串。"""
        resp = client.get("/api/stats/provinces")
        data = resp.json()
        provinces = {p["province"] for p in data}
        assert "北京市" not in provinces
        assert "江苏省" not in provinces
        assert "广西壮族自治区" not in provinces

    def test_no_missing_provinces(self, client):
        """确保所有在校 provinces 都出现在统计中。"""
        resp = client.get("/api/stats/provinces")
        data = resp.json()
        province_names = {p["province"] for p in data}
        assert "北京" in province_names
        assert "江苏" in province_names
        assert "广西" in province_names
