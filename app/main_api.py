# 외부에서 요청을 받는 HTTP API 서버
from fastapi import FastAPI, HTTPException, Depends
# DB 정보 불러오기
from app.database import SessionLocal
from pydantic import BaseModel
import pika
import json
import os

app = FastAPI()

# DB 세션 의존성 주입
def get_db():
    db = SessionLocal()
    try:
        yield db
    
    finally:
        db.close()


# DB 연결 확인 API
@app.get("/db-check")
def db_check(db: Depends = Depends(get_db)):
    # MySQL에 쿼리 날림
    result = db.execute("SELECT 1")
    return {"db": [r[0] for r in result]}


# 병원 오더 입력 요청 바디 구조
class OrderRequest(BaseModel):
    hospital_code: str
    order_text: str


# RabbitMQ 연결 함수, message type: dict
def send_to_queue(message: dict):
    try:
        # docker-compose rabbitmq 접속 인증 정보
        credentials = pika.PlainCredentials('3020467', 'jung04671588!')
        
        # RabbitMQ 연결 설정
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=os.getenv("RABBITMQ_HOST", "localhost"),
            credentials=credentials
        ))
        
        # RabbitMQ에서 실제로 작업을 수행하는 채널 생성
        channel = connection.channel()
        # order_queue라는 이름의 큐 생성 (만약 기존에 존재하지 않는다면 생성), Durable: 서버 재시작 시 큐 유지 (영속성)
        channel.queue_declare(queue='order_queue', durable=True)

        # 메시지를 큐에 전송: 메시지 속성 설정 (영속성 모드)
        channel.basic_publish(
            exchange='',
            routing_key='order_queue',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)  # 메시지 영속성
        )

        # 메시지 전송 후 연결 종료
        connection.close()
    
    except Exception as e:
        print(f"Failed to send to queue: {e}")
        raise


# /orders: 외부에서 오더 요청을 받는 API 엔드포인트
@app.post("/orders")
async def receive_order(req: OrderRequest):

    # 병원 코드와 오더 텍스트가 비어있는지 확인, 비어있으면 400 에러 반환
    if not req.hospital_code or not req.order_text:
        raise HTTPException(status_code=400, detail="hospital_code and order_text are required")

    # 수신받은 오더 정보를 작업 큐에 전송하기 위한 message 생성
    message = {
        "hospital_code": req.hospital_code,
        "order_text": req.order_text
    }

    # RabbitMQ 큐에 메시지 전송: dict 형태로 전송
    send_to_queue(message)
    
    return {"message": "Order received and queued"}