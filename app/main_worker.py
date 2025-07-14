import pika
import json
import os
import time

# received order data example
"""
    {
        "order_id": 45,
        "hospital_id": "41",
        "raw_text": "박지영 / 67890 / 피부 관리 및 마사지 / 205호",
        "created_by": 80,
        "created_at": "2024-01-15T14:30:25.123456"
    }
"""


# 큐에서 오더 메시지를 실제로 처리하는 함수: 새로운 데이터 구조에 맞게 수정
def process_order(message: dict):
    print("=== 오더 처리 시작 ===")
    print(f"오더 ID: {message['order_id']}")
    print(f"병원 ID: {message['hospital_id']}")
    print(f"생성자 ID: {message['created_by']}")
    print(f"생성 시간: {message['created_at']}")
    print(f"row 오더 텍스트: {message['raw_text']}")
    
    # TODO: 주문 텍스트 파싱 로직 추가
    # 예: "박지영 / 67890 / 피부 관리 및 마사지 / 205호" → 구조화된 데이터로 변환
    
    # TODO: 병원 DB 연결 및 시술 매핑 로직 추가
    
    # TODO: Slack 전송 로직 추가
    
    time.sleep(1)  # 처리 시간 시뮬레이션
    print("=== 주문 처리 완료 ===\n")

# RabbitMQ 큐 서버에 연결 후 order_queue 사용 (api 서버와 동일한 큐)
def main():
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
    
    # docker-compose rabbitmq 접속 인증 정보
    credentials = pika.PlainCredentials('3020467', 'jung04671588!')
    # 연결 설정, host는 localhost고, 인증정보는 내 rabbitmq 정보
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=rabbitmq_host,
        credentials=credentials
    ))
    channel = connection.channel()
    channel.queue_declare(queue='order_queue', durable=True)

    # 큐에서 메시지가 도착하면 자동으로 호출되는 함수
    def callback(ch, method, properties, body):
        try:
            message = json.loads(body)  # 메시지 파싱
            process_order(message)      # 메시지 처리
            ch.basic_ack(delivery_tag=method.delivery_tag) # basic_ack: 메시지 처리 확인 후 큐에서 제거
        
        except Exception as e:
            print(f"Error processing message: {e}")
            # 실패 시 메시지를 버리지 않고 다시 큐에 넣을 수도 있음 (requeue)

    # 한 번에 하나의 메시지만 처리
    channel.basic_qos(prefetch_count=1)
    
    # 큐에서 메시지가 도착하면 callback 함수 호출
    channel.basic_consume(queue='order_queue', on_message_callback=callback)

    print("Waiting for orders... (CTRL+C to stop)")
    
    # 메시지 소비 시작
    try:
        channel.start_consuming() # 대기
    
    except KeyboardInterrupt:
        print("Shutting down worker.")
        channel.stop_consuming()
    
    finally:
        connection.close()

if __name__ == "__main__":
    main()