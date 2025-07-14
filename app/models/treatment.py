from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.users import DifficultyLevel

class TreatmentCategory(Base):
    """
    시술 대분류 테이블: 
    
    시술 카테고리 관리
    시술들을 대분류별로 그룹화하여 체계적으로 관리
    예: 보톡스, 울쎄라, 필러, 레이저 등
    """
    __tablename__ = "treatment_categories"
    
    # Primary Key: 카테고리 고유 ID (자동 증가)
    category_id = Column(Integer, primary_key=True, autoincrement=True, comment='카테고리 고유 ID')
    
    # 카테고리 정보
    name = Column(String(100), nullable=False, unique=True, comment='대분류 명 (예: 보톡스, 울쎄라) - 중복 불가')
    
    # Relationships: 이 카테고리에 속한 시술들
    treatments = relationship("Treatment", back_populates="category")

class Treatment(Base):
    """
    단일 시술 마스터 테이블: 실제 시술 단위 정의
    각 시술의 기본 정보와 난이도, 소요시간 등을 정의
    예: 보톡스 100u, 울쎄라 300샷 등
    """
    __tablename__ = "treatments"
    
    # Primary Key: 단일 시술 고유 ID (자동 증가)
    treatment_id = Column(Integer, primary_key=True, autoincrement=True, comment='단일 시술 고유 ID')
    
    # Foreign Key: 대분류 카테고리 ID
    category_id = Column(Integer, ForeignKey("treatment_categories.category_id"), nullable=False, comment='대분류 카테고리 ID')
    
    # 시술 기본 정보
    name = Column(String(200), nullable=False, comment='시술명 (예: 보톡스 100u, 울쎄라 300샷)')
    difficulty_level = Column(Enum(DifficultyLevel), nullable=False, comment='시술 난이도 (하/중/상) - 통계/분석용')
    default_duration_minutes = Column(Integer, nullable=False, comment='기본 소요 시간(분) - 스케줄링에 활용')
    is_active = Column(Boolean, default=True, nullable=False, comment='시술 활성화 여부 (0: 비활성, 1: 활성)')
    
    # Relationships: 다른 테이블과의 관계 정의
    category = relationship("TreatmentCategory", back_populates="treatments")  # 소속 카테고리
    hospital_treatments = relationship("HospitalTreatment", back_populates="treatment")  # 병원별 사용 설정
    doctor_qualifications = relationship("DoctorQualification", back_populates="treatment")  # 자격이 있는 의사들
    treatment_group_mappings = relationship("TreatmentGroupMapping", back_populates="treatment")  # 그룹 시술 구성
    order_treatments = relationship("OrderTreatment", back_populates="treatment")  # 오더에서 사용된 시술들

class HospitalTreatment(Base):
    """
    병원별 시술 사용제어 테이블: 병원마다 사용 가능한 시술 제어
    각 병원에서 어떤 시술을 사용할 수 있는지, 그리고 병원별로 다른 시술명을 사용하는지 관리
    """
    __tablename__ = "hospital_treatments"
    
    # Composite Primary Key: 병원 ID + 시술 ID (한 병원의 한 시술 설정은 하나만)
    hospital_id = Column(Integer, ForeignKey("hospitals.hospital_id"), primary_key=True, comment='병원 ID (FK)')
    treatment_id = Column(Integer, ForeignKey("treatments.treatment_id"), primary_key=True, comment='시술 ID (FK)')
    
    # 병원별 시술 설정
    is_active = Column(Boolean, default=True, nullable=False, comment='이 병원에서의 시술 사용 여부 (0: 사용안함, 1: 사용)')
    custom_name = Column(String(200), nullable=True, comment='병원 내에서 쓰는 시술명 별칭 (예: "보톡스" → "보톡스주사")')
    
    # Relationships
    hospital = relationship("Hospital", back_populates="hospital_treatments")  # 소속 병원 정보
    treatment = relationship("Treatment", back_populates="hospital_treatments")  # 시술 정보

class TreatmentGroup(Base):
    """
    공통 그룹 시술 마스터: 내부 단위 그룹 시술 정의
    여러 개의 단일 시술을 묶어서 하나의 패키지로 관리
    예: "페이스 리프팅 패키지" = 보톡스 + 필러 + 레이저
    """
    __tablename__ = "treatment_groups"
    
    # Primary Key: 그룹 시술 고유 ID (자동 증가)
    group_id = Column(Integer, primary_key=True, autoincrement=True, comment='그룹 시술 고유 ID')
    
    # 그룹 시술 정보
    name = Column(String(200), nullable=False, comment='공통 그룹명 (예: 페이스 리프팅 패키지)')
    description = Column(String(500), nullable=True, comment='그룹 시술 설명 (상세 내용)')
    
    # Relationships
    hospital_treatment_groups = relationship("HospitalTreatmentGroup", back_populates="treatment_group")  # 병원별 그룹명 매핑
    treatment_group_mappings = relationship("TreatmentGroupMapping", back_populates="treatment_group")  # 그룹 구성 시술들

class HospitalTreatmentGroup(Base):
    """
    병원별 그룹명 매핑 테이블: 오더 입력된 그룹명을 실제 그룹ID로 연결
    각 병원에서 사용하는 그룹 시술명을 표준 그룹 ID와 연결
    예: 병원A는 "페이스패키지", 병원B는 "리프팅세트"로 같은 그룹을 다르게 부름
    """
    __tablename__ = "hospital_treatment_groups"
    
    # Composite Primary Key: 병원 ID + 그룹 ID
    hospital_id = Column(Integer, ForeignKey("hospitals.hospital_id"), primary_key=True, comment='병원 ID (FK)')
    group_id = Column(Integer, ForeignKey("treatment_groups.group_id"), primary_key=True, comment='그룹 시술 ID (FK)')
    
    # 병원별 그룹명
    group_name = Column(String(200), nullable=False, comment='병원에서 사용하는 그룹 시술명 (오더 입력 기준)')
    
    # Relationships
    hospital = relationship("Hospital", back_populates="hospital_treatment_groups")  # 소속 병원 정보
    treatment_group = relationship("TreatmentGroup", back_populates="hospital_treatment_groups")  # 그룹 시술 정보

class TreatmentGroupMapping(Base):
    """
    그룹 ↔ 단일 시술 구성 테이블: 그룹에 속한 단일 시술 구성 저장
    각 그룹 시술이 어떤 단일 시술들로 구성되어 있는지, 그리고 각각 몇 개씩 포함되는지 정의
    예: "페이스 패키지" = 보톡스 100u × 1개 + 필러 2cc × 1개 + 레이저 × 1회
    """
    __tablename__ = "treatment_group_mappings"
    
    # Composite Primary Key: 그룹 ID + 시술 ID (한 그룹의 한 시술 구성은 하나만)
    group_id = Column(Integer, ForeignKey("treatment_groups.group_id"), primary_key=True, comment='그룹 시술 ID (FK)')
    treatment_id = Column(Integer, ForeignKey("treatments.treatment_id"), primary_key=True, comment='단일 시술 ID (FK)')
    
    # 구성 정보
    count = Column(Integer, default=1, nullable=False, comment='그룹 내 포함 회수 (예: 보톡스 2개, 필러 1개)')
    
    # Relationships
    treatment_group = relationship("TreatmentGroup", back_populates="treatment_group_mappings")  # 소속 그룹 정보
    treatment = relationship("Treatment", back_populates="treatment_group_mappings")  # 구성 시술 정보 