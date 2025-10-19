FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 설치 (FAISS와 컴파일을 위한 추가 패키지)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    libhdf5-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치 (의존성 충돌 해결)
COPY requirements.txt .

# pip 업그레이드
RUN pip install --upgrade pip

# 핵심 패키지 먼저 설치 (Pydantic 버전 명시)
RUN pip install --no-cache-dir fastapi uvicorn openai python-dotenv numpy pydantic==2.11.9 requests

# langchain 패키지 설치 (최신 안정 버전으로 수정)
RUN pip install --no-cache-dir langchain==0.3.7 langchain-openai==0.2.8 langchain-community==0.3.7

# FAISS 설치
RUN pip install --no-cache-dir faiss-cpu==1.12.0

# 앱 코드 복사
COPY . .

# 포트 노출 (App Runner에서 사용)
EXPOSE 8000

# 환경 변수 설정
ENV PYTHONPATH=/app
ENV PORT=8000

# 비루트 사용자 생성 및 권한 설정 (보안 강화)
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# 서버 실행
CMD ["python", "run_server.py"]