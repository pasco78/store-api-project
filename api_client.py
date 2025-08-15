import requests
import xml.etree.ElementTree as ET
import json
import time
import logging
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class StoreAPIClient:
    """소상공인시장진흥공단 상가(상권)정보 API 클라이언트"""
    
    def __init__(self):
        self.base_url = "http://apis.data.go.kr/B553077/api/open/sdsc2"
        self.service_key = os.getenv("OPEN_API_SERVICE_KEY")
        if not self.service_key:
            raise ValueError("OPEN_API_SERVICE_KEY 환경변수가 설정되지 않았습니다.")
    
    def _make_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """API 요청 실행"""
        url = f"{self.base_url}/{endpoint}"
        params["ServiceKey"] = self.service_key
        params["type"] = "json"  # JSON 형태로 응답 요청
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            # JSON 응답 파싱
            if response.headers.get('content-type', '').startswith('application/json'):
                return response.json()
            else:
                # XML 응답을 JSON으로 변환
                root = ET.fromstring(response.text)
                return self._xml_to_dict(root)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API 요청 실패: {e}")
            return None
        except Exception as e:
            logger.error(f"응답 파싱 실패: {e}")
            return None
    
    def _xml_to_dict(self, element) -> Dict:
        """XML을 딕셔너리로 변환"""
        result = {}
        for child in element:
            if len(child) == 0:
                result[child.tag] = child.text
            else:
                child_dict = self._xml_to_dict(child)
                if child.tag in result:
                    if not isinstance(result[child.tag], list):
                        result[child.tag] = [result[child.tag]]
                    result[child.tag].append(child_dict)
                else:
                    result[child.tag] = child_dict
        return result
    
    def get_stores_by_dong(self, signgu_cd: str, adong_cd: str = None, 
                          page_no: int = 1, num_of_rows: int = 1000) -> Optional[List[Dict]]:
        """행정동 단위 상가업소 조회"""
        params = {
            "divId": "adongCd" if adong_cd else "signguCd",
            "key": adong_cd if adong_cd else signgu_cd,
            "pageNo": page_no,
            "numOfRows": num_of_rows
        }
        
        response = self._make_request("storeListInDong", params)
        if response and "body" in response and "items" in response["body"]:
            items = response["body"]["items"]
            if isinstance(items, list):
                return items
            elif isinstance(items, dict):
                return [items]  # 단일 항목인 경우 리스트로 변환
        return []

# 지역코드 매핑 (일부 예시)
REGION_CODES = {
    "서울특별시": "11",
    "부산광역시": "26", 
    "대구광역시": "27",
    "인천광역시": "28",
    "광주광역시": "29",
    "대전광역시": "30",
    "울산광역시": "31",
    "세종특별자치시": "36",
    "경기도": "41",
    "강원도": "42",
    "충청북도": "43",
    "충청남도": "44",
    "전라북도": "45",
    "전라남도": "46",
    "경상북도": "47",
    "경상남도": "48",
    "제주특별자치도": "50"
}

# 업종코드 매핑 (일부 예시)
INDUSTRY_CODES = {
    "음식": "Q",
    "소매": "F",
    "생활서비스": "G", 
    "숙박": "D",
    "관광여가오락": "R",
    "스포츠": "S",
    "학문교육": "P",
    "부동산": "L"
}