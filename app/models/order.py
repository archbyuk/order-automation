from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Order(Base):
    """
    오더 테이블: 사용자가 입력한 원문 오더 정보 저장
    """
    __tablename__ = "orders"
    
    # Primary Key: 오더 고유 식별자 (자동 증가)
    order_id = Column(Integer, primary_key=True, autoincrement=True, comment='오더 고유 식별자')
    
    # Foreign Keys: 관련 테이블 참조
    hospital_id = Column(Integer, ForeignKey("hospitals.hospital_id"), nullable=False, comment='오더 소속 병원 ID')
    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=False, comment='오더 작성자 사용자 ID')
    
    # 환자 정보
    patient_name = Column(String(100), nullable=True, comment='환자 이름')
    chart_number = Column(String(50), nullable=True, comment='차트 번호 (환자 고유 식별자)')
    
    # 오더 내용
    raw_text = Column(Text, nullable=False, comment='입력된 오더 원문 전체 텍스트 (파싱 전 원본)')
    room = Column(String(50), nullable=True, comment='시술실 정보 (예: 1번실, VIP실)')
    
    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment='오더 생성 시각')
    
    # Relationships: 다른 테이블과의 관계 정의
    hospital = relationship("Hospital", back_populates="orders")  # 소속 병원 정보
    created_by_user = relationship("User", back_populates="orders")  # 작성자 정보
    order_treatments = relationship("OrderTreatment", back_populates="order")  # 파싱된 시술 목록

class OrderTreatment(Base):
    """
    오더 파싱 테이블: 오더를 개별 단일 시술 단위로 분리하여 저장
    """
    __tablename__ = "order_treatments"
    
    # Primary Key: 파싱된 단일 시술 항목 ID (자동 증가)
    id = Column(Integer, primary_key=True, autoincrement=True, comment='파싱된 단일 시술 항목 ID')
    
    # Foreign Keys: 관련 테이블 참조
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False, comment='관련 오더 ID (FK)')
    treatment_id = Column(Integer, ForeignKey("hospital_treatments.treatment_id"), nullable=False, comment='병원별 시술 ID (FK)')
    
    # 파싱된 시술 정보
    count = Column(Integer, default=1, nullable=False, comment='시술 횟수 (예: 보톡스 2개, 필러 1개)')
    round_info = Column(String(50), nullable=True, comment='회차 정보 (예: 1-3회, 2차)')
    area_note = Column(String(200), nullable=True, comment='부위 메모 (예: 턱 부분 민감, 이마 주의)')
    parsed_text = Column(String(500), nullable=True, comment='파싱된 텍스트 원문 일부 (해당 시술 부분만)')
    estimated_minutes = Column(Integer, default=0, nullable=False, comment='계산된 시술 소요 시간(분) - 스케줄링용')
    
    # 의사 배정 정보 (assignment 테이블 대신 통합)
    assigned_doctor_id = Column(Integer, ForeignKey("users.user_id"), nullable=True, comment='배정된 의사 사용자 ID (FK)')
    assigned_at = Column(DateTime, nullable=True, comment='의사 배정 시각')
    
    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment='파싱된 시술 등록 시각')
    
    # Relationships
    order = relationship("Order", back_populates="order_treatments")  # 소속 오더 정보
    treatment = relationship("HospitalTreatment", back_populates="order_treatments")  # 시술 정보
    assigned_doctor = relationship("User", back_populates="assigned_treatments")  # 배정된 의사 정보 