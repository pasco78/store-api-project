#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
완전한 통합 검색 대시보드
- 전체 업종 커버 hierarchical 분류 시스템
- 필터 기반 검색 (검색어 입력 제거)
- AI 챗봇 옵션
- 카드형 결과 + 페이지네이션
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import requests
import json
from datetime import datetime
import time
import math
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 환경 변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="🔍 상가정보 통합 검색",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API 엔드포인트
LLM_API_URL = "http://localhost:8005"

# 데이터베이스 연결
@st.cache_resource
def get_database_connection():
    """데이터베이스 연결 생성"""
    db_host = os.getenv('DB_HOST', '127.0.0.1')
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', 'lge123')
    db_name = os.getenv('DB_NAME', 'store_db')
    
    database_url = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:3306/{db_name}?charset=utf8mb4'
    return create_engine(database_url)

engine = get_database_connection()

# === 실제 데이터베이스 구조에 맞는 업종 분류 시스템 ===
# 실제 DB에는 대분류만 있으므로, 상가명(bizesNm)을 이용한 세부 분류
industry_categories = {
    "음식": {
        "전체": [],  # 음식 전체
        "치킨": ["치킨", "닭", "호프", "통닭", "후라이드", "양념", "BBQ", "교촌", "네네"],
        "카페": ["카페", "커피", "스타벅스", "이디야", "커피빈", "엔젤리너스", "카페베네", "투썸", "Coffee"],
        "한식": ["한식", "한정식", "분식", "국밥", "찌개", "백반", "삼겹살", "갈비", "불고기", "김치", "비빔밥"],
        "중식": ["중식", "중국", "짜장면", "짬뽕", "탕수육", "양장피", "마파두부"],
        "일식": ["일식", "초밥", "라면", "우동", "돈까스", "회", "사시미", "스시"],
        "양식": ["양식", "스테이크", "파스타", "피자", "햄버거", "샐러드", "Pizza"],
        "주점": ["술집", "호프", "포장마차", "노래방", "가라오케", "소주", "맥주", "Bar"],
        "베이커리": ["빵집", "제과", "케이크", "베이커리", "파리바게트", "뚜레주르", "Bakery"],
        "패스트푸드": ["맥도날드", "버거킹", "롯데리아", "KFC", "서브웨이", "McDonald", "Burger"]
    },
    "소매": {
        "전체": [],  # 소매 전체
        "편의점": ["편의점", "CU", "GS25", "세븐일레븐", "이마트24", "미니스톱", "Seven"],
        "마트": ["마트", "슈퍼", "이마트", "롯데마트", "홈플러스", "하나로마트", "Mart", "Super"],
        "의류": ["의류", "패션", "옷", "신발", "가방", "액세서리", "유니클로", "자라", "Fashion"],
        "화장품": ["화장품", "미용", "올리브영", "아모레", "코스메틱", "Beauty"],
        "문구": ["문구", "서점", "교보문고", "영풍문고", "학용품", "Book"],
        "전자제품": ["전자", "핸드폰", "컴퓨터", "가전", "삼성", "LG", "Mobile"],
        "약국": ["약국", "온누리약국", "365약국", "의약품", "Pharmacy"],
        "기타": ["잡화", "생활용품", "가구", "인테리어", "꽃집", "선물"]
    },
    "생활서비스업": {
        "전체": [],  # 생활서비스업 전체
        "미용": ["미용실", "헤어", "네일", "피부", "마사지", "사우나", "찜질방", "Hair", "Beauty"],
        "세탁": ["세탁소", "빨래방", "드라이클리닝", "Laundry"],
        "수리": ["수리", "휴대폰수리", "시계수리", "신발수리", "열쇠", "Repair"],
        "운송": ["택배", "퀵서비스", "이사", "배달", "운송", "Delivery"],
        "청소": ["청소", "하우스클리닝", "사무실청소", "Cleaning"],
        "기타": ["사진관", "인쇄", "복사", "자물쇠", "Photo"]
    },
    "숙박및음식점업": {
        "전체": [],  # 숙박및음식점업 전체
        "숙박": ["호텔", "모텔", "펜션", "게스트하우스", "리조트", "Hotel"],
        "음식점": ["식당", "Restaurant", "레스토랑", "음식점", "요리"],
        "카페": ["카페", "커피", "Coffee", "Cafe"],
        "주점": ["술집", "호프", "Bar", "펍", "Pub"]
    },
    "도매및소매업": {
        "전체": [],  # 도매및소매업 전체
        "도매": ["도매", "총판", "유통", "납품"],
        "소매": ["소매", "판매", "Shop", "Store"],
        "무역": ["수출입", "무역", "통관", "Trade"],
        "기타": ["중간유통", "대리점", "판매대행"]
    },
    "부동산업": {
        "전체": [],  # 부동산업 전체
        "부동산": ["부동산", "공인중개사", "임대", "매매", "Real Estate"],
        "개발": ["건설", "아파트분양", "개발", "Construction"],
        "관리": ["관리사무소", "경비", "시설관리", "Management"],
        "기타": ["감정평가", "컨설팅"]
    },
    "교육": {
        "전체": [],  # 교육 전체
        "학원": ["학원", "교육", "과외", "입시", "Academy"],
        "어학": ["어학원", "영어", "토익", "토플", "회화", "English"],
        "컴퓨터": ["컴퓨터", "IT교육", "프로그래밍", "Computer"],
        "예체능": ["피아노", "미술", "태권도", "발레", "음악", "Art"],
        "기타": ["독서실", "도서관", "스터디룸", "Library"]
    },
    "보건업": {
        "전체": [],  # 보건업 전체
        "병원": ["병원", "의원", "클리닉", "내과", "외과", "Hospital"],
        "치과": ["치과", "임플란트", "교정", "Dental"],
        "한의원": ["한의원", "침술", "한방", "Oriental"],
        "동물병원": ["동물병원", "애완동물", "수의사", "Animal"],
        "기타": ["검진센터", "건강검진", "예방접종"]
    },
    "예술스포츠": {
        "전체": [],  # 예술스포츠 전체
        "스포츠": ["헬스장", "수영장", "골프", "테니스", "Gym", "Sports"],
        "오락": ["노래방", "PC방", "당구장", "볼링장", "Game"],
        "문화": ["영화관", "박물관", "전시관", "문화센터", "Cinema"],
        "기타": ["공원", "VR체험"]
    },
    "하수폐기물": {
        "전체": [],  # 하수폐기물 전체
        "폐기물": ["폐기물", "재활용", "청소", "Waste"],
        "환경": ["환경", "정화", "Environmental"],
        "기타": ["기타"]
    },
    "일반서비스": {
        "전체": [],  # 일반서비스 전체
        "금융": ["은행", "보험", "증권", "대출", "ATM", "농협", "신협", "Bank"],
        "법무": ["변호사", "법무사", "행정사", "공증", "Legal"],
        "회계": ["회계", "세무사", "기장", "Tax"],
        "자동차": ["자동차", "카센터", "타이어", "세차", "주유소", "Car"],
        "기타": ["결혼정보", "장례식장", "웨딩", "Wedding"]
    }
}

# 실제 데이터베이스의 전체 지역 분류 (15개 광역시/도, 139개 구/군) - 단순 리스트 형태
regions = {
    "경기도": ["고양시 일산동구", "광주시", "구리시 교문동", "구리시 갈매동", "구리시 동구동", "구리시 수택동", "구리시 인창동", "군포시 당정동", "군포시 산본동", "김포시", "남양주시 와부읍", "남양주시 진전동", "부천시", "성남시", "수원시"],
    "경상남도": ["거제시", "김해시", "밀양시", "사천시", "양산시", "의령군", "진주시", "창녕군", "통영시", "하동군", "함안시", "창원시", "창원시 마산합포구", "창원시 마산회원구", "창원시 성산구", "창원시 의창구", "창원시 진해구", "진영읍", "하동군", "함안군", "함양군", "합천군"],
    "경상북도": ["경산", "경주시", "구미시", "김천시", "문경시", "상주", "안동시", "영주시", "영천시", "예천군", "울릉군", "울진군", "의성군", "청도군", "청송군", "칠곡", "포항시 남구", "포항시 북구"],
    "광주광역시": ["광산구", "남구", "동구", "북구", "서구"],
    "대구광역시": ["달서구", "중구"],
    "대전광역시": ["대덕구", "동구", "서구", "유성구", "중구"],
    "부산광역시": ["강서구", "금정구", "남구", "동래구", "부산진구", "해운대구"],
    "서울특별시": ["강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구", "금천구", "노원구", "도봉구", "동대문구", "동작구", "마포구"],
    "세종특별자치시": ["세종특별자치시"],
    "울산광역시": ["남구", "동구", "북구", "울주군", "중구"],
    "인천광역시": ["미추홀구", "부평구", "서구", "연수구", "중구", "계양구", "동구"],
    "전라남도": ["고흥군", "곡성군", "광양", "나주", "담양군", "목포시", "무안군", "보성군", "순천시", "신안군", "여수시", "영암군", "완도군", "장성군", "장흥군", "진도군", "함평군", "해남군", "화순군", "영광군"],
    "전라북도특별자치도": ["김제시", "전주시"],
    "충청남도": ["천안시 동남구", "청양군"],
    "충청북도": ["단양군", "보은군", "영동군", "옥천군", "음성군", "제천시", "충주시 상모면", "괴산군"]
}

# 세션 상태 초기화
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "current_page" not in st.session_state:
    st.session_state.current_page = 1
if "items_per_page" not in st.session_state:
    st.session_state.items_per_page = 10
if "popular_searches" not in st.session_state:
    # 인기 검색어와 실제 검색수 (키워드: 검색수)
    st.session_state.popular_searches = [
        ("마트", 7957), ("카페", 7723), ("약국", 5351), ("치킨", 5155),
        ("미용실", 4339), ("병원", 1925), ("세탁소", 1656), ("편의점", 654)
    ]
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "show_ai_chat" not in st.session_state:
    st.session_state.show_ai_chat = True

# 스타일 CSS
st.markdown("""
<style>
    .search-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
        border-left: 4px solid #1f77b4;
    }
    .store-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin: 8px 0;
        border: 1px solid #e9ecef;
    }
    .popular-search-btn {
        margin: 2px;
        padding: 5px 10px;
        background: #e3f2fd;
        border: 1px solid #2196f3;
        border-radius: 15px;
        font-size: 12px;
    }
    .pagination-info {
        text-align: center;
        color: #666;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def search_stores_by_filters(main_category=None, sub_category=None, region=None, sub_region=None, limit=1000):
    """실제 DB 구조에 맞는 필터 기반 상가 검색"""
    try:
        # 기본 쿼리
        query = """
        SELECT bizesId, bizesNm, indsLclsNm, brtcNm, sggNm, adongNm, rdnmAdr, lnoAdr
        FROM stores 
        WHERE 1=1
        """
        params = {}
        
        # 업종 필터 (DB의 indsLclsNm을 직접 사용)
        if main_category and main_category != "전체":
            # 대분류로 먼저 필터링
            query += " AND indsLclsNm = :main_category"
            params['main_category'] = main_category
            
            # 소분류가 있고 "전체"가 아닌 경우, 상가명으로 추가 필터링
            if sub_category and sub_category != "전체":
                keywords = industry_categories.get(main_category, {}).get(sub_category, [])
                if keywords:
                    # 상가명에서 키워드 검색
                    keyword_conditions = " OR ".join([f"bizesNm LIKE :keyword{i}" for i in range(len(keywords))])
                    query += f" AND ({keyword_conditions})"
                    for i, keyword in enumerate(keywords):
                        params[f'keyword{i}'] = f'%{keyword}%'
        
        # 지역 필터
        if region and region != "전체":
            query += " AND brtcNm = :region"
            params['region'] = region
            
            if sub_region and sub_region != "전체":
                query += " AND sggNm = :sub_region"
                params['sub_region'] = sub_region
        
        query += f" ORDER BY bizesNm LIMIT {limit}"
        
        with engine.connect() as conn:
            result = conn.execute(text(query), params)
            return result.fetchall()
            
    except Exception as e:
        logger.error(f"Search error: {e}")
        return []

def display_map_results(results):
    """검색 결과를 지도로 표시"""
    if not results:
        st.warning("지도에 표시할 검색 결과가 없습니다.")
        return
    
    st.markdown(f"**총 {len(results):,}개 업소 위치**")
    
    try:
        # 서울 중심 좌표
        center_lat, center_lng = 37.5665, 126.9780
        
        # Folium 지도 생성
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=11,
            tiles='OpenStreetMap'
        )
        
        # 검색 결과를 지도에 마커로 추가 (최대 100개만)
        display_count = min(100, len(results))
        for i, store in enumerate(results[:display_count]):
            # 임시로 서울 중심 주변에 랜덤 좌표 생성 (실제 좌표가 없는 경우)
            import random
            lat = center_lat + (random.random() - 0.5) * 0.1
            lng = center_lng + (random.random() - 0.5) * 0.1
            
            popup_text = f"""
            <b>{store[1]}</b><br>
            업종: {store[2]}<br>
            지역: {store[3]} {store[4]}<br>
            주소: {store[6] or store[7] or 'N/A'}
            """
            
            folium.Marker(
                location=[lat, lng],
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=store[1],
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
        
        # 지도 표시
        st_folium(m, width=700, height=500)
        
        if len(results) > display_count:
            st.info(f"성능을 위해 처음 {display_count}개 업소만 표시됩니다.")
    
    except Exception as e:
        st.error(f"지도 표시 중 오류가 발생했습니다: {str(e)}")
        st.info("지도 기능을 사용하려면 인터넷 연결을 확인해주세요.")

def display_search_results(results, page=1, items_per_page=10):
    """검색 결과를 카드 형태로 페이지네이션하여 표시"""
    if not results:
        st.warning("검색 결과가 없습니다.")
        return
    
    total_items = len(results)
    total_pages = math.ceil(total_items / items_per_page)
    
    # 페이지네이션 정보
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    page_results = results[start_idx:end_idx]
    
    # 결과 정보 표시
    st.markdown(f"**검색 결과: {total_items:,}개** (페이지 {page}/{total_pages})")
    
    # 3열 레이아웃으로 카드 표시
    cols = st.columns(3)
    for idx, store in enumerate(page_results):
        col_idx = idx % 3
        with cols[col_idx]:
            st.markdown(f"""
            <div class="store-card">
                <h4>{store[1]}</h4>
                <p><strong>업종:</strong> {store[2]}</p>
                <p><strong>위치:</strong> {store[3]} {store[4]} {store[5]}</p>
                <p><strong>주소:</strong> {store[6] or store[7] or 'N/A'}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # 페이지네이션 컨트롤
    if total_pages > 1:
        st.markdown("---")
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
        
        with col1:
            if st.button("⏮️ 처음", disabled=page <= 1):
                st.session_state.current_page = 1
                st.rerun()
        
        with col2:
            if st.button("◀️ 이전", disabled=page <= 1):
                st.session_state.current_page = page - 1
                st.rerun()
        
        with col3:
            # 페이지 선택
            new_page = st.number_input(
                "페이지", 
                min_value=1, 
                max_value=total_pages, 
                value=page, 
                key="page_selector"
            )
            if new_page != page:
                st.session_state.current_page = new_page
                st.rerun()
        
        with col4:
            if st.button("▶️ 다음", disabled=page >= total_pages):
                st.session_state.current_page = page + 1
                st.rerun()
        
        with col5:
            if st.button("⏭️ 마지막", disabled=page >= total_pages):
                st.session_state.current_page = total_pages
                st.rerun()

def chat_with_llm(message, use_llm=True):
    """LLM API와 통신"""
    try:
        response = requests.post(
            f"{LLM_API_URL}/chat",
            json={"message": message, "use_llm": use_llm},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "response": "API 오류가 발생했습니다.",
                "stores": [],
                "llm_used": False,
                "processing_time": 0
            }
    except Exception as e:
        logger.error(f"LLM API error: {e}")
        return {
            "response": f"연결 오류: {str(e)}",
            "stores": [],
            "llm_used": False,
            "processing_time": 0
        }

# 메인 제목을 맨 위에 배치
st.title("🔍 상가업소 통합 검색")
st.markdown("**🔍 상가업소 통합 검색 시스템 v4.0** | 전체 업종 완전 커버")
st.markdown("필터를 활용한 빠른 검색과 AI 챗봇을 제공합니다")

# 입력창과 전송 버튼을 상단에 배치
col1, col2 = st.columns([4, 1])
with col1:
    user_input = st.text_input("", placeholder="강남 치킨집 추천해줘", key="chat_input_top", label_visibility="collapsed")
with col2:
    send_button = st.button("전송", type="primary", use_container_width=True)

# 전송 버튼이 눌리거나 엔터키를 쳤을 때 처리
if send_button and user_input.strip():
    # 사용자 메시지 추가
    st.session_state.chat_messages.append({"role": "user", "content": user_input})
    
    # LLM 응답 생성
    with st.spinner("🤔 생각 중..."):
        result = chat_with_llm(user_input, True)
        
        # 응답 저장
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": result["response"]
        })
    
    # 입력창 클리어를 위해 rerun
    st.rerun()

# 채팅 히스토리 표시 (대화가 있을 때만)
if st.session_state.chat_messages:
    with st.expander("💬 대화 기록", expanded=True):
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

st.markdown("---")

# 상단 컨트롤
col1, col2 = st.columns([3, 1])

with col1:
    # 인기 검색어 - 컴팩트한 레이아웃으로 2행 4열 배치
    st.markdown("**💡 인기 검색어**")
    
    # 1행: 상위 4개
    popular_row1 = st.columns(4)
    for idx, (keyword, count) in enumerate(st.session_state.popular_searches[:4]):
        with popular_row1[idx]:
            if st.button(f"{keyword}\n({count:,}개)", key=f"popular_{idx}", help=f"{keyword} 관련 업체 {count:,}개"):
                # 인기 검색어로 필터 설정
                for main_cat, sub_cats in industry_categories.items():
                    for sub_cat, keywords in sub_cats.items():
                        if keyword in keywords:
                            st.session_state.selected_main_category = main_cat
                            st.session_state.selected_sub_category = sub_cat
                            st.rerun()
    
    # 2행: 하위 4개
    popular_row2 = st.columns(4)
    for idx, (keyword, count) in enumerate(st.session_state.popular_searches[4:8]):
        with popular_row2[idx]:
            if st.button(f"{keyword}\n({count:,}개)", key=f"popular_{idx+4}", help=f"{keyword} 관련 업체 {count:,}개"):
                # 인기 검색어로 필터 설정
                for main_cat, sub_cats in industry_categories.items():
                    for sub_cat, keywords in sub_cats.items():
                        if keyword in keywords:
                            st.session_state.selected_main_category = main_cat
                            st.session_state.selected_sub_category = sub_cat
                            st.rerun()

with col2:
    # 전체 초기화 (챗봇 입력창 + 필터 검색 모두 초기화)
    if st.button("🔄 전체 초기화"):
        # 검색 관련 초기화
        st.session_state.search_results = None
        st.session_state.current_page = 1
        if 'selected_main_category' in st.session_state:
            del st.session_state.selected_main_category
        if 'selected_sub_category' in st.session_state:
            del st.session_state.selected_sub_category
        if 'selected_region' in st.session_state:
            del st.session_state.selected_region
        if 'selected_sub_region' in st.session_state:
            del st.session_state.selected_sub_region
        
        # 챗봇 관련 초기화
        st.session_state.chat_messages = []
        if 'chat_input_top' in st.session_state:
            del st.session_state.chat_input_top
        
        st.success("✅ 모든 검색 기록과 채팅이 초기화되었습니다!")
        st.rerun()

st.markdown("---")


# 메인 검색 섹션
st.header("🔍 필터 검색")

# 필터 설정 - 2행으로 나누어 배치
# 1행: 업종 대분류, 업종 소분류, 검색 버튼
filter_row1_col1, filter_row1_col2, filter_row1_col3 = st.columns(3)

with filter_row1_col1:
    # 업종 대분류
    main_categories = ["전체"] + list(industry_categories.keys())
    selected_main_category = st.selectbox(
        "업종 대분류",
        main_categories,
        index=main_categories.index(st.session_state.get('selected_main_category', '전체')) if st.session_state.get('selected_main_category', '전체') in main_categories else 0
    )

with filter_row1_col2:
    # 업종 소분류
    if selected_main_category and selected_main_category != "전체":
        sub_categories = ["전체"] + list(industry_categories[selected_main_category].keys())
    else:
        sub_categories = ["전체"]
    
    selected_sub_category = st.selectbox(
        "업종 소분류",
        sub_categories,
        index=sub_categories.index(st.session_state.get('selected_sub_category', '전체')) if st.session_state.get('selected_sub_category', '전체') in sub_categories else 0
    )

with filter_row1_col3:
    # 검색 버튼을 1행에 배치하고 위쪽 여백을 추가
    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
    search_clicked = st.button("🔍 검색", type="primary", use_container_width=True)

# 2행: 지역 (도/시), 세부 지역 (구/군)
filter_row2_col1, filter_row2_col2, filter_row2_col3 = st.columns(3)

with filter_row2_col1:
    # 지역 (도/시)
    region_list = ["전체"] + list(regions.keys())
    selected_region = st.selectbox(
        "지역 (도/시)",
        region_list,
        index=region_list.index(st.session_state.get('selected_region', '전체')) if st.session_state.get('selected_region', '전체') in region_list else 0
    )

with filter_row2_col2:
    # 세부 지역 (구/군)
    if selected_region and selected_region != "전체" and selected_region in regions:
        sub_regions = ["전체"] + regions[selected_region]  # 단순 리스트 구조
    else:
        sub_regions = ["전체"]
    
    selected_sub_region = st.selectbox(
        "세부 지역 (구/군)",
        sub_regions,
        index=sub_regions.index(st.session_state.get('selected_sub_region', '전체')) if st.session_state.get('selected_sub_region', '전체') in sub_regions else 0
    )

with filter_row2_col3:
    # 빈 공간 (균형을 위해)
    st.empty()

# 검색 실행
if search_clicked or (selected_main_category != "전체" or selected_region != "전체"):
    # 세션 상태 업데이트
    st.session_state.selected_main_category = selected_main_category
    st.session_state.selected_sub_category = selected_sub_category
    st.session_state.selected_region = selected_region
    st.session_state.selected_sub_region = selected_sub_region
    st.session_state.current_page = 1  # 새 검색시 첫 페이지로
    
    # 검색 실행
    with st.spinner("검색 중..."):
        results = search_stores_by_filters(
            main_category=selected_main_category,
            sub_category=selected_sub_category,
            region=selected_region,
            sub_region=selected_sub_region
        )
        st.session_state.search_results = results

# 검색 결과 표시
if st.session_state.search_results is not None:
    st.markdown("---")
    st.header("📋 검색 결과")
    
    # 결과 표시 방식 선택
    result_tabs = st.tabs(["📋 목록 보기", "🗺️ 지도 보기"])
    
    with result_tabs[0]:
        display_search_results(
            st.session_state.search_results, 
            page=st.session_state.current_page,
            items_per_page=st.session_state.items_per_page
        )
    
    with result_tabs[1]:
        display_map_results(st.session_state.search_results)

# 사이드바
with st.sidebar:
    st.header("ℹ️ 검색 도움말")
    
    # 업종 분류 안내
    with st.expander("📋 업종 분류", expanded=False):
        for main_cat, sub_cats in list(industry_categories.items())[:3]:  # 처음 3개만 표시
            st.markdown(f"**{main_cat}**")
            for sub_cat in list(sub_cats.keys())[:3]:  # 각 대분류의 처음 3개만
                st.markdown(f"  - {sub_cat}")
        st.markdown("*... 및 기타 모든 업종*")
    
    # 지역 분류 안내
    with st.expander("🗺️ 지역 분류", expanded=False):
        for region, districts in list(regions.items())[:3]:  # 처음 3개 지역만 표시
            st.markdown(f"**{region}**")
            for district in districts[:3]:  # 각 지역의 처음 3개 구/군만
                st.markdown(f"  - {district}")
        st.markdown("*... 및 기타 모든 지역*")
    
    # 시스템 정보
    st.divider()
    st.subheader("🔧 시스템 정보")
    
    # DB 연결 상태
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        st.success("✅ 데이터베이스 연결")
    except:
        st.error("❌ 데이터베이스 오류")
    
    # LLM API 상태
    try:
        health = requests.get(f"{LLM_API_URL}/health", timeout=2)
        if health.status_code == 200:
            st.success("✅ AI 챗봇 활성")
        else:
            st.warning("⚠️ AI 챗봇 오류")
    except:
        st.error("❌ AI 챗봇 오프라인")

# 푸터
st.markdown("---")
st.caption("Powered by Streamlit & LLM | 실시간 데이터 분석")