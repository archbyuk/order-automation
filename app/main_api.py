# 외부에서 요청을 받는 HTTP API 서버
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse

# 데이터베이스 의존성 import
from app.database import get_db

# Router import
from app.routers import order

# 커스텀 예외 및 핸들러 import
from app.exceptions import OrderProcessingError
from app.error_handlers import order_processing_error_handler

app = FastAPI(title="Order Automation API", version="1.0.0")

# 커스텀 예외 핸들러 등록
app.add_exception_handler(OrderProcessingError, order_processing_error_handler)

# Router 등록
app.include_router(order.router, prefix="/api/v1", tags=["orders"])

# 오더 상태 조회 API
@app.get("/api/v1/orders/{order_id}/status")
def get_order_status(order_id: int, db = Depends(get_db)):
    """오더 처리 상태 조회"""
    try:
        # 오더 존재 여부 확인
        from app.models import Order
        order = db.query(Order).filter(Order.order_id == order_id).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="오더를 찾을 수 없습니다")
        
        # 오더 처리 상태 확인 (간단한 예시)
        # 실제로는 더 복잡한 로직이 필요할 수 있음
        return {
            "order_id": order_id,
            "status": "completed",  # 또는 "processing", "failed"
            "message": "오더가 성공적으로 처리되었습니다"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상태 조회 중 오류 발생: {str(e)}")

# DB 연결 확인 API
@app.get("/db-check")
def db_check(db: Depends = Depends(get_db)):
    # MySQL에 쿼리 날림
    result = db.execute("SELECT 1")
    return {"db": [r[0] for r in result]}

@app.get("/health")
def health_check():
    return {"status": "healthy"}