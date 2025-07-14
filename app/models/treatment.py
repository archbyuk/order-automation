from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class TreatmentCategory(Base):
    """
    시술 대분류 테이블: 시술 카테고리 관리
    """
    __tablename__ = "treatment_categories"
    
    # Primary Key: 카테고리 고유 ID (자동 증가)
    category_id = Column(Integer, primary_key=True, autoincrement=True, comment='시술 대분류 고유 ID')
    
    # 카테고리 정보
    name = Column(String(100), nullable=False, unique=True, comment='대분류 명 (예: 보톡스, 울쎄라, 필러, 레이저) - 중복 불가')
    description = Column(Text, nullable=True, comment='카테고리 설명 (선택 입력)')
    is_active = Column(Boolean, default=True, nullable=False, comment='카테고리 활성화 여부 (0: 비활성, 1: 활성)')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment='카테고리 등록 시각')
    
    # Relationships: 이 카테고리에 속한 시술들
    hospital_treatments = relationship("HospitalTreatment", back_populates="category")

class HospitalTreatment(Base):
    """
    병원별 시술 설정 테이블: 각 병원에서 사용하는 구체적인 시술들
    """
    __tablename__ = "hospital_treatments"
    
    # Primary Key: 병원별 시술 고유 ID (자동 증가)
    treatment_id = Column(Integer, primary_key=True, autoincrement=True, comment='병원별 시술 고유 ID')
    
    # Foreign Keys: 관련 테이블 참조
    hospital_id = Column(Integer, ForeignKey("hospitals.hospital_id"), nullable=False, comment='소속 병원 ID')
    category_id = Column(Integer, ForeignKey("treatment_categories.category_id"), nullable=False, comment='시술 대분류 ID (FK)')
    
    # 시술 정보
    name = Column(String(200), nullable=False, comment='병원에서 사용하는 구체적 시술명 (예: 보톡스 5u, 턱 보톡스, 승모보톡스)')
    duration_minutes = Column(Integer, nullable=False, default=30, comment='기본 소요 시간(분) - 스케줄링에 활용')
    description = Column(Text, nullable=True, comment='시술 상세 설명 (선택 입력)')
    is_active = Column(Boolean, default=True, nullable=False, comment='이 병원에서의 시술 사용 여부 (0: 사용안함, 1: 사용)')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment='병원별 시술 등록 시각')
    
    # Relationships
    hospital = relationship("Hospital", back_populates="hospital_treatments")  # 소속 병원 정보
    category = relationship("TreatmentCategory", back_populates="hospital_treatments")  # 소속 카테고리 정보
    order_treatments = relationship("OrderTreatment", back_populates="treatment")  # 오더에서 사용된 시술들
    treatment_group_items = relationship("TreatmentGroupItem", back_populates="treatment")  # 그룹 시술 구성

class TreatmentGroup(Base):
    """
    그룹 시술 테이블: 여러 개의 단일 시술을 묶어서 하나의 패키지로 관리
    """
    __tablename__ = "treatment_groups"
    
    # Primary Key: 그룹 시술 고유 ID (자동 증가)
    group_id = Column(Integer, primary_key=True, autoincrement=True, comment='그룹 시술 고유 ID')
    
    # Foreign Key: 소속 병원 ID
    hospital_id = Column(Integer, ForeignKey("hospitals.hospital_id"), nullable=False, comment='소속 병원 ID')
    
    # 그룹 시술 정보
    group_name = Column(String(200), nullable=False, comment='병원에서 사용하는 그룹 시술명 (오더 입력 기준)')
    description = Column(Text, nullable=True, comment='그룹 시술 설명 (상세 내용)')
    is_active = Column(Boolean, default=True, nullable=False, comment='그룹 시술 활성화 여부 (0: 비활성, 1: 활성)')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment='그룹 시술 등록 시각')
    
    # Relationships
    hospital = relationship("Hospital", back_populates="treatment_groups")  # 소속 병원 정보
    treatment_group_items = relationship("TreatmentGroupItem", back_populates="treatment_group")  # 그룹 구성 시술들

class TreatmentGroupItem(Base):
    """
    그룹 시술 구성 테이블: 각 그룹에 포함된 단일 시술과 개수 정의
    """
    __tablename__ = "treatment_group_items"
    
    # Composite Primary Key: 그룹 ID + 시술 ID (한 그룹의 한 시술 구성은 하나만)
    group_id = Column(Integer, ForeignKey("treatment_groups.group_id"), primary_key=True, comment='그룹 시술 ID (FK)')
    treatment_id = Column(Integer, ForeignKey("hospital_treatments.treatment_id"), primary_key=True, comment='병원별 시술 ID (FK)')
    
    # 구성 정보
    count = Column(Integer, default=1, nullable=False, comment='그룹 내 포함 회수 (예: 보톡스 2개, 필러 1개)')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment='그룹 구성 등록 시각')
    
    # Relationships
    treatment_group = relationship("TreatmentGroup", back_populates="treatment_group_items")  # 소속 그룹 정보
    treatment = relationship("HospitalTreatment", back_populates="treatment_group_items")  # 구성 시술 정보 