from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.database import get_db
from app.services.log_service import get_log_service

class SchedulerService:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.log_service = get_log_service()
        self._setup_jobs()
    
    def _setup_jobs(self):
        """스케줄 작업 설정"""
        try:
            # 매일 오전 12시에 의사 프로필 리셋
            self.scheduler.add_job(
                func=self._reset_doctor_profiles_job,
                trigger=CronTrigger(hour=0, minute=0),  # 매일 00:00
                id='reset_doctor_profiles',
                name='의사 프로필 리셋',
                replace_existing=True
            )
            
            print("스케줄러 작업 설정 완료")
            print("   - 의사 프로필 리셋: 매일 오전 12시")
            
        except Exception as e:
            print(f"스케줄러 작업 설정 실패: {str(e)}")
    
    def _reset_doctor_profiles_job(self):
        """의사 프로필 리셋 작업 (매일 오전 12시 실행)"""
        print(f"\n🕐 의사 프로필 리셋 작업 시작: {datetime.now()}")
        
        try:
            # DB 세션 생성
            db = next(get_db())
            
            try:
                # 의사 프로필 리셋 실행
                success = self.log_service.reset_doctor_profiles(db)
                
                if success:
                    print(f"의사 프로필 리셋 완료: {datetime.now()}")
                else:
                    print(f"의사 프로필 리셋 실패: {datetime.now()}")
                    
            finally:
                db.close()
                
        except Exception as e:
            print(f"의사 프로필 리셋 작업 중 오류: {str(e)}")
    
    def start(self):
        """스케줄러 시작"""
        try:
            if not self.scheduler.running:
                self.scheduler.start()
                print("스케줄러 시작됨")
                
                # 다음 실행 시간 출력
                next_run = self.scheduler.get_job('reset_doctor_profiles').next_run_time
                print(f"   - 다음 의사 프로필 리셋: {next_run}")
                
            else:
                print("스케줄러가 이미 실행 중입니다")
                
        except Exception as e:
            print(f"스케줄러 시작 실패: {str(e)}")
    
    def stop(self):
        """스케줄러 중지"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                print("스케줄러 중지됨")
            else:
                print("스케줄러가 실행 중이 아닙니다")
                
        except Exception as e:
            print(f"스케줄러 중지 실패: {str(e)}")
    
    
    def get_job_status(self) -> dict:
        """스케줄러 작업 상태 조회"""
        try:
            jobs = []
            for job in self.scheduler.get_jobs():
                jobs.append({
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                    "trigger": str(job.trigger)
                })
            
            return {
                "scheduler_running": self.scheduler.running,
                "jobs": jobs
            }
            
        except Exception as e:
            print(f"스케줄러 상태 조회 실패: {str(e)}")
            return {"scheduler_running": False, "jobs": []}


# 싱글톤 인스턴스
_scheduler_service = None

def get_scheduler_service() -> SchedulerService:
    """ 스케줄러 서비스 싱글톤 인스턴스 반환 """
    global _scheduler_service
    
    if _scheduler_service is None:
        _scheduler_service = SchedulerService()
    
    return _scheduler_service