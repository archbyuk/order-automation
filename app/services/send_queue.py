import pika
import json
import os

# RabbitMQ 큐에 메시지 전송
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
        print(f"Failed to send to RabbitMQ: {e}")
        raise 