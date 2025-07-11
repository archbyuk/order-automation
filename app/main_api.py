# 외부에서 요청을 받는 HTTP API 서버
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pika
import json
import os

app = FastAPI()

# 병원 오더 입력 요청 바디 구조
class OrderRequest(BaseModel):
    hospital_code: str
    order_text: str


# RabbitMQ 연결 함수
def send_to_queue(message: dict):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=os.getenv("RABBITMQ_HOST", "localhost")
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

    message = {
        "hospital_code": req.hospital_code,
        "order_text": req.order_text
    }

    # RabbitMQ 큐에 메시지 전송
    send_to_queue(message)
    
    return {"message": "Order received and queued"}

