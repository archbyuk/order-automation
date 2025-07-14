from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import OrderTreatment
from app.schemas.schemas import MappedTreatment, DoctorAssignmentResult

def save_mapped_treatments_with_assignment(
    db: Session, 
    order_id: int, 
    mapped_treatments: List[MappedTreatment],
    assignment_results: List[DoctorAssignmentResult]
):
    """매핑된 시술들을 OrderTreatment 테이블에 저장 (의사 배정 정보 포함)"""
    try:
        # assignment_results를 treatment_id로 인덱싱
        assignment_dict = {
            result.treatment_id: result 
            for result in assignment_results
        }
        
        for item in mapped_treatments:
            # 해당 시술의 배정 정보 가져오기
            assignment = assignment_dict.get(item.treatment_id)
            
            db.add(OrderTreatment(
                order_id=order_id,
                treatment_id=item.treatment_id,
                count=item.count,
                round_info=item.round_info,
                area_note=item.area_note,
                parsed_text=item.parsed_text if hasattr(item, 'parsed_text') else None,
                estimated_minutes=item.estimated_minutes,
                assigned_doctor_id=assignment.assigned_doctor_id if assignment else None,
                assigned_at=db.query(func.now()).scalar() if assignment and assignment.assigned_doctor_id else None
            ))
        
        db.commit()
        print(f"✅ {len(mapped_treatments)}개의 시술이 DB에 저장되었습니다.")
        
        # 배정 결과 요약 출력
        successful_assignments = [r for r in assignment_results if r.assignment_success]
        failed_assignments = [r for r in assignment_results if not r.assignment_success]
        
        print(f"[ 의사 배정 결과 ]:")
        print(f"   ✅ 성공: {len(successful_assignments)}개")
        print(f"   ❌ 실패: {len(failed_assignments)}개")
        
        if failed_assignments:
            print(f"[ 실패 사유 ]:")
            for failed in failed_assignments:
                print(f"      - 시술 ID {failed.treatment_id}: {failed.reason}")
    
    except Exception as e:
        db.rollback()
        print(f"❌ DB 저장 중 오류 발생: {e}")
        raise e

def save_mapped_treatments(db: Session, order_id: int, mapped_treatments: List[MappedTreatment]):
    """매핑된 시술들을 OrderTreatment 테이블에 저장"""
    try:
        for item in mapped_treatments:
            db.add(OrderTreatment(
                order_id=order_id,
                treatment_id=item.treatment_id,
                count=item.count,
                round_info=item.round_info,
                area_note=item.area_note,
                parsed_text=item.parsed_text if hasattr(item, 'parsed_text') else None,
                estimated_minutes=item.estimated_minutes
            ))
        db.commit()
        print(f"✅ {len(mapped_treatments)}개의 시술이 DB에 저장되었습니다.")
    
    except Exception as e:
        db.rollback()
        print(f"DB 저장 중 오류 발생: {e}")
        raise e