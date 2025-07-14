from sqlalchemy import Column, Integer, String, Boolean, DateTime, Time, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class DoctorProfile(Base):
    """의사 배정을 위한 통합 프로필 정보"""
    __tablename__ = "doctor_profiles"

    profile_id = Column(Integer, primary_key=True, autoincrement=True, comment="프로필 고유 ID")
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, comment="의사 사용자 ID")
    hospital_id = Column(Integer, ForeignKey("hospitals.hospital_id", ondelete="CASCADE"), nullable=False, comment="소속 병원 ID")
    name = Column(String(100), nullable=False, comment="의사 이름")
    is_active = Column(Boolean, nullable=False, default=True, comment="의사 활성화 여부")
    total_minutes = Column(Integer, nullable=False, default=0, comment="총 시술시간(분) - 오늘 누적")
    break_start = Column(Time, nullable=True, comment="휴무 시작 시간 (HH:MM:SS)")
    break_end = Column(Time, nullable=True, comment="휴무 종료 시간 (HH:MM:SS)")
    qualified_treatment_ids = Column(JSON, nullable=True, comment="가능 시술 ID 목록 (JSON 배열)")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="프로필 생성 시각")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="프로필 업데이트 시각")

    # 관계 설정
    user = relationship("User", back_populates="doctor_profile")
    hospital = relationship("Hospital", back_populates="doctor_profiles")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('user_id', name='uq_user_id'),
    )

    def __repr__(self):
        return f"<DoctorProfile(profile_id={self.profile_id}, name='{self.name}', hospital_id={self.hospital_id})>" 