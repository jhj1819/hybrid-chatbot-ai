#!/bin/bash

# AI 서버 배포 스크립트

echo "🚀 AI 서버 배포를 시작합니다..."

# 1. 시스템 업데이트
echo "📦 시스템 패키지를 업데이트합니다..."
sudo dnf update -y

# 2. Docker 및 Docker Compose 설치
echo "🐳 Docker를 설치합니다..."
sudo dnf install docker docker-compose git curl wget unzip -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

# 3. 프로젝트 디렉토리로 이동
cd ~/hybrid-chatbot-ai

# 4. 환경 변수 파일 확인 및 생성
if [ ! -f .env ]; then
    echo "⚠️  .env 파일이 없습니다. 생성합니다..."
    cat > .env << 'EOF'
# OpenAI API 키
# ⚠️ 주의: 아래 값을 실제 OpenAI API 키로 변경해야 합니다!
OPENAI_API_KEY=sk-your-actual-openai-api-key-REPLACE-THIS

# 서버 설정
PORT=8000
WORKERS=1

# 로그 설정
LOG_LEVEL=info
EOF
    echo "📝 .env 파일을 편집하여 실제 OpenAI API 키를 설정하세요:"
    echo "   nano .env"
    echo "   또는: export OPENAI_API_KEY='sk-your-actual-key'"
    exit 1
fi

# 5. Docker로 서버 실행
echo "🎯 Docker로 AI 서버를 시작합니다..."
docker-compose up --build -d

echo "✅ 서버가 백그라운드에서 실행 중입니다."
echo "🌐 서버 URL: http://$(curl -s https://api.ipify.org):8000"
echo "📖 API 문서: http://$(curl -s https://api.ipify.org):8000/docs"
echo ""
echo "📋 서버 상태 확인: docker-compose ps"
echo "📋 로그 확인: docker-compose logs -f"
echo "📋 서버 중지: docker-compose down"
