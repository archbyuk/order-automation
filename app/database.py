# sqlalchemy 라이브러리: DB 연결, 모델 정의, 쿼리 실행 등을 위한 파이썬 라이브러리
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 데이터베이스 연결 정보 (반드시 환경변수에서만 읽음)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL 환경변수가 설정되어 있지 않습니다. .env 파일을 확인하세요.")

# SQLAlchemy에서 DB와 연결하는 객체: 미리 만들어둔 연결 재사용
engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True) # pool_pre_ping: 연결 유지 확인

# DB 세션 객체: DB 연결 유지하고 쿼리 실행하는 데 사용 - DB 열고 닫는 함수
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# 모델 선언 시 사용할 Base 클래스
Base = declarative_base()
# 나중에 코드 한 줄로 모델을 정의할 수 있게 해주는 클래스


# FastAPI 의존성 주입을 위한 데이터베이스 세션 함수
def get_db():
    """데이터베이스 세션 의존성 주입"""
    db = SessionLocal()
    try:
        yield db
    
    finally:
        db.close()