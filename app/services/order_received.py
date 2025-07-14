from sqlalchemy.orm import Session
from app.models import Order, Hospital
from app.schemas import schemas
from app.services.send_queue import send_to_queue
from fastapi import HTTPException
import datetime

""" 오더 요청이 들어오면 raw data를 DB에 저장하고 RabbitMQ에 전송하는 서비스 """
def create_order(db: Session, order_request: schemas.OrderCreateRequest):
    try: 
        # 1. 들어온 오더 내 hospital_id와 Hospital 테이블을 비교하여 오더 요청 병원 조회
        hospital = db.query(Hospital).filter(Hospital.hospital_id == order_request.hospital_id).first()

        # 만약 오더 요청이 들어온 병원이 없다면 404 에러 발생
        if not hospital:
            raise HTTPException(status_code=404, detail="Hospital not found")
        
        # 2. 오더 요청이 언제 들어왔는지 현재 시간 저장
        order_created_at = datetime.datetime.now()

        # 3. 요청된 오더 내용을 Order 테이블에 저장
        new_order = Order(
            hospital_id=order_request.hospital_id,
            raw_text=order_request.order_text,
            created_by=order_request.user_id,
            created_at=order_created_at,
        )
        
        db.add(new_order)
        db.flush()  # ID 생성용: 트랜잭션 커밋 전 메모리에 임시 저장
        
        # 4. RabbitMQ 전송용 payload 구성 (필요한 데이터만)
        payload = {
            "order_id": new_order.order_id,
            "hospital_id": new_order.hospital_id,
            "raw_text": new_order.raw_text,
            "created_by": new_order.created_by,
            "created_at": new_order.created_at.isoformat()
        }

        # 5. RabbitMQ 전송
        send_to_queue(payload)
        
        # 6. 모든 작업 성공 시에만 커밋: 트랜잭션 커밋
        db.commit()
        db.refresh(new_order)
        
        return new_order

    except Exception as e:
        db.rollback()
        
        # 만약 메시지 큐에 전송 실패하면 503 에러 발생
        if "RabbitMQ" in str(e) or "queue" in str(e).lower():
            raise HTTPException(status_code=503, detail="메시지 큐 전송 실패. 잠시 후 다시 시도해주세요.")
        
        else:
            raise HTTPException(status_code=500, detail=f"오더 저장 실패: {str(e)}")