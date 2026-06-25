from app.models.school import School
from app.models.major import Major, SchoolMajor
from app.models.admission import AdmissionScore
from app.models.province import Province
from app.models.score_rank import ScoreRankEntry
from app.models.province_cutline import ProvinceCutline

__all__ = ["School", "Major", "SchoolMajor", "AdmissionScore", "Province", "ScoreRankEntry", "ProvinceCutline"]