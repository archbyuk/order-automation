from sqlalchemy.orm import Session
from app.models.doctor_profiles import DoctorProfile
from app.models.system_log import SystemLog, LogType

class LogService:
    # 슬랙 알림 로그 저장
    def log_slack_notification(
            self, 
            db: Session, 
            hospital_id: int, 
            order_id: int, 
            message: str, 
            created_by: int = None,
            success: bool = True
    ) -> bool:
        """
            슬랙 알림 로그 저장
            
            Args:
                db: 데이터베이스 세션
                hospital_id: 병원 ID
                order_id: 오더 ID
                message: 전송된 메시지
                created_by: 로그 생성자 사용자 ID
                success: 전송 성공 여부
                
            Returns:
                bool: 로그 저장 성공 여부
        """
        try:
            # ORM 모델을 사용하여 로그 저장
            log_entry = SystemLog(
                log_type=LogType.SLACK_NOTIFICATION,
                hospital_id=hospital_id,
                created_by=created_by,
                order_id=order_id,
                message=message,
                success=success
            )
            
            db.add(log_entry)
            db.flush()
            db.commit()
            
            print(f"슬랙 알림 로그 저장 성공 (병원 {hospital_id}, 오더 {order_id})")
            return True
            
        except Exception as e:
            db.rollback()
            print(f"슬랙 알림 로그 저장 실패: {str(e)}")
            return False
    
    def log_jandi_notification(
            self, 
            db: Session, 
            hospital_id: int, 
            order_id: int, 
            message: str, 
            created_by: int = None,
            success: bool = True
    ) -> bool:
        """
            잔디 알림 로그 저장
            
            Args:
                db: 데이터베이스 세션
                hospital_id: 병원 ID
                order_id: 오더 ID
                message: 전송된 메시지
                created_by: 로그 생성자 사용자 ID
                success: 전송 성공 여부
                
            Returns:
                bool: 로그 저장 성공 여부
        """
        try:
            # ORM 모델을 사용하여 로그 저장
            log_entry = SystemLog(
                log_type=LogType.JANDI_NOTIFICATION,
                hospital_id=hospital_id,
                created_by=created_by,
                order_id=order_id,
                message=message,
                success=success
            )
            
            db.add(log_entry)
            db.flush()
            db.commit()
            
            print(f"잔디 알림 로그 저장 성공 (병원 {hospital_id}, 오더 {order_id})")
            return True
            
        except Exception as e:
            db.rollback()
            print(f"잔디 알림 로그 저장 실패: {str(e)}")
            return False
    
    def log_doctor_profile_reset(
            self, 
            db: Session, 
            hospital_id: int, 
            doctor_id: int, 
            doctor_name: str, 
            total_minutes: int,
            created_by: int = None
    ) -> bool:
        """
            의사 프로필 리셋 로그 저장
            
            Args:
                db: 데이터베이스 세션
                hospital_id: 병원 ID
                doctor_id: 의사 ID
                doctor_name: 의사 이름
                total_minutes: 리셋 전 총 시술시간
                created_by: 로그 생성자 사용자 ID
                
            Returns:
                bool: 로그 저장 성공 여부
        """
        try:
            message = f"의사 프로필 리셋: {doctor_name} - 총 시술시간 {total_minutes}분"
            
            # ORM 모델을 사용하여 로그 저장
            log_entry = SystemLog(
                log_type=LogType.DOCTOR_PROFILE_RESET,
                hospital_id=hospital_id,
                created_by=created_by,
                doctor_id=doctor_id,
                doctor_name=doctor_name,
                total_minutes=total_minutes,
                message=message,
                success=True
            )
            
            db.add(log_entry)
            db.flush()
            db.commit()
            
            print(f"의사 프로필 리셋 로그 저장 성공: {doctor_name} ({total_minutes}분)")
            return True
            
        except Exception as e:
            db.rollback()
            print(f"의사 프로필 리셋 로그 저장 실패: {str(e)}")
            return False
     
    def reset_doctor_profiles(self, db: Session) -> bool:
        """
            모든 의사의 프로필을 리셋 (매일 오전 12시 실행)
            
            Args:
                db: 데이터베이스 세션
                
            Returns:
                bool: 리셋 성공 여부
        """
        try:
            # 모든 활성 의사 프로필 조회
            doctor_profiles = db.query(DoctorProfile).filter(
                DoctorProfile.is_active == True
            ).all()
            
            reset_count = 0
            
            for profile in doctor_profiles:
                # 리셋 전 로그 저장
                self.log_doctor_profile_reset(
                    db=db,
                    hospital_id=profile.hospital_id,
                    doctor_id=profile.user_id,
                    doctor_name=profile.name,
                    total_minutes=profile.total_minutes
                )
                
                # total_minutes를 0으로 리셋
                profile.total_minutes = 0
                reset_count += 1
            
            db.commit()
            print(f"의사 프로필 리셋 완료: {reset_count}명")
            return True
            
        except Exception as e:
            db.rollback()
            print(f"의사 프로필 리셋 실패: {str(e)}")
            return False
    


    def get_daily_stats(self, db: Session, date: str) -> dict:
        """
            특정 날짜의 시스템 로그 통계 조회
            
            Args:
                db: 데이터베이스 세션
                date: 날짜 (YYYY-MM-DD 형식)
                
            Returns:
                dict: 통계 정보
        """
        try:
            from sqlalchemy import func, and_
            from datetime import datetime
            
            # 날짜 파싱
            target_date = datetime.strptime(date, '%Y-%m-%d').date()
            
            # 슬랙 알림 통계
            slack_stats = db.query(
                func.count(SystemLog.log_id).label('total_count'),
                func.sum(func.case((SystemLog.success == True, 1), else_=0)).label('success_count')
            ).filter(
                and_(
                    SystemLog.log_type == LogType.SLACK_NOTIFICATION,
                    func.date(SystemLog.created_at) == target_date
                )
            ).first()
            
            # 잔디 알림 통계
            jandi_stats = db.query(
                func.count(SystemLog.log_id).label('total_count'),
                func.sum(func.case((SystemLog.success == True, 1), else_=0)).label('success_count')
            ).filter(
                and_(
                    SystemLog.log_type == LogType.JANDI_NOTIFICATION,
                    func.date(SystemLog.created_at) == target_date
                )
            ).first()
            
            # 의사 프로필 리셋 통계
            reset_stats = db.query(
                func.count(SystemLog.log_id).label('reset_count'),
                func.sum(SystemLog.total_minutes).label('total_minutes')
            ).filter(
                and_(
                    SystemLog.log_type == LogType.DOCTOR_PROFILE_RESET,
                    func.date(SystemLog.created_at) == target_date
                )
            ).first()
            
            return {
                "date": date,
                "slack_notifications": {
                    "total": slack_stats.total_count if slack_stats else 0,
                    "success": slack_stats.success_count if slack_stats else 0
                },
                "jandi_notifications": {
                    "total": jandi_stats.total_count if jandi_stats else 0,
                    "success": jandi_stats.success_count if jandi_stats else 0
                },
                "doctor_resets": {
                    "count": reset_stats.reset_count if reset_stats else 0,
                    "total_minutes": reset_stats.total_minutes if reset_stats else 0
                }
            }
            
        except Exception as e:
            print(f"일일 통계 조회 실패: {str(e)}")
            return {}


# 싱글톤 인스턴스
_log_service = None

def get_log_service() -> LogService:
    """ 로그 서비스 싱글톤 인스턴스 반환 """
    global _log_service
    
    if _log_service is None:
        _log_service = LogService()
    
    return _log_service 