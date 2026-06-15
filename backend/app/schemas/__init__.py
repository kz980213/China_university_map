from app.schemas.school import SchoolRead, SchoolListItem, SchoolQueryParams
from app.schemas.major import MajorRead, SchoolMajorRead
from app.schemas.admission import AdmissionScoreRead, AdmissionScoreQueryParams
from app.schemas.common import PaginatedResponse, ProvinceStatRead
from app.schemas.province import ProvinceRead, ProvinceTracksResponse

__all__ = [
    "SchoolRead",
    "SchoolListItem",
    "SchoolQueryParams",
    "MajorRead",
    "SchoolMajorRead",
    "AdmissionScoreRead",
    "AdmissionScoreQueryParams",
    "PaginatedResponse",
    "ProvinceStatRead",
    "ProvinceRead",
    "ProvinceTracksResponse",
]