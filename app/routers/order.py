from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

# 오더 관련 스키마, 서비스 로직 Import
from app.schemas import order
from app.services.order_received import create_order

# API Router 설정
router = APIRouter()

# 오더 생성 API: create_order service 로직 호출
@router.post("/orders/create", response_model=order.OrderCreateResponse)
def create_order_endpoint(req: order.OrderCreateRequest, db: Session = Depends(get_db)):
    order = create_order(db, req)
    
    return { "order_id": order.order_id, "message": "Order created and queued successfully" }