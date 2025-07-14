from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Hospital(Base):
    """
    병원 정보 테이블: 여러 병원 환경에서 병원별 데이터 구분 기준
    """
    __tablename__ = "hospitals"
    
    # Primary Key: 병원 고유 식별자 (자동 증가)
    hospital_id = Column(Integer, primary_key=True, autoincrement=True, comment='병원 고유 식별자')
    
    # 병원 정보
    name = Column(String(200), nullable=False, comment='병원 이름')
    address = Column(String(500), nullable=True, comment='병원 주소 (선택 입력)')
    is_active = Column(Boolean, default=True, nullable=False, comment='병원 서비스 사용 여부 (0: 비활성, 1: 활성)')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment='병원 등록 시각')
    
    # Relationships: 다른 테이블과의 관계 정의
    users = relationship("User", back_populates="hospital")  # 소속 사용자들
    hospital_treatments = relationship("HospitalTreatment", back_populates="hospital")  # 병원별 시술들
    treatment_groups = relationship("TreatmentGroup", back_populates="hospital")  # 병원별 그룹 시술들
    orders = relationship("Order", back_populates="hospital")  # 병원 오더들
    doctor_profiles = relationship("DoctorProfile", back_populates="hospital")  # 병원 의사 프로필들