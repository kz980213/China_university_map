from pydantic import BaseModel


class VolunteerSchoolItem(BaseModel):
    school_id: int
    school_name: str
    school_province: str
    school_city: str
    is_985: bool
    is_211: bool
    is_double_first_class: bool
    min_score: int
    school_rank: int
    rank_diff: int  # school_rank - user_rank；正=有余量，负=用户位次差于录取线

    model_config = {"from_attributes": True}


class VolunteerResult(BaseModel):
    score: int
    province: str
    year: int
    subject_type: str
    user_rank: int | None
    user_rank_reason: str
    error: str | None = None
    reach: list[VolunteerSchoolItem] = []   # 冲
    target: list[VolunteerSchoolItem] = []  # 稳
    safety: list[VolunteerSchoolItem] = []  # 保
