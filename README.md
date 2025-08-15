# 📊 공공데이터 API로 DB생성 + FastAPI 만들기

소상공인시장진흥공단 공공데이터 API를 활용하여 상가업소 정보를 수집하고 MariaDB에 저장한 후, FastAPI로 서비스를 제공하는 프로젝트입니다.

## 🚀 빠른 시작

1. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

2. **환경변수 설정**
   ```bash
   # .env.example을 복사하여 .env 파일 생성
   cp .env.example .env
   # 실제 데이터베이스 정보로 수정
   ```

3. **MariaDB 설정**
   ```bash
   python setup_mariadb.py
   ```

4. **서버 실행**
   ```bash
   # FastAPI 서버 실행
   python main.py
   
   # Streamlit 대시보드 실행
   streamlit run dashboard.py
   # 또는
   python run_dashboard.py
   ```

5. **접속**
   - **API 서버**: http://localhost:8000
   - **API 문서**: http://localhost:8000/docs
   - **📊 대시보드**: http://localhost:8501

## 📋 데이터베이스 설정

1. **환경변수 설정**
   - `.env.example` 파일을 복사하여 `.env` 파일 생성
   - 실제 데이터베이스 연결 정보 입력

2. **MariaDB 연결 정보**
   ```env
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_password_here
   DB_NAME=store_db
   ```

⚠️ **보안 주의사항**: 실제 암호는 `.env` 파일에만 저장하고 절대 Git에 커밋하지 마세요!

## 📁 주요 파일
- `main.py`: FastAPI API 서버
- `dashboard.py`: Streamlit 대시보드
- `run_dashboard.py`: 대시보드 실행 스크립트
- `setup_mariadb.py`: 데이터베이스 설정
- `models.py`: 데이터베이스 모델
- `api_client.py`: 공공데이터 API 클라이언트
- `data_service.py`: 비즈니스 로직

## 📊 대시보드 기능

### 🎯 주요 기능
- **📈 요약 통계**: 전체 상가업소, 지역, 업종 수
- **📊 상세 통계**: 업종별/지역별 분포 차트
- **🗺️ 지도 시각화**: 상가업소 위치 표시
- **🔍 검색 기능**: 상가명, 업종, 지역별 필터링

### 📱 사용법
1. **요약 탭**: 전체 현황 한눈에 보기
2. **통계 탭**: 업종별/지역별 상세 분석
3. **지도 탭**: 실제 위치 기반 시각화
4. **검색 탭**: 조건별 상가업소 찾기

## 📡 API 엔드포인트

### 상가업소 조회 API (15개)
1. `GET /storeListInDong` - 행정동 단위 상가업소 조회
2. `GET /storeOne` - 단일 상가업소 조회
3. `GET /storeListInBuilding` - 건물 단위 상가업소 조회
4. `GET /storeListInPnu` - 지번 단위 상가업소 조회
5. `GET /storeListInArea` - 상권 내 상가업소 조회
6. `GET /storeListInRadius` - 반경 내 상가업소 조회
7. `GET /storeListInRectangle` - 사각형 내 상가업소 조회
8. `GET /storeListInPolygon` - 다각형 내 상가업소 조회
9. `GET /storeListInUpjong` - 업종별 상가업소 조회
10. `GET /storeListByDate` - 수정일자별 상가업소 조회
11. `GET /reqStoreModify` - 상가업소 변화정보 조회
12. `GET /largeUpjongList` - 상권정보 업종 대분류 조회
13. `GET /middleUpjongList` - 상권정보 업종 중분류 조회
14. `GET /smallUpjongList` - 상권정보 업종 소분류 조회
15. `GET /storeZoneInRectangle` - 상권 영역정보 사각형좌표 조회

프로젝트 완료! 🎉