from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Assignment(Base):
    """
    의사 배정 테이블: 
    
    파싱된 단일 시술에 어떤 의사가 배정되었는지 기록
    각 시술 항목에 대해 적절한 의사를 자동으로 배정하고 그 결과를 저장
    예: "보톡스 100u 이마" → 김의사 배정, "필러 2cc 볼" → 박의사 배정
    """
    __tablename__ = "assignments"
    
    # Primary Key: 배정 고유 ID (자동 증가)
    assignment_id = Column(Integer, primary_key=True, autoincrement=True, comment='배정 고유 ID')
    
    # Foreign Keys: 관련 테이블 참조
    order_treatment_id = Column(Integer, ForeignKey("order_treatments.id"), nullable=False, comment='파싱된 시술 항목 ID (FK)')
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, comment='배정된 의사 사용자 ID')
    
    # 배정 정보
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment='배정 시각 (언제 배정되었는지)')
    
    # Unique Constraint: 한 시술 항목에는 한 명의 의사만 배정 가능
    __table_args__ = (
        UniqueConstraint('order_treatment_id', name='uq_order_treatment'),
    )
    
    # Relationships: 다른 테이블과의 관계 정의
    order_treatment = relationship("OrderTreatment", back_populates="assignment")  # 배정된 시술 항목 정보
    user = relationship("User", back_populates="assignments")  # 배정된 의사 정보 