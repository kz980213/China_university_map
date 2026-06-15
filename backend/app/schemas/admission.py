from datetime import datetime
from pydantic import BaseModel


class AdmissionScoreQueryParams(BaseModel):
    student_province: str | None = None
    subject_type: str | None = None
    batch: str | None = None
    major_id: int | None = None
    year_from: int | None = None
    year_to: int | None = None


class AdmissionScoreRead(BaseModel):
    id: int
    school_id: int | None = None
    major_id: int | None = None
    year: int
    student_province: str
    subject_type: str
    batch: str | None = None
    major_name: str | None = None
    min_score: int
    min_rank: int | None = None  # 源数据自带真实位次（大多 NULL），不可被派生值覆盖
    avg_score: int | None = None
    max_score: int | None = None
    enrollment_count: int | None = None
    remark: str | None = None
    raw_school_name: str | None = None
    raw_school_code: str | None = None
    raw_major_name: str | None = None
    raw_major_code: str | None = None
    admission_group: str | None = None
    score_subject_req: str | None = None
    is_school_level: bool
    match_status: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class AdmissionScoreWithRank(AdmissionScoreRead):
    """分数线 + 派生位次（由 score_rank_service 实时换算）。

    min_rank 仍然是源数据真实位次（不受影响）。
    estimated_rank / estimated_rank_reason 来自 ConversionResult。
    """
    estimated_rank: int | None = None
    estimated_rank_reason: str | None = None


class AdmissionListItem(BaseModel):
    """跨院校分数线列表单条（JOIN schools + 关联子查询估算位次）。"""
    id: int
    school_id: int
    school_name: str
    school_province: str
    school_city: str
    is_985: bool
    is_211: bool
    is_double_first_class: bool
    year: int
    batch: str | None = None
    subject_type: str
    min_score: int
    estimated_rank: int | None = None  # 由一分一段表关联子查询得出，2021/2022 年无数据

    model_config = {"from_attributes": True}
