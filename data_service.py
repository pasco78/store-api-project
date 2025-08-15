from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict
from models import Store, StoreCreate, StoreSearch
from api_client import StoreAPIClient
import logging

logger = logging.getLogger(__name__)

class StoreDataService:
    """상가 데이터 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        self.api_client = StoreAPIClient()
    
    def create_store(self, store_data: Dict) -> Store:
        """상가 정보 생성"""
        # 데이터 정제
        store_dict = self._clean_store_data(store_data)
        
        db_store = Store(**store_dict)
        self.db.add(db_store)
        self.db.commit()
        self.db.refresh(db_store)
        return db_store
    
    def get_store_by_id(self, store_id: int) -> Optional[Store]:
        """ID로 상가 조회"""
        return self.db.query(Store).filter(Store.id == store_id).first()
    
    def sync_stores_from_api(self, signgu_cd: str, limit: int = None) -> Dict:
        """API에서 상가 데이터 동기화"""
        logger.info(f"시군구코드 {signgu_cd}의 상가 데이터 동기화 시작")
        
        # API에서 데이터 조회
        stores_data = self.api_client.get_stores_by_dong(signgu_cd)
        
        if limit:
            stores_data = stores_data[:limit]
        
        created_count = 0
        error_count = 0
        
        for store_data in stores_data:
            try:
                bizes_id = store_data.get("bizesId")
                if not bizes_id:
                    error_count += 1
                    continue
                
                # 새로 생성
                self.create_store(store_data)
                created_count += 1
                    
            except Exception as e:
                logger.error(f"상가 데이터 처리 오류: {e}")
                error_count += 1
        
        result = {
            "total_processed": len(stores_data),
            "created": created_count,
            "errors": error_count
        }
        
        return result
    
    def _clean_store_data(self, data: Dict) -> Dict:
        """API 데이터 정제"""
        cleaned = {}
        
        # 문자열 필드 정제
        string_fields = [
            'bizesId', 'bizesNm', 'brtcNm', 'sggNm', 'adongNm', 'bdongNm',
            'lnoAdr', 'rdnmAdr', 'indsLclsCd', 'indsLclsNm', 'indsMclsCd', 
            'indsMclsNm', 'indsSclsCd', 'indsSclsNm', 'bldMngNo', 'bldNm',
            'flrInfo', 'tel', 'ctprvnCd', 'sggCd', 'adongCd', 'bdongCd'
        ]
        
        for field in string_fields:
            value = data.get(field)
            if value and value.strip():
                cleaned[field] = value.strip()[:200]  # 길이 제한
        
        # 숫자 필드 정제
        try:
            if data.get('lon'):
                cleaned['lon'] = float(data['lon'])
        except (ValueError, TypeError):
            pass
            
        try:
            if data.get('lat'):
                cleaned['lat'] = float(data['lat'])
        except (ValueError, TypeError):
            pass
        
        return cleaned
    
    # 새로운 API 엔드포인트 지원 메서드들
    
    def get_stores_by_dong(self, div_id: str, start_index: int = 1, end_index: int = 5) -> List[Dict]:
        """행정동 단위 상가업소 조회"""
        query = self.db.query(Store).filter(Store.adongCd == div_id)
        stores = query.offset(start_index - 1).limit(end_index - start_index + 1).all()
        return [self._store_to_dict(store) for store in stores]
    
    def get_store_by_bizes_id(self, bizes_id: str) -> Optional[Dict]:
        """상가업소번호로 단일 상가업소 조회"""
        store = self.db.query(Store).filter(Store.bizesId == bizes_id).first()
        return self._store_to_dict(store) if store else None
    
    def get_stores_by_building(self, key_value: str, start_index: int = 1, end_index: int = 5) -> List[Dict]:
        """건물 단위 상가업소 조회"""
        query = self.db.query(Store).filter(Store.bldMngNo == key_value)
        stores = query.offset(start_index - 1).limit(end_index - start_index + 1).all()
        return [self._store_to_dict(store) for store in stores]
    
    def get_stores_by_pnu(self, key_value: str, start_index: int = 1, end_index: int = 5) -> List[Dict]:
        """지번 단위 상가업소 조회"""
        query = self.db.query(Store).filter(Store.lnoAdr.like(f"%{key_value}%"))
        stores = query.offset(start_index - 1).limit(end_index - start_index + 1).all()
        return [self._store_to_dict(store) for store in stores]
    
    def get_stores_by_area(self, trar_no: str, start_index: int = 1, end_index: int = 5) -> List[Dict]:
        """상권 내 상가업소 조회"""
        # 상권번호는 추가 테이블이 필요하지만, 임시로 동일 지역 기준으로 조회
        query = self.db.query(Store).filter(Store.sggCd == trar_no[:5])
        stores = query.offset(start_index - 1).limit(end_index - start_index + 1).all()
        return [self._store_to_dict(store) for store in stores]
    
    def get_stores_by_radius(self, cx: float, cy: float, radius: int, start_index: int = 1, end_index: int = 5) -> List[Dict]:
        """반경 내 상가업소 조회"""
        # 간단한 사각형 범위로 근사
        lat_range = radius / 111000  # 위도 1도 ≈ 111km
        lon_range = radius / (111000 * func.cos(func.radians(cy)))
        
        query = self.db.query(Store).filter(
            and_(
                Store.lat.between(cy - lat_range, cy + lat_range),
                Store.lon.between(cx - lon_range, cx + lon_range)
            )
        )
        stores = query.offset(start_index - 1).limit(end_index - start_index + 1).all()
        return [self._store_to_dict(store) for store in stores]
    
    def get_stores_by_rectangle(self, minx: float, miny: float, maxx: float, maxy: float, start_index: int = 1, end_index: int = 5) -> List[Dict]:
        """사각형 내 상가업소 조회"""
        query = self.db.query(Store).filter(
            and_(
                Store.lat.between(miny, maxy),
                Store.lon.between(minx, maxx)
            )
        )
        stores = query.offset(start_index - 1).limit(end_index - start_index + 1).all()
        return [self._store_to_dict(store) for store in stores]
    
    def get_stores_by_polygon(self, coordinates: str, start_index: int = 1, end_index: int = 5) -> List[Dict]:
        """다각형 내 상가업소 조회"""
        # 간단한 구현: 좌표에서 min/max 추출하여 사각형으로 근사
        try:
            coords = [float(x) for x in coordinates.split(',')]
            lons = coords[::2]
            lats = coords[1::2]
            minx, maxx = min(lons), max(lons)
            miny, maxy = min(lats), max(lats)
            return self.get_stores_by_rectangle(minx, miny, maxx, maxy, start_index, end_index)
        except:
            return []
    
    def get_stores_by_upjong(self, inds_lcls_cd: str, inds_mcls_cd: str = None, inds_scls_cd: str = None, start_index: int = 1, end_index: int = 5) -> List[Dict]:
        """업종별 상가업소 조회"""
        filters = [Store.indsLclsCd == inds_lcls_cd]
        
        if inds_mcls_cd:
            filters.append(Store.indsMclsCd == inds_mcls_cd)
        if inds_scls_cd:
            filters.append(Store.indsSclsCd == inds_scls_cd)
        
        query = self.db.query(Store).filter(and_(*filters))
        stores = query.offset(start_index - 1).limit(end_index - start_index + 1).all()
        return [self._store_to_dict(store) for store in stores]
    
    def get_stores_by_date(self, modified_time: str, start_index: int = 1, end_index: int = 5) -> List[Dict]:
        """수정일자별 상가업소 조회"""
        # 날짜 필터링은 created_at 또는 updated_at 필드 기준
        # 여기서는 모든 데이터를 반환하는 것으로 구현
        query = self.db.query(Store)
        stores = query.offset(start_index - 1).limit(end_index - start_index + 1).all()
        return [self._store_to_dict(store) for store in stores]
    
    def get_store_modify_info(self, bizes_id: str, start_index: int = 1, end_index: int = 5) -> List[Dict]:
        """상가업소 변화정보 조회"""
        # 변화정보는 별도 테이블이 필요하지만, 임시로 해당 상가 정보 반환
        store = self.db.query(Store).filter(Store.bizesId == bizes_id).first()
        if store:
            return [self._store_to_dict(store)]
        return []
    
    def get_large_upjong_list(self, start_index: int = 1, end_index: int = 5) -> List[Dict]:
        """상권정보 업종 대분류 조회"""
        query = self.db.query(Store.indsLclsCd, Store.indsLclsNm).distinct()
        results = query.offset(start_index - 1).limit(end_index - start_index + 1).all()
        return [{"indsLclsCd": r[0], "indsLclsNm": r[1]} for r in results if r[0]]
    
    def get_middle_upjong_list(self, inds_lcls_cd: str, start_index: int = 1, end_index: int = 5) -> List[Dict]:
        """상권정보 업종 중분류 조회"""
        query = self.db.query(Store.indsMclsCd, Store.indsMclsNm).filter(
            Store.indsLclsCd == inds_lcls_cd
        ).distinct()
        results = query.offset(start_index - 1).limit(end_index - start_index + 1).all()
        return [{"indsMclsCd": r[0], "indsMclsNm": r[1]} for r in results if r[0]]
    
    def get_small_upjong_list(self, inds_lcls_cd: str, inds_mcls_cd: str, start_index: int = 1, end_index: int = 5) -> List[Dict]:
        """상권정보 업종 소분류 조회"""
        query = self.db.query(Store.indsSclsCd, Store.indsSclsNm).filter(
            and_(
                Store.indsLclsCd == inds_lcls_cd,
                Store.indsMclsCd == inds_mcls_cd
            )
        ).distinct()
        results = query.offset(start_index - 1).limit(end_index - start_index + 1).all()
        return [{"indsSclsCd": r[0], "indsSclsNm": r[1]} for r in results if r[0]]
    
    def get_store_zone_in_rectangle(self, minx: float, miny: float, maxx: float, maxy: float, start_index: int = 1, end_index: int = 5) -> List[Dict]:
        """상권 영역정보 사각형좌표 조회"""
        # 상권 영역 정보는 별도 테이블이 필요하지만, 임시로 해당 지역의 상가 집계 정보 반환
        query = self.db.query(Store.sggCd, Store.sggNm, func.count(Store.id).label('store_count')).filter(
            and_(
                Store.lat.between(miny, maxy),
                Store.lon.between(minx, maxx)
            )
        ).group_by(Store.sggCd, Store.sggNm)
        results = query.offset(start_index - 1).limit(end_index - start_index + 1).all()
        return [{"sggCd": r[0], "sggNm": r[1], "storeCount": r[2]} for r in results]
    
    def _store_to_dict(self, store: Store) -> Dict:
        """Store 객체를 딕셔너리로 변환"""
        if not store:
            return {}
        
        return {
            "bizesId": store.bizesId,
            "bizesNm": store.bizesNm,
            "brtcNm": store.brtcNm,
            "sggNm": store.sggNm,
            "adongNm": store.adongNm,
            "bdongNm": store.bdongNm,
            "lnoAdr": store.lnoAdr,
            "rdnmAdr": store.rdnmAdr,
            "lon": store.lon,
            "lat": store.lat,
            "indsLclsCd": store.indsLclsCd,
            "indsLclsNm": store.indsLclsNm,
            "indsMclsCd": store.indsMclsCd,
            "indsMclsNm": store.indsMclsNm,
            "indsSclsCd": store.indsSclsCd,
            "indsSclsNm": store.indsSclsNm,
            "bldMngNo": store.bldMngNo,
            "bldNm": store.bldNm,
            "flrInfo": store.flrInfo,
            "tel": store.tel,
            "ctprvnCd": store.ctprvnCd,
            "sggCd": store.sggCd,
            "adongCd": store.adongCd,
            "bdongCd": store.bdongCd
        }