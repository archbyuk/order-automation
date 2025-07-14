from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Hospital(Base):
    """
    병원 정보 테이블: 
    
    여러 병원 환경에서 병원별 데이터 구분 기준
    각 병원의 기본 정보를 저장하고, 모든 관련 데이터의 소속을 구분하는 기준이 됨
    """
    __tablename__ = "hospitals"
    
    # Primary Key: 병원 고유 식별자 (자동 증가)
    hospital_id = Column(Integer, primary_key=True, autoincrement=True, comment='병원 고유 식별자')
    
    # 병원 기본 정보
    name = Column(String(200), nullable=False, comment='병원 이름')
    address = Column(String(500), nullable=True, comment='병원 주소 (선택 입력)')
    
    # 상태 정보
    is_active = Column(Boolean, default=True, nullable=False, comment='병원 서비스 사용 여부 (0: 비활성, 1: 활성)')
    
    # Relationships: 다른 테이블과의 관계 정의
    users = relationship("User", back_populates="hospital")  # 소속 직원/의사 목록
    orders = relationship("Order", back_populates="hospital")  # 소속 오더 목록
    hospital_treatments = relationship("HospitalTreatment", back_populates="hospital")  # 병원별 시술 설정
    hospital_treatment_groups = relationship("HospitalTreatmentGroup", back_populates="hospital")  # 병원별 그룹 시술 설정