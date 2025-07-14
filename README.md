# order-automation
# Order Automation 시스템 활성화 가이드

## 시스템 활성화 명령어 순서

### 1. Docker 컨테이너 실행
```bash
docker-compose up -d
```
**설명**: MySQL과 RabbitMQ 컨테이너를 백그라운드에서 실행

### 2. 가상환경 활성화
```bash
source venv/bin/activate
```
**설명**: Python 가상환경을 활성화하여 필요한 패키지들을 사용할 수 있게 함

### 3. API 서버 실행
```bash
uvicorn app.main_api:app --reload
```
**설명**: FastAPI 서버를 실행하여 HTTP 요청을 받을 수 있게 함

### 4. 워커 실행 (새 터미널에서)
```bash
source venv/bin/activate
python app/main_worker.py
```
**설명**: RabbitMQ 큐에서 메시지를 받아 처리하는 워커 프로세스 실행

---

## 시스템 상태 확인 명령어

### Docker 컨테이너 상태 확인
```bash
docker ps
```
**설명**: MySQL과 RabbitMQ 컨테이너가 정상 실행 중인지 확인

### RabbitMQ 포트 확인
```bash
netstat -an | grep 5672
```
**설명**: RabbitMQ가 포트 5672에서 정상적으로 리스닝하고 있는지 확인

### API 서버 상태 확인
```bash
curl -X GET "http://localhost:8000/db-check"
```
**설명**: API 서버와 DB 연결이 정상인지 확인

---

## API 테스트 명령어

### 주문 생성 API 테스트
```bash
curl -X POST "http://localhost:8000/orders" \
  -H "Content-Type: application/json" \
  -d '{"hospital_code": "H123", "order_text": "Test order"}'
```
**설명**: 주문을 생성하고 RabbitMQ 큐에 전송하는 API 테스트

---

## 시스템 종료 명령어

### 워커 종료
```bash
Ctrl + C
```
**설명**: 워커 프로세스 종료

### API 서버 종료
```bash
Ctrl + C
```
**설명**: FastAPI 서버 종료

### Docker 컨테이너 종료
```bash
docker-compose down
```
**설명**: 모든 Docker 컨테이너 종료 및 정리

---

## 주의사항

- API 서버와 워커는 별도의 터미널에서 실행해야 합니다
- Docker 컨테이너가 먼저 실행되어야 API 서버와 워커가 정상 동작합니다
- 가상환경 활성화는 각 터미널에서 별도로 해야 합니다