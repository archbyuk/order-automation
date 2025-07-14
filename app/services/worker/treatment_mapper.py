from typing import List
from sqlalchemy.orm import Session

# db models schemas
from app.models import TreatmentCategory, HospitalTreatment, TreatmentGroup, TreatmentGroupItem
from app.schemas.schemas import ParsedTreatment, MappedTreatment

def map_parsed_treatments(db: Session, hospital_id: int, parsed_treatments: List[ParsedTreatment]) -> List[MappedTreatment]:
    """ 파싱된 시술 리스트를 DB의 실제 단일 시술(treatment_id)로 매핑하여 리턴 (그룹 시술 포함) """
    # 1. 매핑 결과 리스트 초기화
    mapped_results = []

    # 2. 파싱된 parsed_treatments(파싱된 시술 내용) 리스트 순회 
    for parsed in parsed_treatments:
        # 2-1. 단일 시술 매핑 시도
        hospital_treatment = (
            db.query(HospitalTreatment)
            .join(TreatmentCategory)
            .filter(
                HospitalTreatment.hospital_id == hospital_id,
                HospitalTreatment.is_active == True,
                HospitalTreatment.name == parsed.name
            )
            .first()
        )

        # 단일 시술 매핑 성공 시 mapped_results에 추가
        if hospital_treatment:
            mapped_results.append(
                # 매핑된 시술 내용을 MappedTreatment 모델로 반환
                MappedTreatment(
                    treatment_id=hospital_treatment.treatment_id,
                    count=parsed.count,
                    round_info=parsed.round_info,
                    area_note=parsed.area_note,
                    estimated_minutes=hospital_treatment.duration_minutes
                )
            )
            continue 

        # 2-2. 그룹 시술 매핑 시도
        treatment_group = (
            db.query(TreatmentGroup)
            .filter(
                TreatmentGroup.hospital_id == hospital_id,
                TreatmentGroup.group_name == parsed.name,
                TreatmentGroup.is_active == True
            )
            .first()
        )

        # 그룹 시술 매핑 성공 시 mapped_results에 추가
        if treatment_group:
            group_items = (
                db.query(TreatmentGroupItem)
                .filter(TreatmentGroupItem.group_id == treatment_group.group_id)
                .all()
            )
            
            # 그룹 내 각 시술을 개별 시술로 추가
            for item in group_items:
                hospital_treatment = db.query(HospitalTreatment).filter(
                    HospitalTreatment.treatment_id == item.treatment_id
                ).first()
                
                if hospital_treatment:
                    mapped_results.append(
                        MappedTreatment(
                            treatment_id=item.treatment_id,
                            count=item.count * parsed.count,  # 그룹 횟수 * 입력된 횟수
                            round_info=parsed.round_info,
                            area_note=parsed.area_note,
                            estimated_minutes=hospital_treatment.duration_minutes
                        )
                    )

    return mapped_results
