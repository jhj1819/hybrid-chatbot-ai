#!/usr/bin/env python3
"""
외부 네트워크에서 접근 가능한 AI 서버 실행 스크립트
Python 3.9 호환 버전
"""

import uvicorn
import os
import sys
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def get_server_ip():
    """서버의 퍼블릭 IP 주소를 가져옵니다."""
    try:
        import requests
        response = requests.get('https://api.ipify.org', timeout=5)
        return response.text.strip()
    except:
        return "YOUR_IP_ADDRESS"

if __name__ == "__main__":
    # 서버 설정
    host = "0.0.0.0"  # 모든 네트워크 인터페이스에서 접근 가능
    port = int(os.getenv("PORT", 8000))  # 환경변수에서 포트 읽기, 기본값 8000
    workers = int(os.getenv("WORKERS", 1))  # 워커 프로세스 수
    
    # 서버 IP 주소 가져오기
    server_ip = get_server_ip()
    
    print("🚀 AI 서버를 시작합니다...")
    print(f"📍 호스트: {host}")
    print(f"🔌 포트: {port}")
    print(f"👥 워커 수: {workers}")
    print(f"🌐 외부 접근 URL: http://{server_ip}:{port}")
    print(f"📖 API 문서: http://{server_ip}:{port}/docs")
    print("=" * 50)
    
    # 서버 실행
    try:
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            workers=workers,
            reload=False,  # 프로덕션에서는 False로 설정
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 서버를 종료합니다...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 서버 실행 중 오류 발생: {e}")
        sys.exit(1)

