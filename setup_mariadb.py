import pymysql
import logging
from database import create_tables

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MariaDB 연결 정보
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'lge123',
    'charset': 'utf8mb4'
}

DATABASE_NAME = 'store_db'

def test_mariadb_connection():
    """MariaDB 연결 테스트"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            logger.info(f"✅ MariaDB 연결 성공! 버전: {version[0]}")
        connection.close()
        return True
    except Exception as e:
        logger.error(f"❌ MariaDB 연결 실패: {e}")
        return False

def create_database():
    """store_db 데이터베이스 생성"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            logger.info(f"✅ 데이터베이스 '{DATABASE_NAME}' 생성 완료!")
        connection.close()
        return True
    except Exception as e:
        logger.error(f"❌ 데이터베이스 생성 실패: {e}")
        return False

def main():
    print("MariaDB 설정 도구")
    if test_mariadb_connection():
        create_database()
        create_tables()
        print("🎉 설정 완료! python main.py로 서버를 시작하세요.")

if __name__ == "__main__":
    main()