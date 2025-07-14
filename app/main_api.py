# 외부에서 요청을 받는 HTTP API 서버
from fastapi import FastAPI, Depends

# 데이터베이스 의존성 import
from app.database import get_db

# Router import
from app.routers import order

app = FastAPI(title="Order Automation API", version="1.0.0")

# Router 등록
app.include_router(order.router, prefix="/api/v1", tags=["orders"])


# DB 연결 확인 API
@app.get("/db-check")
def db_check(db: Depends = Depends(get_db)):
    # MySQL에 쿼리 날림
    result = db.execute("SELECT 1")
    return {"db": [r[0] for r in result]}

