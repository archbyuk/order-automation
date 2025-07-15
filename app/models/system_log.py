from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class LogType(enum.Enum):
    SLACK_NOTIFICATION = 'slack_notification'
    JANDI_NOTIFICATION = 'jandi_notification'
    DOCTOR_PROFILE_RESET = 'doctor_profile_reset'

class SystemLog(Base):
    """시스템 로그 테이블"""
    __tablename__ = "system_logs"

    log_id = Column(Integer, primary_key=True, autoincrement=True, comment="로그 고유 ID")
    log_type = Column(Enum(LogType), nullable=False, comment="로그 타입")
    hospital_id = Column(Integer, ForeignKey("hospitals.hospital_id"), nullable=False, comment="병원 ID")
    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=True, comment="로그 생성자 사용자 ID")
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=True, comment="관련 오더 ID")
    doctor_id = Column(Integer, ForeignKey("users.user_id"), nullable=True, comment="관련 의사 ID")
    doctor_name = Column(String(100), nullable=True, comment="의사 이름")
    total_minutes = Column(Integer, nullable=True, comment="총 시술시간(분)")
    message = Column(Text, nullable=False, comment="로그 메시지")
    success = Column(Boolean, nullable=False, default=True, comment="성공 여부")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성 시각")

    # 관계 설정
    hospital = relationship("Hospital")
    created_by_user = relationship("User", foreign_keys=[created_by])
    order = relationship("Order")
    doctor = relationship("User", foreign_keys=[doctor_id])

    def __repr__(self):
        return f"<SystemLog(log_id={self.log_id}, log_type={self.log_type.value}, hospital_id={self.hospital_id})>" 