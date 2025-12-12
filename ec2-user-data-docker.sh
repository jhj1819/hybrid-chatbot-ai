#!/bin/bash

# EC2 사용자 데이터 스크립트 (Docker 버전)
# Docker를 사용하여 배포하면 Python 버전 문제가 해결됩니다

# 시스템 업데이트
yum update -y

# Docker 설치
yum install -y docker git

# Docker 시작
systemctl start docker
systemctl enable docker
usermod -aG docker ec2-user

# 프로젝트 클론
cd /home/ec2-user
git clone https://github.com/jhj1819/hybrid-chatbot-ai.git
cd hybrid-chatbot-ai

# 환경 변수 설정
# ⚠️ 주의: 실제 배포 시 OPENAI_API_KEY를 실제 키로 변경해야 합니다!
cat > .env << 'EOF'
# TODO: 아래 값을 실제 OpenAI API 키로 변경하세요
OPENAI_API_KEY=sk-your-actual-openai-api-key-REPLACE-THIS
PORT=8000
PYTHONPATH=/app
EOF

# Docker 이미지 빌드
docker build -t hybrid-chatbot-ai .

# Docker 컨테이너 실행
docker run -d \
  --name hybrid-chatbot \
  -p 8000:8000 \
  --env-file .env \
  --restart always \
  hybrid-chatbot-ai

# 완료 메시지
echo "=== Docker 배포 완료 ==="
echo "컨테이너 상태:"
docker ps | grep hybrid-chatbot
echo ""
echo "로그 확인: docker logs -f hybrid-chatbot"
echo "컨테이너 재시작: docker restart hybrid-chatbot"
echo "컨테이너 중지: docker stop hybrid-chatbot"

