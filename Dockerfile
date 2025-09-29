FROM python:3.9-slim

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
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치 (단계별로 설치하여 오류 방지)
COPY requirements.txt .

# pip 업그레이드
RUN pip install --upgrade pip

# 핵심 패키지 먼저 설치
RUN pip install --no-cache-dir fastapi uvicorn openai python-dotenv numpy pydantic requests

# langchain 패키지 설치 (호환 버전)
RUN pip install --no-cache-dir langchain==0.1.0 langchain-openai==0.0.5 langchain-community==0.0.10

# FAISS 설치
RUN pip install --no-cache-dir faiss-cpu==1.12.0

# 앱 코드 복사
COPY . .

# 포트 노출
EXPOSE 8000

# 환경 변수 설정
ENV PYTHONPATH=/app

# 서버 실행
CMD ["python", "run_server.py"]
