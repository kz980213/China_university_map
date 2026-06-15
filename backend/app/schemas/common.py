from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class ProvinceStatRead(BaseModel):
    province: str
    total: int
    undergraduate_count: int
    junior_college_count: int
    count_985: int
    count_211: int
    double_first_class_count: int

    model_config = {"from_attributes": True}