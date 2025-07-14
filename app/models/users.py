from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class User(Base):
    """
    사용자 테이블: 직원 및 의사 계정 관리
    """
    __tablename__ = "users"
    
    # Primary Key: 사용자 고유 식별자 (자동 증가)
    user_id = Column(Integer, primary_key=True, autoincrement=True, comment='사용자 고유 식별자')
    
    # Foreign Key: 소속 병원 ID
    hospital_id = Column(Integer, ForeignKey("hospitals.hospital_id"), nullable=False, comment='소속 병원 ID')
    
    # 기본 정보
    name = Column(String(100), nullable=False, comment='사용자 실명')
    role = Column(String(50), nullable=False, comment='사용자 역할 (예: doctor, nurse, manager)')
    email = Column(String(200), nullable=False, unique=True, comment='로그인용 이메일 (중복 불가)')
    hashed_password = Column(String(500), nullable=False, comment='비밀번호 해시값 (보안을 위해 암호화)')
    
    # 상태 플래그
    is_doctor = Column(Boolean, default=False, nullable=False, comment='의사 여부 (0: 일반직원, 1: 의사)')
    is_active = Column(Boolean, default=True, nullable=False, comment='계정 활성화 상태 (0: 비활성, 1: 활성)')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment='계정 생성 시각')
    
    # Relationships: 다른 테이블과의 관계 정의
    hospital = relationship("Hospital", back_populates="users")  # 소속 병원 정보
    orders = relationship("Order", back_populates="created_by_user")  # 작성한 오더 목록
    assigned_treatments = relationship("OrderTreatment", back_populates="assigned_doctor")  # 배정된 시술 목록
    doctor_profile = relationship("DoctorProfile", back_populates="user", uselist=False)  # 의사 프로필 (1:1 관계)