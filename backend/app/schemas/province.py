from pydantic import BaseModel


class ProvinceRead(BaseModel):
    id: int
    name: str
    name_full: str
    pinyin: str
    slug: str
    code: str
    gaokao_reform_type: str
    new_gaokao_first_year: int | None = None
    max_score: int
    valid_tracks: list[str]
    region: str | None = None

    model_config = {"from_attributes": True}


class ProvinceTracksResponse(BaseModel):
    """供前端分数输入校验和展示使用。"""
    province: str
    year: int
    tracks: list[str]
    gaokao_reform_type: str
    max_score: int
