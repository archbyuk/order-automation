from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, Time, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum

# 요일 enum: 의사의 휴무 시간을 요일별로 관리하기 위한 열거형
class DayOfWeek(enum.Enum):
    MONDAY = '월'
    TUESDAY = '화'
    WEDNESDAY = '수'
    THURSDAY = '목'
    FRIDAY = '금'
    SATURDAY = '토'
    SUNDAY = '일'

# 난이도 enum: 시술의 난이도를 표준화하여 관리하기 위한 열거형
class DifficultyLevel(enum.Enum):
    LOW = '하'      # 초급 시술
    MEDIUM = '중'   # 중급 시술
    HIGH = '상'     # 고급 시술

class User(Base):
    """
    사용자 테이블: 
    
    직원 및 의사 계정 관리
    병원 내 모든 직원(의사, 간호사, 실장 등)의 계정 정보를 저장
    """
    __tablename__ = "users"
    
    # Primary Key: 사용자 고유 식별자 (자동 증가)
    user_id = Column(Integer, primary_key=True, autoincrement=True, comment='사용자 고유 식별자')
    
    # Foreign Key: 소속 병원 ID (hospitals 테이블 참조)
    hospital_id = Column(Integer, ForeignKey("hospitals.hospital_id"), nullable=False, comment='소속 병원 ID')
    
    # 기본 정보
    name = Column(String(100), nullable=False, comment='사용자 실명')
    role = Column(String(50), nullable=False, comment='사용자 역할 (예: 의사, 실장, 간호사)')
    email = Column(String(200), nullable=False, unique=True, comment='로그인용 이메일 (중복 불가)')
    hashed_password = Column(String(500), nullable=False, comment='비밀번호 해시값 (보안을 위해 암호화)')
    
    # 상태 플래그
    is_doctor = Column(Boolean, default=False, nullable=False, comment='의사 여부 (0: 일반직원, 1: 의사)')
    is_active = Column(Boolean, default=True, nullable=False, comment='계정 활성화 상태 (0: 비활성, 1: 활성)')
    
    # Relationships: 다른 테이블과의 관계 정의
    hospital = relationship("Hospital", back_populates="users")  # 소속 병원 정보
    doctor_profile = relationship("DoctorProfile", back_populates="user", uselist=False)  # 의사 전용 프로필 (1:1 관계)
    doctor_break_times = relationship("DoctorBreakTime", back_populates="user")  # 의사 휴무 시간 목록
    doctor_qualifications = relationship("DoctorQualification", back_populates="user")  # 의사 자격 정보
    doctor_daily_metrics = relationship("DoctorDailyMetric", back_populates="user")  # 일일 시술 시간 통계
    orders = relationship("Order", back_populates="created_by_user")  # 작성한 오더 목록
    assignments = relationship("Assignment", back_populates="user")  # 배정된 시술 목록

class DoctorProfile(Base):
    """
    의사 프로필 테이블: 
    
    당직 여부 등 의료진 상태 정보
    의사만이 가지는 특별한 상태 정보를 별도로 관리
    """
    __tablename__ = "doctor_profiles"
    
    # Primary Key: 의사 사용자 ID (users 테이블의 user_id와 1:1 관계)
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True, comment='의사 사용자 ID')
    
    # 의사 상태 정보
    is_on_duty = Column(Boolean, default=False, nullable=False, comment='당직 중인지 여부 (0: 일반, 1: 당직)')
    
    # Relationships
    user = relationship("User", back_populates="doctor_profile")  # 소속 사용자 정보

class DoctorBreakTime(Base):
    """
    의사 휴무 시간 테이블: 
    
    요일+시간 구간 기반으로 휴무 스케줄 정의
    의사의 정기적인 휴무 시간을 요일별, 시간대별로 관리
    """
    __tablename__ = "doctor_break_times"
    
    # Primary Key: 휴무 구간 고유 ID
    id = Column(Integer, primary_key=True, autoincrement=True, comment='휴무 구간 고유 ID')
    
    # Foreign Key: 의사 사용자 ID
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, comment='의사 사용자 ID (FK)')
    
    # 휴무 시간 정보
    day_of_week = Column(Enum(DayOfWeek), nullable=False, comment='휴무 요일 (월~일)')
    start_time = Column(Time, nullable=False, comment='휴무 시작 시각 (HH:MM:SS)')
    end_time = Column(Time, nullable=False, comment='휴무 종료 시각 (HH:MM:SS)')
    
    # Relationships
    user = relationship("User", back_populates="doctor_break_times")  # 소속 의사 정보

class DoctorQualification(Base):
    """
    의사 자격 테이블: 
    
    의사가 가능한 단일 시술 목록 저장
    각 의사가 어떤 시술을 수행할 수 있는지 자격 정보를 관리
    """
    __tablename__ = "doctor_qualifications"
    
    # Composite Primary Key: 의사 ID + 시술 ID (한 의사가 한 시술에 대한 자격은 하나만)
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True, comment='의사 사용자 ID (FK)')
    treatment_id = Column(Integer, ForeignKey("treatments.treatment_id"), primary_key=True, comment='시술 ID (FK)')
    
    # Relationships
    user = relationship("User", back_populates="doctor_qualifications")  # 소속 의사 정보
    treatment = relationship("Treatment", back_populates="doctor_qualifications")  # 자격이 있는 시술 정보

class DoctorDailyMetric(Base):
    """
    일일 시술 시간 테이블: 
    
    의사 하루 누적 시술 시간 추적
    의사의 일일 시술 시간을 집계하여 업무량 분석에 활용
    """
    __tablename__ = "doctor_daily_metrics"
    
    # Composite Primary Key: 의사 ID + 날짜 (한 의사의 하루 통계는 하나만)
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True, comment='의사 사용자 ID (FK)')
    date = Column(Date, primary_key=True, comment='집계 기준 일자 (YYYY-MM-DD)')
    
    # 통계 데이터
    total_minutes = Column(Integer, default=0, nullable=False, comment='금일 누적 시술 시간(분)')
    
    # Relationships
    user = relationship("User", back_populates="doctor_daily_metrics")  # 소속 의사 정보
