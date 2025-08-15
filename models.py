from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

Base = declarative_base()

class Store(Base):
    """상가업소 정보 테이블"""
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    
    # 기본 정보
    bizesId = Column(String(50), unique=True, index=True, comment="상가업소번호")
    bizesNm = Column(String(200), comment="상호명")
    brtcNm = Column(String(50), comment="시도명")
    sggNm = Column(String(50), comment="시군구명")
    adongNm = Column(String(50), comment="행정동명")
    bdongNm = Column(String(50), comment="법정동명")
    lnoAdr = Column(String(500), comment="지번주소")  # MariaDB용 길이 증가
    rdnmAdr = Column(String(500), comment="도로명주소")  # MariaDB용 길이 증가
    
    # 업종 정보
    indsLclsCd = Column(String(10), comment="업종대분류코드")
    indsLclsNm = Column(String(100), comment="업종대분류명")
    indsMclsCd = Column(String(10), comment="업종중분류코드")
    indsMclsNm = Column(String(100), comment="업종중분류명")
    indsSclsCd = Column(String(10), comment="업종소분류코드")
    indsSclsNm = Column(String(100), comment="업종소분류명")
    
    # 위치 정보
    lon = Column(Float, comment="경도")
    lat = Column(Float, comment="위도")
    
    # 건물 정보
    bldMngNo = Column(String(30), comment="건물관리번호")
    bldNm = Column(String(200), comment="건물명")
    flrInfo = Column(String(20), comment="층정보")
    
    # 기타 정보
    tel = Column(String(20), comment="전화번호")
    ctprvnCd = Column(String(10), comment="시도코드")
    sggCd = Column(String(10), comment="시군구코드")
    adongCd = Column(String(10), comment="행정동코드")
    bdongCd = Column(String(10), comment="법정동코드")
    
    # 메타 정보 (MariaDB용 타임존 설정)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # 인덱스 설정
    __table_args__ = (
        Index('idx_store_location', 'brtcNm', 'sggNm', 'adongNm'),
        Index('idx_store_industry', 'indsLclsCd', 'indsMclsCd', 'indsSclsCd'),
        Index('idx_store_coord', 'lat', 'lon'),
        Index('idx_store_bizesnm', 'bizesNm'),  # 상호명 검색용
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}  # MariaDB/MySQL 옵션
    )

# Pydantic 모델들
class StoreBase(BaseModel):
    bizesNm: Optional[str] = None
    brtcNm: Optional[str] = None
    sggNm: Optional[str] = None
    adongNm: Optional[str] = None
    bdongNm: Optional[str] = None
    lnoAdr: Optional[str] = None
    rdnmAdr: Optional[str] = None
    indsLclsCd: Optional[str] = None
    indsLclsNm: Optional[str] = None
    indsMclsCd: Optional[str] = None
    indsMclsNm: Optional[str] = None
    indsSclsCd: Optional[str] = None
    indsSclsNm: Optional[str] = None
    lon: Optional[float] = None
    lat: Optional[float] = None
    bldMngNo: Optional[str] = None
    bldNm: Optional[str] = None
    flrInfo: Optional[str] = None
    tel: Optional[str] = None

class StoreCreate(StoreBase):
    bizesId: str

class StoreResponse(StoreBase):
    id: int
    bizesId: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class StoreSearch(BaseModel):
    brtc_nm: Optional[str] = None
    sgg_nm: Optional[str] = None
    adong_nm: Optional[str] = None
    bizesnm: Optional[str] = None
    inds_lcls_cd: Optional[str] = None
    inds_mcls_cd: Optional[str] = None
    min_lat: Optional[float] = None
    max_lat: Optional[float] = None
    min_lon: Optional[float] = None
    max_lon: Optional[float] = None
    page: int = 1
    size: int = 100