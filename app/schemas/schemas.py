# 오더에 대한 요청/응답 스키마 정의
from pydantic import BaseModel
from typing import Optional, List

# 로그인 관련 스키마
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    user_id: Optional[int] = None
    hospital_id: Optional[int] = None
    name: Optional[str] = None
    role: Optional[str] = None
    is_doctor: Optional[bool] = None
    message: Optional[str] = None

# 사용자가 오더 요청을 보낼 때 사용하는 스키마
class OrderCreateRequest(BaseModel):
    hospital_id: int    # hospital_id
    user_id: int        # user_id
    order_text: str     # row_order_text
    created_by: Optional[int] = None

# 오더 요쳥에 따른 클라이언트 응답용 스키마
class OrderCreateResponse(BaseModel):
    order_id: int
    message: str


# 파싱된 '시술 내용'을 담는 데이터 모델: 원본 오더, 시술 이름, 횟수, 회차, 부위 메모
class ParsedTreatment(BaseModel):
    raw_text: str
    name: str
    count: int = 1
    round_info: Optional[str] = None
    area_note: Optional[str] = None

# 매핑된 시술 내용을 담는 데이터 모델: 시술 ID, 횟수, 회차, 부위 메모, 소요 시간
class MappedTreatment(BaseModel):
    treatment_id: int
    count: int
    round_info: Optional[str]
    area_note: Optional[str]
    estimated_minutes: int


"""======================= 의사 배정 관련 데이터 구조 ======================="""
from dataclasses import dataclass
from app.models import DoctorProfile

@dataclass
class DoctorAssignmentResult:
    """의사 배정 결과 데이터 클래스"""
    treatment_id: int
    assigned_doctor_id: Optional[int]
    assigned_doctor_name: Optional[str]
    assignment_success: bool
    reason: str
    assignment_score: float = 0.0

@dataclass
class DoctorCandidate:
    """의사 후보 정보"""
    doctor: DoctorProfile
    score: float
    available_treatments: List[int]
    current_load: int