from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime, Date
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Order(Base):
    """
    오더 테이블: 
    
    사용자가 입력한 원문 오더 정보 저장
    병원에서 실제로 입력한 오더의 원본 정보를 그대로 저장
    예: "김환자, 차트번호 12345, 1번실, 보톡스 100u 이마, 필러 2cc 볼"
    """
    __tablename__ = "orders"
    
    # Primary Key: 오더 고유 식별자 (자동 증가)
    order_id = Column(Integer, primary_key=True, autoincrement=True, comment='오더 고유 식별자')
    
    # Foreign Keys: 관련 테이블 참조
    hospital_id = Column(Integer, ForeignKey("hospitals.hospital_id"), nullable=False, comment='오더 소속 병원 ID')
    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=False, comment='오더 작성자 사용자 ID')
    
    # 환자 정보
    patient_name = Column(String(100), nullable=False, comment='환자 이름')
    chart_number = Column(String(50), nullable=False, comment='차트 번호 (환자 고유 식별자)')
    
    # 오더 내용
    raw_text = Column(Text, nullable=False, comment='입력된 오더 원문 전체 텍스트 (파싱 전 원본)')
    room = Column(String(50), nullable=False, comment='시술실 정보 (예: 1번실, VIP실)')
    
    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment='오더 생성 시각')
    
    # Relationships: 다른 테이블과의 관계 정의
    hospital = relationship("Hospital", back_populates="orders")  # 소속 병원 정보
    created_by_user = relationship("User", back_populates="orders")  # 작성자 정보
    order_treatments = relationship("OrderTreatment", back_populates="order")  # 파싱된 시술 목록
    order_logs = relationship("OrderLog", back_populates="order")  # 처리 로그 목록

class OrderTreatment(Base):
    """
    오더 파싱 테이블: 
    
    오더를 개별 단일 시술 단위로 분리하여 저장
    원문 오더를 파싱하여 각각의 시술을 개별적으로 관리
    예: "보톡스 100u 이마" → treatment_id: 1, count: 1, area_note: "이마"
    """
    __tablename__ = "order_treatments"
    
    # Primary Key: 파싱된 단일 시술 항목 ID (자동 증가)
    id = Column(Integer, primary_key=True, autoincrement=True, comment='파싱된 단일 시술 항목 ID')
    
    # Foreign Keys: 관련 테이블 참조
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False, comment='관련 오더 ID (FK)')
    treatment_id = Column(Integer, ForeignKey("treatments.treatment_id"), nullable=False, comment='단일 시술 ID (FK)')
    
    # 파싱된 시술 정보
    count = Column(Integer, default=1, nullable=False, comment='시술 횟수 (예: 보톡스 2개, 필러 1개)')
    round_info = Column(String(50), nullable=True, comment='회차 정보 (예: 1-3회, 2차)')
    area_note = Column(String(200), nullable=True, comment='부위 메모 (예: 턱 부분 민감, 이마 주의)')
    parsed_text = Column(String(500), nullable=True, comment='파싱된 텍스트 원문 일부 (해당 시술 부분만)')
    estimated_minutes = Column(Integer, default=0, nullable=False, comment='계산된 시술 소요 시간(분) - 스케줄링용')
    
    # Relationships
    order = relationship("Order", back_populates="order_treatments")  # 소속 오더 정보
    treatment = relationship("Treatment", back_populates="order_treatments")  # 시술 정보
    assignment = relationship("Assignment", back_populates="order_treatment", uselist=False)  # 배정 정보 (1:1 관계)

class OrderLog(Base):
    """
    오더 처리 로그 테이블: 
    
    파싱, 배정, 전송 등 이벤트 기록용
    오더 처리 과정에서 발생하는 모든 이벤트를 시간순으로 기록
    예: 파싱 성공, 의사 배정 완료, Slack 전송 실패 등
    """
    __tablename__ = "order_logs"
    
    # Primary Key: 로그 고유 ID (자동 증가)
    log_id = Column(Integer, primary_key=True, autoincrement=True, comment='로그 고유 ID')
    
    # Foreign Key: 연결된 오더 ID
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False, comment='연결된 오더 ID (FK)')
    
    # 로그 정보
    event_type = Column(String(100), nullable=False, comment='이벤트 종류 (파싱, 배정, 전송 실패, 완료 등)')
    message = Column(Text, nullable=False, comment='상세 메시지 / 오류 내용 (구체적인 처리 결과)')
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, comment='이벤트 발생 시각')
    
    # Relationships
    order = relationship("Order", back_populates="order_logs")  # 소속 오더 정보 