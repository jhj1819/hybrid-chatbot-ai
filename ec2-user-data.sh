#!/bin/bash

# EC2 사용자 데이터 스크립트 (비용 최적화 버전)
# 이 스크립트를 EC2 인스턴스 생성 시 사용자 데이터에 복사

# 시스템 업데이트
yum update -y
yum install -y git python3 python3-pip htop

# Python 3.8 설치 (Amazon Linux 2)
amazon-linux-extras install python3.8 -y
alternatives --set python /usr/bin/python3.8
alternatives --set python3 /usr/bin/python3.8

# 프로젝트 클론
cd /home/ec2-user
git clone https://github.com/jhj1819/hybrid-chatbot-ai.git
cd hybrid-chatbot-ai

# Python 의존성 설치
pip3 install --upgrade pip
pip3 install -r requirements.txt

# 환경 변수 설정
# ⚠️ 주의: 실제 배포 시 OPENAI_API_KEY를 실제 키로 변경해야 합니다!
cat > .env << 'EOF'
# TODO: 아래 값을 실제 OpenAI API 키로 변경하세요
OPENAI_API_KEY=sk-your-actual-openai-api-key-REPLACE-THIS
PORT=8000
PYTHONPATH=/home/ec2-user/hybrid-chatbot-ai
EOF

# systemd 서비스 파일 생성
sudo tee /etc/systemd/system/hybrid-chatbot.service > /dev/null << 'EOF'
[Unit]
Description=Hybrid Chatbot AI Service
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/hybrid-chatbot-ai
Environment=PATH=/usr/bin:/usr/local/bin
EnvironmentFile=/home/ec2-user/hybrid-chatbot-ai/.env
ExecStart=/usr/bin/python3 run_server.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# 서비스 시작
sudo systemctl daemon-reload
sudo systemctl enable hybrid-chatbot
sudo systemctl start hybrid-chatbot

# 로그 확인
sleep 10
sudo systemctl status hybrid-chatbot

# 방화벽 설정 (필요시)
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload

# 완료 메시지
echo "=== 배포 완료 ==="
echo "서비스 상태:"
sudo systemctl status hybrid-chatbot --no-pager
echo ""
echo "로그 확인: sudo journalctl -u hybrid-chatbot -f"
echo "서비스 재시작: sudo systemctl restart hybrid-chatbot"
echo "서비스 중지: sudo systemctl stop hybrid-chatbot"
