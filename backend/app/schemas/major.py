from datetime import datetime
from pydantic import BaseModel


class MajorRead(BaseModel):
    id: int
    name: str
    code: str
    category: str
    discipline: str
    degree: str
    duration: str
    description: str | None = None
    employment_direction: list | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class SchoolMajorRead(BaseModel):
    id: int
    school_id: int
    major_id: int
    college_name: str
    tuition: int | None = None
    duration: str
    subject_requirement: str | None = None
    is_national_first_class: bool
    is_provincial_first_class: bool
    major: MajorRead | None = None

    model_config = {"from_attributes": True}