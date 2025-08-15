from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
import logging
import os
from dotenv import load_dotenv

from database import get_db, create_tables
from models import StoreResponse
from data_service import StoreDataService

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="공공데이터 API로 DB생성 + FastAPI 만들기",
    description="소상공인시장진흥공단 상가(상권)정보를 활용한 FastAPI 서비스",
    version="1.0.0"
)

# 서버 시작시 테이블 생성
@app.on_event("startup")
async def startup_event():
    create_tables()
    logger.info("데이터베이스 테이블이 생성되었습니다.")

@app.get("/")
async def root():
    return {"message": "공공데이터 API로 DB생성 + FastAPI 프로젝트", "docs": "/docs"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "서비스가 정상 작동 중입니다."}

# 1. 행정동 단위 상가업소 조회
@app.get("/storeListInDong")
async def get_store_list_in_dong(
    key: str = Query(..., description="인증키"),
    type: str = Query("json", description="요청파일타입"),
    service: str = Query("storeListInDong", description="서비스명"),
    start_index: int = Query(1, description="요청시작위치"),
    end_index: int = Query(5, description="요청종료위치"),
    divId: str = Query(..., description="행정동코드"),
    db: Session = Depends(get_db)
):
    """행정동 단위 상가업소 조회"""
    try:
        service_obj = StoreDataService(db)
        result = service_obj.get_stores_by_dong(divId, start_index, end_index)
        return {"storeListInDong": {"list_total_count": len(result), "row": result}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2. 단일 상가업소 조회
@app.get("/storeOne")
async def get_store_one(
    key: str = Query(..., description="인증키"),
    type: str = Query("json", description="요청파일타입"),
    service: str = Query("storeOne", description="서비스명"),
    bizesId: str = Query(..., description="상가업소번호"),
    db: Session = Depends(get_db)
):
    """단일 상가업소 조회"""
    try:
        service_obj = StoreDataService(db)
        result = service_obj.get_store_by_bizes_id(bizesId)
        if not result:
            raise HTTPException(status_code=404, detail="상가업소를 찾을 수 없습니다.")
        return {"storeOne": {"list_total_count": 1, "row": [result]}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3. 건물 단위 상가업소 조회
@app.get("/storeListInBuilding")
async def get_store_list_in_building(
    key: str = Query(..., description="인증키"),
    type: str = Query("json", description="요청파일타입"),
    service: str = Query("storeListInBuilding", description="서비스명"),
    start_index: int = Query(1, description="요청시작위치"),
    end_index: int = Query(5, description="요청종료위치"),
    key_value: str = Query(..., description="건물관리번호"),
    db: Session = Depends(get_db)
):
    """건물 단위 상가업소 조회"""
    try:
        service_obj = StoreDataService(db)
        result = service_obj.get_stores_by_building(key_value, start_index, end_index)
        return {"storeListInBuilding": {"list_total_count": len(result), "row": result}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 4. 지번 단위 상가업소 조회
@app.get("/storeListInPnu")
async def get_store_list_in_pnu(
    key: str = Query(..., description="인증키"),
    type: str = Query("json", description="요청파일타입"),
    service: str = Query("storeListInPnu", description="서비스명"),
    start_index: int = Query(1, description="요청시작위치"),
    end_index: int = Query(5, description="요청종료위치"),
    key_value: str = Query(..., description="지번주소"),
    db: Session = Depends(get_db)
):
    """지번 단위 상가업소 조회"""
    try:
        service_obj = StoreDataService(db)
        result = service_obj.get_stores_by_pnu(key_value, start_index, end_index)
        return {"storeListInPnu": {"list_total_count": len(result), "row": result}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 5. 상권 내 상가업소 조회
@app.get("/storeListInArea")
async def get_store_list_in_area(
    key: str = Query(..., description="인증키"),
    type: str = Query("json", description="요청파일타입"),
    service: str = Query("storeListInArea", description="서비스명"),
    start_index: int = Query(1, description="요청시작위치"),
    end_index: int = Query(5, description="요청종료위치"),
    trarNo: str = Query(..., description="상권번호"),
    db: Session = Depends(get_db)
):
    """상권 내 상가업소 조회"""
    try:
        service_obj = StoreDataService(db)
        result = service_obj.get_stores_by_area(trarNo, start_index, end_index)
        return {"storeListInArea": {"list_total_count": len(result), "row": result}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 6. 반경 내 상가업소 조회
@app.get("/storeListInRadius")
async def get_store_list_in_radius(
    key: str = Query(..., description="인증키"),
    type: str = Query("json", description="요청파일타입"),
    service: str = Query("storeListInRadius", description="서비스명"),
    start_index: int = Query(1, description="요청시작위치"),
    end_index: int = Query(5, description="요청종료위치"),
    radius: int = Query(..., description="반경"),
    cx: float = Query(..., description="중심점 X좌표"),
    cy: float = Query(..., description="중심점 Y좌표"),
    db: Session = Depends(get_db)
):
    """반경 내 상가업소 조회"""
    try:
        service_obj = StoreDataService(db)
        result = service_obj.get_stores_by_radius(cx, cy, radius, start_index, end_index)
        return {"storeListInRadius": {"list_total_count": len(result), "row": result}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 7. 사각형 내 상가업소 조회
@app.get("/storeListInRectangle")
async def get_store_list_in_rectangle(
    key: str = Query(..., description="인증키"),
    type: str = Query("json", description="요청파일타입"),
    service: str = Query("storeListInRectangle", description="서비스명"),
    start_index: int = Query(1, description="요청시작위치"),
    end_index: int = Query(5, description="요청종료위치"),
    minx: float = Query(..., description="최소 X좌표"),
    miny: float = Query(..., description="최소 Y좌표"),
    maxx: float = Query(..., description="최대 X좌표"),
    maxy: float = Query(..., description="최대 Y좌표"),
    db: Session = Depends(get_db)
):
    """사각형 내 상가업소 조회"""
    try:
        service_obj = StoreDataService(db)
        result = service_obj.get_stores_by_rectangle(minx, miny, maxx, maxy, start_index, end_index)
        return {"storeListInRectangle": {"list_total_count": len(result), "row": result}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 8. 다각형 내 상가업소 조회
@app.get("/storeListInPolygon")
async def get_store_list_in_polygon(
    key: str = Query(..., description="인증키"),
    type: str = Query("json", description="요청파일타입"),
    service: str = Query("storeListInPolygon", description="서비스명"),
    start_index: int = Query(1, description="요청시작위치"),
    end_index: int = Query(5, description="요청종료위치"),
    coordinates: str = Query(..., description="다각형 좌표"),
    db: Session = Depends(get_db)
):
    """다각형 내 상가업소 조회"""
    try:
        service_obj = StoreDataService(db)
        result = service_obj.get_stores_by_polygon(coordinates, start_index, end_index)
        return {"storeListInPolygon": {"list_total_count": len(result), "row": result}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 9. 업종별 상가업소 조회
@app.get("/storeListInUpjong")
async def get_store_list_in_upjong(
    key: str = Query(..., description="인증키"),
    type: str = Query("json", description="요청파일타입"),
    service: str = Query("storeListInUpjong", description="서비스명"),
    start_index: int = Query(1, description="요청시작위치"),
    end_index: int = Query(5, description="요청종료위치"),
    indsLclsCd: str = Query(..., description="업종대분류코드"),
    indsMclsCd: str = Query(None, description="업종중분류코드"),
    indsSclsCd: str = Query(None, description="업종소분류코드"),
    db: Session = Depends(get_db)
):
    """업종별 상가업소 조회"""
    try:
        service_obj = StoreDataService(db)
        result = service_obj.get_stores_by_upjong(indsLclsCd, indsMclsCd, indsSclsCd, start_index, end_index)
        return {"storeListInUpjong": {"list_total_count": len(result), "row": result}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 10. 수정일자별 상가업소 조회
@app.get("/storeListByDate")
async def get_store_list_by_date(
    key: str = Query(..., description="인증키"),
    type: str = Query("json", description="요청파일타입"),
    service: str = Query("storeListByDate", description="서비스명"),
    start_index: int = Query(1, description="요청시작위치"),
    end_index: int = Query(5, description="요청종료위치"),
    modifiedTime: str = Query(..., description="수정일자"),
    db: Session = Depends(get_db)
):
    """수정일자별 상가업소 조회"""
    try:
        service_obj = StoreDataService(db)
        result = service_obj.get_stores_by_date(modifiedTime, start_index, end_index)
        return {"storeListByDate": {"list_total_count": len(result), "row": result}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 11. 상가업소 변화정보 조회
@app.get("/reqStoreModify")
async def get_store_modify_info(
    key: str = Query(..., description="인증키"),
    type: str = Query("json", description="요청파일타입"),
    service: str = Query("reqStoreModify", description="서비스명"),
    start_index: int = Query(1, description="요청시작위치"),
    end_index: int = Query(5, description="요청종료위치"),
    bizesId: str = Query(..., description="상가업소번호"),
    db: Session = Depends(get_db)
):
    """상가업소 변화정보 조회"""
    try:
        service_obj = StoreDataService(db)
        result = service_obj.get_store_modify_info(bizesId, start_index, end_index)
        return {"reqStoreModify": {"list_total_count": len(result), "row": result}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 12. 상권정보 업종 대분류 조회
@app.get("/largeUpjongList")
async def get_large_upjong_list(
    key: str = Query(..., description="인증키"),
    type: str = Query("json", description="요청파일타입"),
    service: str = Query("largeUpjongList", description="서비스명"),
    start_index: int = Query(1, description="요청시작위치"),
    end_index: int = Query(5, description="요청종료위치"),
    db: Session = Depends(get_db)
):
    """상권정보 업종 대분류 조회"""
    try:
        service_obj = StoreDataService(db)
        result = service_obj.get_large_upjong_list(start_index, end_index)
        return {"largeUpjongList": {"list_total_count": len(result), "row": result}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 13. 상권정보 업종 중분류 조회
@app.get("/middleUpjongList")
async def get_middle_upjong_list(
    key: str = Query(..., description="인증키"),
    type: str = Query("json", description="요청파일타입"),
    service: str = Query("middleUpjongList", description="서비스명"),
    start_index: int = Query(1, description="요청시작위치"),
    end_index: int = Query(5, description="요청종료위치"),
    indsLclsCd: str = Query(..., description="업종대분류코드"),
    db: Session = Depends(get_db)
):
    """상권정보 업종 중분류 조회"""
    try:
        service_obj = StoreDataService(db)
        result = service_obj.get_middle_upjong_list(indsLclsCd, start_index, end_index)
        return {"middleUpjongList": {"list_total_count": len(result), "row": result}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 14. 상권정보 업종 소분류 조회
@app.get("/smallUpjongList")
async def get_small_upjong_list(
    key: str = Query(..., description="인증키"),
    type: str = Query("json", description="요청파일타입"),
    service: str = Query("smallUpjongList", description="서비스명"),
    start_index: int = Query(1, description="요청시작위치"),
    end_index: int = Query(5, description="요청종료위치"),
    indsLclsCd: str = Query(..., description="업종대분류코드"),
    indsMclsCd: str = Query(..., description="업종중분류코드"),
    db: Session = Depends(get_db)
):
    """상권정보 업종 소분류 조회"""
    try:
        service_obj = StoreDataService(db)
        result = service_obj.get_small_upjong_list(indsLclsCd, indsMclsCd, start_index, end_index)
        return {"smallUpjongList": {"list_total_count": len(result), "row": result}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 15. 상권 영역정보 사각형좌표 조회
@app.get("/storeZoneInRectangle")
async def get_store_zone_in_rectangle(
    key: str = Query(..., description="인증키"),
    type: str = Query("json", description="요청파일타입"),
    service: str = Query("storeZoneInRectangle", description="서비스명"),
    start_index: int = Query(1, description="요청시작위치"),
    end_index: int = Query(5, description="요청종료위치"),
    minx: float = Query(..., description="최소 X좌표"),
    miny: float = Query(..., description="최소 Y좌표"),
    maxx: float = Query(..., description="최대 X좌표"),
    maxy: float = Query(..., description="최대 Y좌표"),
    db: Session = Depends(get_db)
):
    """상권 영역정보 사각형좌표 조회"""
    try:
        service_obj = StoreDataService(db)
        result = service_obj.get_store_zone_in_rectangle(minx, miny, maxx, maxy, start_index, end_index)
        return {"storeZoneInRectangle": {"list_total_count": len(result), "row": result}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    
    uvicorn.run("main:app", host=host, port=port, reload=True)