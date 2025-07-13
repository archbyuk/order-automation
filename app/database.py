# sqlalchemy 라이브러리: DB 연결, 모델 정의, 쿼리 실행 등을 위한 파이썬 라이브러리
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 데이터베이스 연결 정보
DATABASE_URL = (
    "mysql+pymysql://oa_user:jung04671588!@localhost:3308/oa_clinic_db"
)

# SQLAlchemy에서 DB와 연결하는 객체: 미리 만들어둔 연결 재사용
engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True) # pool_pre_ping: 연결 유지 확인

# DB 세션 객체: DB 연결 유지하고 쿼리 실행하는 데 사용 - DB 열고 닫는 함수
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# 모델 선언 시 사용할 Base 클래스
Base = declarative_base()
# 나중에 코드 한 줄로 모델을 정의할 수 있게 해주는 클래스