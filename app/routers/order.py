from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

# 오더 관련 스키마, 서비스 로직 Import
from app.schemas import schemas
from app.services.order_received import create_order

# 커스텀 예외 및 검증 로직 Import
from app.exceptions import OrderParsingError, TreatmentParsingError, TreatmentMappingError
from app.services.worker.order_parser import order_parser
from app.services.worker.treatment_parser import treatment_parser
from app.services.worker.treatment_mapper import map_parsed_treatments

# API Router 설정
router = APIRouter()

# 오더 생성 API: create_order service 로직 호출
@router.post("/orders/create", response_model=schemas.OrderCreateResponse)
def create_order_endpoint(req: schemas.OrderCreateRequest, db: Session = Depends(get_db)):
    try:
        # 1단계: 오더 파싱 사전 검증
        success, parsed_order, error_message = order_parser.parse_with_validation(req.order_text)
        if not success:
            raise OrderParsingError(error_message)
        
        # 2단계: 시술 파싱 사전 검증
        parsed_treatments = treatment_parser.parse_treatment_text(parsed_order.treatment)
        if not parsed_treatments:
            raise TreatmentParsingError(f"시술 내용을 파싱할 수 없습니다: '{parsed_order.treatment}'")
        
        # 3단계: 시술 매핑 사전 검증
        mapped_treatments = map_parsed_treatments(
            db=db,
            hospital_id=req.hospital_id,
            parsed_treatments=parsed_treatments
        )
        if not mapped_treatments:
            raise TreatmentMappingError(f"입력한 시술을 찾을 수 없습니다: '{parsed_order.treatment}'")
        
        # 모든 사전 검증 통과 시에만 오더 생성
    order = create_order(db, req)
    
    return { "order_id": order.order_id, "message": "Order created and queued successfully" }
        
    except (OrderParsingError, TreatmentParsingError, TreatmentMappingError):
        # 커스텀 예외는 전역 핸들러에서 600번대 응답으로 자동 변환
        raise