from datetime import datetime
from pydantic import BaseModel


class SchoolQueryParams(BaseModel):
    keyword: str | None = None
    province: str | None = None
    city: str | None = None
    level: str | None = None
    school_type: str | None = None
    ownership: str | None = None
    is_985: bool | None = None
    is_211: bool | None = None
    is_double_first_class: bool | None = None
    page: int = 1
    page_size: int = 20


class SchoolListItem(BaseModel):
    id: int
    name: str
    english_name: str | None = None
    school_code: str
    province: str
    city: str
    level: str
    school_type: str
    ownership: str
    is_985: bool
    is_211: bool
    is_double_first_class: bool
    popular_majors: list | None = None

    model_config = {"from_attributes": True}


class ProvinceRead(BaseModel):
    """省份最小信息，供筛选器下拉列表。"""
    id: int
    name: str
    name_full: str
    code: str
    slug: str

    model_config = {"from_attributes": True}


class SchoolRead(SchoolListItem):
    district: str | None = None
    address: str | None = None
    longitude: float | None = None
    latitude: float | None = None
    website: str | None = None
    admission_website: str | None = None
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
