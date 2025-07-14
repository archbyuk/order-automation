import pika
import json
import os
import time
from app.services.worker.order_parser import order_parser
from app.services.worker.treatment_parser import parse_treatment_text

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
    
    # 1단계: 주문 텍스트 파싱
    print("\n--- 1단계: 주문 텍스트 파싱 ---")
    success, parsed_order, error_message = order_parser.parse_with_validation(message['raw_text'])
    
    if not success:
        print(f"❌ 파싱 실패: {error_message}")
        print("=== 오더 처리 실패 ===\n")
        return
    
    print(f"✅ 파싱 성공!")
    print(f"   환자 이름: {parsed_order.patient_name}")
    print(f"   차트 번호: {parsed_order.chart_number}")
    print(f"   시술 내용: {parsed_order.treatment}")
    print(f"   방 번호: {parsed_order.room}")
    
    # 8. 2단계: 시술 파싱
    print("\n--- 2단계: 시술 파싱 ---")
    
    # 8-1. 시술 텍스트 파싱 실행
    try:
        parsed_treatments = parse_treatment_text(parsed_order.treatment)
        
        # 8-2. 파싱 결과 확인
        if not parsed_treatments:
            print(f"❌ 시술 파싱 실패: '{parsed_order.treatment}'")
            print("=== 오더 처리 실패 ===\n")
            return
        
        # 8-3. 파싱 성공 시 결과 출력
        print(f"✅ 시술 파싱 성공!")
        print(f" [ 원본 시술: {parsed_order.treatment} ]")
        print(f" [[ 파싱된 시술 수: {len(parsed_treatments)}개 ]]")
        print()
        
        for i, treatment in enumerate(parsed_treatments, 1):
            print(f"- 시술 {i}:")
            print(f"- 시술명: {treatment.name}")
            print(f"- 횟수: {treatment.count}회")
            
            if treatment.round_info:
                print(f"- 회차: {treatment.round_info}")
            if treatment.area_note:
                print(f"- 메모: {treatment.area_note}")
            
            print()  # 각 시술 사이에 빈 줄 추가
        
    except Exception as e:
        print(f"❌ 시술 파싱 중 오류 발생: {e}")
        print("=== 오더 처리 실패 ===\n")
        return
    
    # TODO: 9. 3단계: 의사 배정 알고리즘 추가
    
    # TODO: 10. Slack 전송 로직 추가
    
    # 11. 처리 시간 시뮬레이션 (1초 대기)
    time.sleep(1)
    print("=== 오더 처리 완료 ===\n")

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