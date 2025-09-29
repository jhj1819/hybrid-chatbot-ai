#!/bin/bash

# AI 서버 배포 스크립트

echo "🚀 AI 서버 배포를 시작합니다..."

# 1. 시스템 업데이트
echo "📦 시스템 패키지를 업데이트합니다..."
sudo dnf update -y

# 2. Python 및 필수 패키지 설치
echo "🐍 Python 환경을 설정합니다..."
sudo dnf install python3 python3-pip git curl wget unzip -y

# 3. 프로젝트 디렉토리로 이동
cd ~/hybrid-chatbot-ai

# 4. 가상환경 생성 및 활성화
echo "🔧 가상환경을 설정합니다..."
python3 -m venv venv
source venv/bin/activate

# 5. pip 업그레이드 및 의존성 설치
echo "📚 의존성을 설치합니다..."
pip install --upgrade pip
pip install -r requirements.txt

# 6. 환경 변수 파일 확인
if [ ! -f .env ]; then
    echo "⚠️  .env 파일이 없습니다. env.example을 복사하여 설정하세요."
    cp env.example .env
    echo "📝 .env 파일을 편집하여 OpenAI API 키를 설정하세요."
    exit 1
fi

# 7. 서버 실행
echo "🎯 AI 서버를 시작합니다..."
python run_server.py
