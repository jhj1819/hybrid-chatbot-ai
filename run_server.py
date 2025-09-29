#!/usr/bin/env python3
"""
외부 네트워크에서 접근 가능한 AI 서버 실행 스크립트
"""

import uvicorn
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

if __name__ == "__main__":
    # 서버 설정
    host = "0.0.0.0"  # 모든 네트워크 인터페이스에서 접근 가능
    port = int(os.getenv("PORT", 8000))  # 환경변수에서 포트 읽기, 기본값 8000
    workers = int(os.getenv("WORKERS", 1))  # 워커 프로세스 수
    
    print(f"🚀 AI 서버를 시작합니다...")
    print(f"📍 호스트: {host}")
    print(f"🔌 포트: {port}")
    print(f"👥 워커 수: {workers}")
    print(f"🌐 외부 접근 URL: http://YOUR_IP_ADDRESS:{port}")
    print(f"📖 API 문서: http://YOUR_IP_ADDRESS:{port}/docs")
    print("=" * 50)
    
    # 서버 실행
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        workers=workers,
        reload=False,  # 프로덕션에서는 False로 설정
        log_level="info"
    )

