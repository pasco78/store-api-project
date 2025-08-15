import os
import sys
import subprocess

def main():
    print("공공데이터 API로 DB생성 + FastAPI 프로젝트")
    print("1. 의존성 설치")
    print("2. MariaDB 설정")
    print("3. 서버 실행")
    
    choice = input("선택하세요 (1-3): ").strip()
    
    if choice == "1":
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    elif choice == "2":
        subprocess.run([sys.executable, "setup_mariadb.py"])
    elif choice == "3":
        subprocess.run([sys.executable, "main.py"])
    else:
        print("잘못된 선택입니다.")

if __name__ == "__main__":
    main()