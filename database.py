from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:lge123@127.0.0.1:3306/store_db")

# MariaDB/MySQL 사용시 설정
if DATABASE_URL.startswith("mysql"):
    engine = create_engine(
        DATABASE_URL,
        echo=True,  # SQL 쿼리 로깅
        pool_pre_ping=True,  # 연결 상태 확인
        pool_recycle=3600,   # 1시간마다 연결 재생성
        connect_args={"charset": "utf8mb4"}  # UTF-8 지원
    )
# SQLite 사용시 설정 (백업용)
elif DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=True
    )
else:
    # PostgreSQL 등 기타 DB
    engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """데이터베이스 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """테이블 생성"""
    from models import Base
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """테이블 삭제"""
    from models import Base
    Base.metadata.drop_all(bind=engine)