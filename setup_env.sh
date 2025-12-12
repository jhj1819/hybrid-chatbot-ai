#!/bin/bash

# 환경 변수 설정 스크립트
echo "🔧 환경 변수를 설정합니다..."

# .env 파일 생성
# ⚠️ 주의: 실제 배포 시 OPENAI_API_KEY를 실제 키로 변경해야 합니다!
cat > .env << 'EOF'
# OpenAI API 키
# TODO: 아래 값을 실제 OpenAI API 키로 변경하세요
OPENAI_API_KEY=sk-your-actual-openai-api-key-REPLACE-THIS

# 서버 설정
PORT=8000
WORKERS=1

# 로그 설정
LOG_LEVEL=info
EOF

echo "✅ .env 파일이 생성되었습니다."
echo "📝 .env 파일을 편집하여 실제 OpenAI API 키를 설정하세요:"
echo "   nano .env"
echo ""
echo "🚀 설정 완료 후 다음 명령어로 서버를 실행하세요:"
echo "   docker-compose up --build"
