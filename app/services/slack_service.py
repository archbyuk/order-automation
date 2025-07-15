import os
import requests
from typing import Optional
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.services.log_service import get_log_service

# .env 파일 로드
load_dotenv()


class SlackService:
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv('SLACK_WEBHOOK_URL')
    
    def get_hospital_webhook_url(self, hospital_id: int) -> Optional[str]:
        webhook_env_name = f"SLACK_WEBHOOK_HOSPITAL_{hospital_id}"
        webhook_url = os.getenv(webhook_env_name)
        
        if not webhook_url:
            print(f"!!!! {webhook_env_name} 환경변수가 설정되지 않았습니다. 병원 {hospital_id}의 슬랙 알림이 비활성화됩니다.")
            return None
            
        return webhook_url
    
    def send_message(self, message: str, hospital_id: Optional[int] = None) -> bool:
        # 병원별 웹훅 URL 사용
        if hospital_id is not None:
            webhook_url = self.get_hospital_webhook_url(hospital_id)
            
            if not webhook_url:
                print(f"병원 {hospital_id}의 슬랙 웹훅이 설정되지 않아 메시지를 전송하지 않습니다.")
                return False
        else:
            print("병원 ID도 없고 전역 웹훅도 설정되지 않았습니다. 슬랙 메시지를 전송하지 않습니다.")
            return False
            
        try:
            payload = {
                "text": message
            }
            
            response = requests.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"슬랙 메시지 전송 성공 (병원 {hospital_id})")
                return True
            
            else:
                print(f"슬랙 메시지 전송 실패: {response.status_code} - {response.text} (병원 {hospital_id})")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"슬랙 메시지 전송 중 네트워크 오류: {str(e)} (병원 {hospital_id})")
            return False
        
        except Exception as e:
            print(f"슬랙 메시지 전송 중 오류: {str(e)} (병원 {hospital_id})")
            return False
    
    def send_assigned_order(self, order_text: str, assigned_doctor: str, hospital_id: int, order_id: int, db: Session, created_by: int = None) -> bool:
        """
            의사 배정 완료된 오더를 슬랙에 전송하고 로그 저장
            
            Args:
                order_text: 원본 오더 텍스트 (예: "김환자 / 12345 / 보톡스 2개 / 1번실")
                assigned_doctor: 배정된 의사 이름
                hospital_id: 병원 ID
                order_id: 오더 ID
                db: 데이터베이스 세션
                created_by: 오더 생성자 사용자 ID
                
            Returns:
                bool: 전송 성공 여부
        """
        try:
            # 원본 오더 텍스트에 배정된 의사명 추가
            message = f"{order_text} / {assigned_doctor}"
            
            # 슬랙 메시지 전송
            success = self.send_message(message, hospital_id)
            
            # 로그 저장
            log_service = get_log_service()
            log_service.log_slack_notification(
                db=db,
                hospital_id=hospital_id,
                order_id=order_id,
                message=message,
                created_by=created_by,
                success=success
            )
            
            return success
            
        except Exception as e:
            print(f"배정된 오더 전송 실패: {str(e)} (병원 {hospital_id})")
            
            # 실패 로그도 저장
            try:
                log_service = get_log_service()
                log_service.log_slack_notification(
                    db=db,
                    hospital_id=hospital_id,
                    order_id=order_id,
                    message=f"{order_text} / {assigned_doctor}",
                    created_by=created_by,
                    success=False
                )
            except Exception as log_error:
                print(f"로그 저장 실패: {str(log_error)}")
            
            return False


# 싱글톤 인스턴스
_slack_service = None

def get_slack_service() -> SlackService:
    """ 슬랙 서비스 싱글톤 인스턴스 반환 """
    global _slack_service
    
    if _slack_service is None:
        _slack_service = SlackService()
    
    return _slack_service