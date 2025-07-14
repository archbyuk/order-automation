# 모든 모델을 한 곳에서 import할 수 있게 해주는 파일
from app.database import Base

# Hospital 모델
from .hospital import Hospital

# User 관련 모델들
from .users import User, DoctorProfile, DoctorBreakTime, DoctorQualification, DoctorDailyMetric, DayOfWeek, DifficultyLevel

# Treatment 관련 모델들
from .treatment import (
    TreatmentCategory, Treatment, HospitalTreatment, 
    TreatmentGroup, HospitalTreatmentGroup, TreatmentGroupMapping
)

# Order 관련 모델들
from .order import Order, OrderTreatment, OrderLog

# Assignment 모델
from .assignment import Assignment

# 모든 모델을 한 곳에서 import할 수 있게 함
__all__ = [
    "Base",
    "Hospital",
    "User", "DoctorProfile", "DoctorBreakTime", "DoctorQualification", "DoctorDailyMetric",
    "DayOfWeek", "DifficultyLevel",
    "TreatmentCategory", "Treatment", "HospitalTreatment", 
    "TreatmentGroup", "HospitalTreatmentGroup", "TreatmentGroupMapping",
    "Order", "OrderTreatment", "OrderLog",
    "Assignment"
]

