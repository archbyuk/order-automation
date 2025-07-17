# [ FastAPI 컨테이너 ]

# 1. 베이스 이미지: Python 3.9 slim 버전
FROM python:3.9-slim

# 2. 환경 변수 설정: .pyc 파일 생성 방지 (개발 환경 최적화), 파이썬 출력 버퍼링 비활성화, 파이썬 모듈 검색 경로 설정
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# 3. 작업 디레곹리 설정: 컨테이너 내부의 작업 디렉토리를 /app으로 설정
WORKDIR /app

# 4. 패키지 설치 (mysql연결 ,health check)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        default-libmysqlclient-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 5. 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 6. 애플리케이션 코드 복사
COPY app/ ./app/
COPY .env* ./

# 7. 보안설정: non-root 사용자 권한 설정
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

# 8. 포트 노출
EXPOSE 8000

# 9. 헬스 체크 설정
HEALTHCHECK --interval=30s \
    --timeout=30s \
    --start-period=5s \
    --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
    

# 10. 애플리케이션 실행
CMD ["uvicorn", "app.main_api:app", "--host", "0.0.0.0", "--port", "8000"]