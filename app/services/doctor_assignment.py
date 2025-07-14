"""
의사 배정 알고리즘 서비스
오더의 시술들을 적절한 의사에게 배정하는 로직을 담당합니다.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, time
import json
from app.models import DoctorProfile, OrderTreatment, HospitalTreatment
from app.schemas.schemas import MappedTreatment

class DoctorAssignmentService:
    """의사 배정 서비스"""
    
    def __init__(self):
        pass
    
    def assign_doctors_to_treatments(
        self, 
        db: Session, 
        hospital_id: int, 
        mapped_treatments: List[MappedTreatment]
    ) -> List[Dict[str, Any]]:
        """
        시술들을 의사에게 배정하는 메인 함수
        
        Args:
            db: 데이터베이스 세션
            hospital_id: 병원 ID
            mapped_treatments: 매핑된 시술 리스트
            
        Returns:
            배정 결과 리스트 (각 시술별 배정된 의사 정보)
        """
        print(f"의사 배정 시작 - 병원 ID: {hospital_id}")
        print(f"배정할 시술 수: {len(mapped_treatments)}개")
        
        assignment_results = []
        
        for i, treatment in enumerate(mapped_treatments, 1):
            print(f"\n--- 시술 {i} 배정 중 ---")
            print(f"   시술 ID: {treatment.treatment_id}")
            print(f"   횟수: {treatment.count}회")
            print(f"   예상 소요시간: {treatment.estimated_minutes}분")
            
            # 1. 해당 시술을 할 수 있는 의사들 조회
            available_doctors = self._get_available_doctors(
                db, hospital_id, treatment.treatment_id
            )
            
            if not available_doctors:
                print(f"해당 시술을 할 수 있는 의사가 없습니다")
                assignment_results.append({
                    "treatment_id": treatment.treatment_id,
                    "assigned_doctor_id": None,
                    "assigned_doctor_name": None,
                    "assignment_success": False,
                    "reason": "해당 시술을 할 수 있는 의사가 없습니다"
                })
                continue
            
            print(f"   ✅ 가능한 의사 수: {len(available_doctors)}명")
            
            # 2. 현재 시간 기준으로 휴무시간이 아닌 의사들 필터링
            active_doctors = self._filter_active_doctors(available_doctors)
            
            if not active_doctors:
                print(f"현재 휴무시간이 아닌 의사가 없습니다")
                assignment_results.append({
                    "treatment_id": treatment.treatment_id,
                    "assigned_doctor_id": None,
                    "assigned_doctor_name": None,
                    "assignment_success": False,
                    "reason": "현재 휴무시간이 아닌 의사가 없습니다"
                })
                continue
            
            print(f"   ✅ 휴무시간이 아닌 의사 수: {len(active_doctors)}명")
            
            # 3. 최적의 의사 선택 (누적 시간이 가장 적은 의사)
            best_doctor = self._select_best_doctor(active_doctors)
            
            if best_doctor:
                print(f"   ✅ 배정된 의사: {best_doctor.name} (누적시간: {best_doctor.total_minutes}분)")
                
                # 4. 의사의 누적 시간 업데이트
                self._update_doctor_total_minutes(db, best_doctor, treatment.estimated_minutes)
                
                assignment_results.append({
                    "treatment_id": treatment.treatment_id,
                    "assigned_doctor_id": best_doctor.user_id,
                    "assigned_doctor_name": best_doctor.name,
                    "assignment_success": True,
                    "reason": "성공적으로 배정됨"
                })
            else:
                print(f"적절한 의사를 찾을 수 없습니다")
                assignment_results.append({
                    "treatment_id": treatment.treatment_id,
                    "assigned_doctor_id": None,
                    "assigned_doctor_name": None,
                    "assignment_success": False,
                    "reason": "적절한 의사를 찾을 수 없습니다"
                })
        
        return assignment_results
    
    def _get_available_doctors(
        self, 
        db: Session, 
        hospital_id: int, 
        treatment_id: int
    ) -> List[DoctorProfile]:
        """해당 시술을 할 수 있는 의사들을 조회"""
        # 1. 해당 병원의 모든 활성 의사 조회
        doctors = (
            db.query(DoctorProfile)
            .filter(
                DoctorProfile.hospital_id == hospital_id,
                DoctorProfile.is_active == True
            )
            .all()
        )
        
        available_doctors = []
        
        for doctor in doctors:
            # 2. qualified_treatment_ids에서 해당 시술 ID 확인
            if self._can_doctor_perform_treatment(doctor, treatment_id):
                available_doctors.append(doctor)
        
        return available_doctors
    
    def _can_doctor_perform_treatment(
        self, 
        doctor: DoctorProfile, 
        treatment_id: int
    ) -> bool:
        """의사가 해당 시술을 할 수 있는지 확인"""
        if not doctor.qualified_treatment_ids:
            return False
        
        try:
            # JSON 문자열을 리스트로 파싱
            qualified_ids = json.loads(doctor.qualified_treatment_ids)
            return treatment_id in qualified_ids
        except (json.JSONDecodeError, TypeError):
            return False
    
    def _filter_active_doctors(self, doctors: List[DoctorProfile]) -> List[DoctorProfile]:
        """현재 휴무시간이 아닌 의사들만 필터링"""
        current_time = datetime.now().time()
        active_doctors = []
        
        for doctor in doctors:
            # 휴무시간이 설정되지 않은 경우
            if not doctor.break_start or not doctor.break_end:
                active_doctors.append(doctor)
                continue
            
            # 현재 시간이 휴무시간에 포함되지 않는 경우
            if not self._is_break_time(current_time, doctor.break_start, doctor.break_end):
                active_doctors.append(doctor)
        
        return active_doctors
    
    def _is_break_time(
        self, 
        current_time: time, 
        break_start: time, 
        break_end: time
    ) -> bool:
        """현재 시간이 휴무시간에 포함되는지 확인"""
        # 자정을 걸치는 휴무시간 처리 (예: 22:00 ~ 02:00)
        if break_start > break_end:
            return current_time >= break_start or current_time <= break_end
        else:
            return break_start <= current_time <= break_end
    
    def _select_best_doctor(self, doctors: List[DoctorProfile]) -> Optional[DoctorProfile]:
        """누적 시간이 가장 적은 의사를 선택"""
        if not doctors:
            return None
        
        # 누적 시간이 가장 적은 의사를 선택
        return min(doctors, key=lambda d: d.total_minutes)
    
    def _update_doctor_total_minutes(
        self, 
        db: Session, 
        doctor: DoctorProfile, 
        additional_minutes: int
    ):
        """의사의 누적 시술시간 업데이트"""
        doctor.total_minutes += additional_minutes
        db.commit()
        print(f"의사 {doctor.name}의 누적시간 업데이트: {doctor.total_minutes}분")


# 전역 인스턴스 생성
doctor_assignment_service = DoctorAssignmentService() 