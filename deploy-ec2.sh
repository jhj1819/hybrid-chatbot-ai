#!/bin/bash

# EC2 비용 최적화 배포 스크립트
# 사용법: ./deploy-ec2.sh <AWS_REGION> <KEY_PAIR_NAME>

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 함수 정의
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${BLUE}[SUCCESS]${NC} $1"
}

# 매개변수 확인
if [ $# -ne 2 ]; then
    print_error "사용법: $0 <AWS_REGION> <KEY_PAIR_NAME>"
    print_error "예시: $0 ap-northeast-2 my-key-pair"
    exit 1
fi

AWS_REGION=$1
KEY_PAIR_NAME=$2
INSTANCE_TYPE="t2.micro"  # 최대 비용 절약
SECURITY_GROUP_NAME="hybrid-chatbot-sg"
INSTANCE_NAME="hybrid-chatbot-ai"

print_info "EC2 비용 최적화 배포를 시작합니다..."
print_info "AWS Region: $AWS_REGION"
print_info "Key Pair: $KEY_PAIR_NAME"
print_info "Instance Type: $INSTANCE_TYPE (비용 최적화)"

# 보안 그룹 생성
print_info "보안 그룹을 생성합니다..."
SECURITY_GROUP_ID=$(aws ec2 create-security-group \
    --group-name $SECURITY_GROUP_NAME \
    --description "Security group for hybrid chatbot AI" \
    --region $AWS_REGION \
    --query 'GroupId' \
    --output text 2>/dev/null || \
    aws ec2 describe-security-groups \
    --group-names $SECURITY_GROUP_NAME \
    --region $AWS_REGION \
    --query 'SecurityGroups[0].GroupId' \
    --output text)

print_success "보안 그룹 ID: $SECURITY_GROUP_ID"

# 보안 그룹 규칙 추가
print_info "보안 그룹 규칙을 설정합니다..."
aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0 \
    --region $AWS_REGION 2>/dev/null || true

aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp \
    --port 8000 \
    --cidr 0.0.0.0/0 \
    --region $AWS_REGION 2>/dev/null || true

# 사용자 데이터 스크립트 생성
print_info "사용자 데이터 스크립트를 생성합니다..."
cat > user-data.sh << 'EOF'
#!/bin/bash
yum update -y
yum install -y git python3 python3-pip

# Python 3.12 설치 (Amazon Linux 2)
amazon-linux-extras install python3.8 -y
alternatives --set python /usr/bin/python3.8

# 프로젝트 클론
cd /home/ec2-user
git clone https://github.com/jhj1819/hybrid-chatbot-ai.git
cd hybrid-chatbot-ai

# Python 의존성 설치
pip3 install -r requirements.txt

# 환경 변수 설정
# ⚠️ 주의: 실제 배포 시 OPENAI_API_KEY를 실제 키로 변경해야 합니다!
cat > .env << 'ENVEOF'
# TODO: 아래 값을 실제 OpenAI API 키로 변경하세요
OPENAI_API_KEY=sk-your-actual-openai-api-key-REPLACE-THIS
PORT=8000
PYTHONPATH=/home/ec2-user/hybrid-chatbot-ai
ENVEOF

# 서비스 파일 생성
sudo tee /etc/systemd/system/hybrid-chatbot.service > /dev/null << 'SERVICEEOF'
[Unit]
Description=Hybrid Chatbot AI Service
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/hybrid-chatbot-ai
Environment=PATH=/usr/bin:/usr/local/bin
ExecStart=/usr/bin/python3 run_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICEEOF

# 서비스 시작
sudo systemctl daemon-reload
sudo systemctl enable hybrid-chatbot
sudo systemctl start hybrid-chatbot

# 로그 확인
sleep 10
sudo systemctl status hybrid-chatbot
EOF

# EC2 인스턴스 생성 (스팟 인스턴스로 비용 절약)
print_info "EC2 인스턴스를 생성합니다 (스팟 인스턴스로 비용 절약)..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id ami-0c02fb55956c7d316 \
    --count 1 \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_PAIR_NAME \
    --security-group-ids $SECURITY_GROUP_ID \
    --user-data file://user-data.sh \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}]" \
    --region $AWS_REGION \
    --query 'Instances[0].InstanceId' \
    --output text)

print_success "인스턴스 ID: $INSTANCE_ID"

# 인스턴스 시작 대기
print_info "인스턴스가 시작될 때까지 대기합니다..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region $AWS_REGION

# 퍼블릭 IP 가져오기
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --region $AWS_REGION \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

print_success "배포 완료!"
print_success "퍼블릭 IP: $PUBLIC_IP"
print_success "서비스 URL: http://$PUBLIC_IP:8000"
print_success "API 문서: http://$PUBLIC_IP:8000/docs"
print_success ""
print_success "비용 최적화 설정:"
print_success "- 인스턴스 타입: $INSTANCE_TYPE (월 $8.5)"
print_success "- CPU 크레딧 기반으로 간헐적 사용에 최적화"
print_success "- 스팟 인스턴스 사용으로 최대 90% 할인 가능"
print_success "- 자동 재시작 설정으로 안정성 확보"
print_success ""
print_warning "중요: .env 파일에서 OPENAI_API_KEY를 실제 키로 변경하세요!"
print_warning "SSH 접속: ssh -i $KEY_PAIR_NAME.pem ec2-user@$PUBLIC_IP"
