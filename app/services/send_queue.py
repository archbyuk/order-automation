import pika
import json
import os

# RabbitMQ 큐에 메시지 전송
def send_to_queue(message: dict):
    try:
        # 환경변수에서 RabbitMQ 인증 정보 가져오기 (기본값 없음)
        username = os.getenv("RABBITMQ_USERNAME")
        password = os.getenv("RABBITMQ_PASSWORD")
        
        if not username or not password:
            raise ValueError("RABBITMQ_USERNAME과 RABBITMQ_PASSWORD 환경변수가 설정되어야 합니다.")
        
        credentials = pika.PlainCredentials(username, password)
        
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
        print(f"Failed to send to RabbitMQ: {e}")
        raise