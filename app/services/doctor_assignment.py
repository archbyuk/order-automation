from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from datetime import datetime, time
import json
import logging
from app.models import DoctorProfile
from app.schemas.schemas import MappedTreatment, DoctorAssignmentResult, DoctorCandidate
from app.exceptions import DoctorAssignmentError, SpecifiedDoctorAssignmentError

# 로깅 설정
logger = logging.getLogger(__name__)

class DoctorAssignmentService:
    """ 의사 배정 알고리즘 """
    
    # ==================== Public Methods ====================
    def assign_doctors_to_treatments(
        self, 
        db: Session, 
        hospital_id: int, 
        mapped_treatments: List[MappedTreatment],
        specified_doctor_name: Optional[str] = None  # 지명 의사 이름 (선택적)
    ) -> List[DoctorAssignmentResult]:
        
        logger.info(f"의사 배정 시작 - 병원 ID: {hospital_id}, 시술 수: {len(mapped_treatments)}, 지명 의사: {specified_doctor_name}")
        
        try:
            # 1. 지명 의사가 있는 경우 해당 의사로 배정 시도
            if specified_doctor_name:
                return self._assign_to_specified_doctor(
                    db, hospital_id, mapped_treatments, specified_doctor_name
                )
            
            # 2. 지명 의사가 없는 경우 기존 자동 배정 로직 사용
            return self._assign_with_auto_selection(db, hospital_id, mapped_treatments)
            
        except (DoctorAssignmentError, SpecifiedDoctorAssignmentError):
            # 커스텀 예외는 그대로 재발생
            raise
        except Exception as e:
            logger.error(f"의사 배정 중 예상치 못한 오류 발생: {e}")
            raise DoctorAssignmentError(f"의사 배정 중 오류가 발생했습니다: {str(e)}")
    
    def _assign_to_specified_doctor(
        self, 
        db: Session, 
        hospital_id: int, 
        mapped_treatments: List[MappedTreatment],
        doctor_name: str
    ) -> List[DoctorAssignmentResult]:
        """지명된 의사에게 배정 시도"""
        logger.info(f"지명 의사 '{doctor_name}'에게 배정 시도")
        
        try:
            # 1. 지명된 의사 조회
            specified_doctor = (
                db.query(DoctorProfile)
                .filter(
                    DoctorProfile.hospital_id == hospital_id,
                    DoctorProfile.name == doctor_name,
                    DoctorProfile.is_active == True
                )
                .first()
            )
            
            if not specified_doctor:
                raise SpecifiedDoctorAssignmentError(f"지명된 의사 '{doctor_name}'을 찾을 수 없습니다")
            
            # 2. 휴무시간 체크
            current_time = datetime.now().time()
            if self._is_doctor_on_break(specified_doctor, current_time):
                raise SpecifiedDoctorAssignmentError(f"지명된 의사 '{doctor_name}'이 휴무시간입니다")
            
            # 3. 가능한 시술 목록 확인
            qualified_treatments = self._parse_qualified_treatments(specified_doctor.qualified_treatment_ids)
            all_treatment_ids = [treatment.treatment_id for treatment in mapped_treatments]
            
            if not all(treatment_id in qualified_treatments for treatment_id in all_treatment_ids):
                raise SpecifiedDoctorAssignmentError(f"지명된 의사 '{doctor_name}'이 모든 시술을 할 수 없습니다")
            
            # 4. 지명된 의사에게 배정
            assignment_results = []
            total_minutes = sum(treatment.estimated_minutes for treatment in mapped_treatments)
            
            try:
                # DB 업데이트
                self._update_doctor_in_database(db, specified_doctor, total_minutes)
                
                # 모든 시술에 대해 배정 결과 생성
                for treatment in mapped_treatments:
                    result = DoctorAssignmentResult(
                        treatment_id=treatment.treatment_id,
                        assigned_doctor_id=specified_doctor.user_id,
                        assigned_doctor_name=specified_doctor.name,
                        assignment_success=True,
                        reason=f"지명된 의사 {specified_doctor.name}에게 배정됨",
                        assignment_score=1.0  # 지명 의사는 최고 점수
                    )
                    assignment_results.append(result)
                
                logger.info(f"지명된 의사 {specified_doctor.name}에게 {len(mapped_treatments)}개 시술 배정 완료 (총 {total_minutes}분)")
                
            except Exception as e:
                logger.error(f"지명 의사 배정 DB 업데이트 실패: {e}")
                raise SpecifiedDoctorAssignmentError(f"DB 업데이트 실패: {str(e)}")
            
            # 5. 배정 결과 로깅
            self._log_assignment_summary(assignment_results)
            
            return assignment_results
            
        except (SpecifiedDoctorAssignmentError):
            # 커스텀 예외는 그대로 재발생
            raise
        except Exception as e:
            logger.error(f"지명 의사 배정 중 예상치 못한 오류 발생: {e}")
            raise SpecifiedDoctorAssignmentError(f"지명 의사 배정 중 오류가 발생했습니다: {str(e)}")
    
    def _assign_with_auto_selection(
        self, 
        db: Session, 
        hospital_id: int, 
        mapped_treatments: List[MappedTreatment]
    ) -> List[DoctorAssignmentResult]:
        """기존 자동 배정 로직"""
        logger.info("자동 의사 배정 시작")
        
            # 1. 의사 후보들을 한 번에 조회 (성능 최적화)
            doctor_candidates = self._get_doctor_candidates(db, hospital_id)
            
            if not doctor_candidates:
            raise DoctorAssignmentError("병원에 배정 가능한 의사가 없습니다")
            
            # 2. 오더의 모든 시술을 할 수 있는 의사 찾기
            all_treatment_ids = [treatment.treatment_id for treatment in mapped_treatments]
            available_candidates = [
                c for c in doctor_candidates 
                if all(treatment_id in c.available_treatments for treatment_id in all_treatment_ids)
            ]
            
            if not available_candidates:
            raise DoctorAssignmentError("오더의 모든 시술을 할 수 있는 의사가 없습니다")
            
            # 3. 최적 의사 선택
            best_candidate = self._select_best_candidate(available_candidates)
            
            if not best_candidate:
            raise DoctorAssignmentError("적절한 의사를 찾을 수 없습니다")
            
            # 4. 선택된 의사에게 모든 시술 배정
            assignment_results = []
            total_minutes = sum(treatment.estimated_minutes for treatment in mapped_treatments)
            
            try:
                # DB 업데이트
                self._update_doctor_in_database(db, best_candidate.doctor, total_minutes)
                
                # 모든 시술에 대해 배정 결과 생성
                for treatment in mapped_treatments:
                    result = DoctorAssignmentResult(
                        treatment_id=treatment.treatment_id,
                        assigned_doctor_id=best_candidate.doctor.user_id,
                        assigned_doctor_name=best_candidate.doctor.name,
                        assignment_success=True,
                    reason=f"자동 배정된 의사 {best_candidate.doctor.name}에게 모든 시술 배정됨",
                        assignment_score=best_candidate.score
                    )
                    assignment_results.append(result)
                
            logger.info(f"자동 배정된 의사 {best_candidate.doctor.name}에게 {len(mapped_treatments)}개 시술 배정 완료 (총 {total_minutes}분)")
                
            except Exception as e:
                logger.error(f"의사 배정 DB 업데이트 실패: {e}")
            raise DoctorAssignmentError(f"DB 업데이트 실패: {str(e)}")
            
            # 5. 배정 결과 로깅
            self._log_assignment_summary(assignment_results)
            
            return assignment_results
    
    
    ###========================================================== ###
    ### ==================== Private Methods ==================== ###
    def _get_doctor_candidates(self, db: Session, hospital_id: int) -> List[DoctorCandidate]:
        """의사 후보들을 효율적으로 조회"""
        current_time = datetime.now().time()
        
        # 1. SQL 쿼리 최적화: 필요한 의사 정보를 한 번에 조회
        doctors = (
            db.query(DoctorProfile)
            .filter(
                DoctorProfile.hospital_id == hospital_id,
                DoctorProfile.is_active == True
            )
            .all()
        )
        
        candidates = []
        
        for doctor in doctors:
            # 2. 휴무시간 체크
            if self._is_doctor_on_break(doctor, current_time):
                continue
            
            # 3. 가능한 시술 목록 파싱 (캐싱 고려)
            available_treatments = self._parse_qualified_treatments(doctor.qualified_treatment_ids)
            
            if not available_treatments:
                continue
            
            # 4. 의사 후보 생성
            candidate = DoctorCandidate(
                doctor=doctor,
                score=self._calculate_doctor_score(doctor),
                available_treatments=available_treatments,
                current_load=doctor.total_minutes
            )
            candidates.append(candidate)
        
        return candidates
    
    def _assign_single_treatment(
        self, 
        treatment: MappedTreatment, 
        candidates: List[DoctorCandidate],
        db: Session
    ) -> DoctorAssignmentResult:
        """단일 시술 배정"""
        # 1. 해당 시술을 할 수 있는 의사들 필터링
        available_candidates = [
            c for c in candidates 
            if treatment.treatment_id in c.available_treatments
        ]
        
        if not available_candidates:
            return DoctorAssignmentResult(
                treatment_id=treatment.treatment_id,
                assigned_doctor_id=None,
                assigned_doctor_name=None,
                assignment_success=False,
                reason="해당 시술을 할 수 있는 의사가 없습니다"
            )
        
        # 2. 배정 전략에 따른 최적 의사 선택
        best_candidate = self._select_best_candidate(available_candidates)
        
        if not best_candidate:
            return DoctorAssignmentResult(
                treatment_id=treatment.treatment_id,
                assigned_doctor_id=None,
                assigned_doctor_name=None,
                assignment_success=False,
                reason="적절한 의사를 찾을 수 없습니다"
            )
        
        # 3. 의사 배정 및 DB 업데이트
        try:
            self._update_doctor_in_database(db, best_candidate.doctor, treatment.estimated_minutes)
            
            return DoctorAssignmentResult(
                treatment_id=treatment.treatment_id,
                assigned_doctor_id=best_candidate.doctor.user_id,
                assigned_doctor_name=best_candidate.doctor.name,
                assignment_success=True,
                reason="성공적으로 배정됨",
                assignment_score=best_candidate.score
            )
            
        except Exception as e:
            logger.error(f"의사 배정 DB 업데이트 실패: {e}")
            return DoctorAssignmentResult(
                treatment_id=treatment.treatment_id,
                assigned_doctor_id=None,
                assigned_doctor_name=None,
                assignment_success=False,
                reason=f"DB 업데이트 실패: {str(e)}"
            )
    
    def _update_doctor_in_database(
        self, 
        db: Session, 
        doctor: DoctorProfile, 
        additional_minutes: int
    ):
        """의사 정보 DB 업데이트 (트랜잭션 안전성 보장)"""
        try:
            # SELECT FOR UPDATE로 동시성 제어
            updated_doctor = (
                db.query(DoctorProfile)
                .filter(DoctorProfile.profile_id == doctor.profile_id)
                .with_for_update()
                .first()
            )
            
            if updated_doctor:
                updated_doctor.total_minutes += additional_minutes
                db.commit()
                logger.info(f"의사 {doctor.name} 누적시간 업데이트: {updated_doctor.total_minutes}분")
            else:
                raise Exception("의사 정보를 찾을 수 없습니다")
                
        except Exception as e:
            db.rollback()
            raise e
    
    def _update_candidate_after_assignment(
        self, 
        doctor_id: int, 
        additional_minutes: int,
        candidates: List[DoctorCandidate]
    ):
        """배정 후 후보 정보 업데이트 (캐시 동기화)"""
        for candidate in candidates:
            if candidate.doctor.user_id == doctor_id:
                candidate.current_load += additional_minutes
                candidate.score = self._calculate_doctor_score(candidate.doctor)
                break
    
    def _create_failed_assignments(
        self, 
        treatments: List[MappedTreatment], 
        reason: str
    ) -> List[DoctorAssignmentResult]:
        """실패한 배정 결과 생성"""
        return [
            DoctorAssignmentResult(
                treatment_id=treatment.treatment_id,
                assigned_doctor_id=None,
                assigned_doctor_name=None,
                assignment_success=False,
                reason=reason
            )
            for treatment in treatments
        ]
    
    def _log_assignment_summary(self, results: List[DoctorAssignmentResult]):
        """배정 결과 요약 로깅"""
        successful = [r for r in results if r.assignment_success]
        failed = [r for r in results if not r.assignment_success]
        
        logger.info(f"배정 완료 - 성공: {len(successful)}개, 실패: {len(failed)}개")
        
        if failed:
            for result in failed:
                logger.warning(f"배정 실패 - 시술 ID {result.treatment_id}: {result.reason}")
    

    ###========================================================= ###
    ### ==================== Helper Methods ==================== ###
    def _is_doctor_on_break(self, doctor: DoctorProfile, current_time: time) -> bool:
        """의사가 휴무시간인지 확인"""
        if not doctor.break_start or not doctor.break_end:
            return False
        
        # 자정을 걸치는 휴무시간 처리
        if doctor.break_start > doctor.break_end:
            return current_time >= doctor.break_start or current_time <= doctor.break_end
        else:
            return doctor.break_start <= current_time <= doctor.break_end
    
    def _parse_qualified_treatments(self, qualified_treatment_ids: Optional[str]) -> List[int]:
        """가능한 시술 목록 파싱 (에러 처리 강화)"""
        if not qualified_treatment_ids:
            return []
        
        try:
            return json.loads(qualified_treatment_ids)
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"시술 목록 파싱 실패: {e}")
            return []
    
    def _calculate_doctor_score(self, doctor: DoctorProfile) -> float:
        """의사 점수 계산 (배정 전략에 따라)"""
        base_score = 100.0
        
        # 누적 시간에 따른 점수 감소 (부하 분산)
        load_penalty = min(doctor.total_minutes / 100, 50.0)  # 최대 50점 감소
        
        return base_score - load_penalty
    
    def _select_best_candidate(self, candidates: List[DoctorCandidate]) -> Optional[DoctorCandidate]:
        """최적 의사 선택 (부하 분산 전략)"""
        if not candidates:
            return None
        
        # 부하 분산: 점수가 가장 높은 의사 선택 (업무량이 적은 의사)
        return max(candidates, key=lambda c: c.score)

# 전역 인스턴스 생성
doctor_assignment_service = DoctorAssignmentService() 