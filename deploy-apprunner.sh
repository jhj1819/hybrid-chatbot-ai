#!/bin/bash

# AWS App Runner 배포 스크립트
# 사용법: ./deploy-apprunner.sh <AWS_ACCOUNT_ID> <AWS_REGION>

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# 매개변수 확인
if [ $# -ne 2 ]; then
    print_error "사용법: $0 <AWS_ACCOUNT_ID> <AWS_REGION>"
    print_error "예시: $0 123456789012 ap-northeast-2"
    exit 1
fi

AWS_ACCOUNT_ID=$1
AWS_REGION=$2
REPOSITORY_NAME="hybrid-chatbot-ai"
IMAGE_TAG="latest"

print_info "AWS App Runner 배포를 시작합니다..."
print_info "AWS Account ID: $AWS_ACCOUNT_ID"
print_info "AWS Region: $AWS_REGION"
print_info "Repository: $REPOSITORY_NAME"

# ECR 로그인
print_info "ECR에 로그인 중..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# ECR 리포지토리 존재 확인 및 생성
print_info "ECR 리포지토리 확인 중..."
if ! aws ecr describe-repositories --repository-names $REPOSITORY_NAME --region $AWS_REGION >/dev/null 2>&1; then
    print_info "ECR 리포지토리를 생성합니다..."
    aws ecr create-repository --repository-name $REPOSITORY_NAME --region $AWS_REGION
else
    print_info "ECR 리포지토리가 이미 존재합니다."
fi

# Docker 이미지 빌드
print_info "Docker 이미지를 빌드합니다..."
docker build -t $REPOSITORY_NAME:$IMAGE_TAG .

# ECR에 태그 지정
ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPOSITORY_NAME:$IMAGE_TAG"
print_info "이미지에 ECR 태그를 지정합니다: $ECR_URI"
docker tag $REPOSITORY_NAME:$IMAGE_TAG $ECR_URI

# ECR에 푸시
print_info "이미지를 ECR에 푸시합니다..."
docker push $ECR_URI

print_info "배포 준비가 완료되었습니다!"
print_info ""
print_info "다음 단계를 수행하세요:"
print_info "1. AWS App Runner 콘솔로 이동"
print_info "2. 'Create service' 클릭"
print_info "3. 소스 설정:"
print_info "   - Source type: Container registry"
print_info "   - Provider: Amazon ECR"
print_info "   - Container image URI: $ECR_URI"
print_info "4. 서비스 설정:"
print_info "   - Service name: $REPOSITORY_NAME"
print_info "   - Virtual CPU: 1 vCPU"
print_info "   - Virtual memory: 2 GB"
print_info "5. 환경 변수 설정:"
print_info "   - OPENAI_API_KEY: your_openai_api_key_here"
print_info "   - PORT: 8000"
print_info "   - PYTHONPATH: /app"
print_info "   - ENVIRONMENT: production"
print_info "6. 네트워크 설정:"
print_info "   - Port: 8000"
print_info "   - Health check path: /"
print_info ""
print_warning "배포 후 서비스 URL을 확인하고 API 테스트를 수행하세요."
print_info "API 문서: https://your-service-url.region.awsapprunner.com/docs"
