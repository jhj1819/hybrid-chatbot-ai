# AWS App Runner 배포 가이드

이 문서는 Hybrid Chatbot AI 프로젝트를 AWS App Runner에 배포하는 방법을 설명합니다.

## 사전 요구사항

1. AWS 계정 및 CLI 설정
2. Docker 이미지를 저장할 ECR (Elastic Container Registry) 리포지토리
3. OpenAI API 키

## 배포 단계

### 1. ECR 리포지토리 생성

```bash
# ECR 리포지토리 생성
aws ecr create-repository --repository-name hybrid-chatbot-ai --region ap-northeast-2

# 로그인 토큰 가져오기
aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.ap-northeast-2.amazonaws.com
```

### 2. Docker 이미지 빌드 및 푸시

```bash
# Docker 이미지 빌드
docker build -t hybrid-chatbot-ai .

# ECR에 태그 지정
docker tag hybrid-chatbot-ai:latest <ACCOUNT_ID>.dkr.ecr.ap-northeast-2.amazonaws.com/hybrid-chatbot-ai:latest

# ECR에 푸시
docker push <ACCOUNT_ID>.dkr.ecr.ap-northeast-2.amazonaws.com/hybrid-chatbot-ai:latest
```

### 3. App Runner 서비스 생성

AWS 콘솔에서 App Runner 서비스를 생성할 때 다음 설정을 사용하세요:

#### 소스 설정
- **소스 유형**: Container registry
- **Provider**: Amazon ECR
- **Container image URI**: `<ACCOUNT_ID>.dkr.ecr.ap-northeast-2.amazonaws.com/hybrid-chatbot-ai:latest`

#### 서비스 설정
- **Service name**: `hybrid-chatbot-ai`
- **Virtual CPU**: 1 vCPU
- **Virtual memory**: 2 GB
- **Environment variables**:
  - `OPENAI_API_KEY`: `your_openai_api_key_here`
  - `PORT`: `8000`
  - `PYTHONPATH`: `/app`
  - `ENVIRONMENT`: `production`

#### 네트워크 설정
- **Port**: `8000`
- **Health check path**: `/`

### 4. 환경 변수 설정

App Runner 서비스 생성 후 다음 환경 변수를 설정하세요:

```
OPENAI_API_KEY=sk-your-actual-openai-api-key
PORT=8000
PYTHONPATH=/app
ENVIRONMENT=production
LOG_LEVEL=info
```

### 5. 배포 확인

서비스가 배포되면 다음 URL로 접근할 수 있습니다:
- **서비스 URL**: `https://your-service-name.region.awsapprunner.com`
- **API 문서**: `https://your-service-name.region.awsapprunner.com/docs`
- **헬스체크**: `https://your-service-name.region.awsapprunner.com/`

## API 엔드포인트

### 1. 의도 분류 API
```bash
POST /zeroshot-intent
Content-Type: application/json

{
  "user_question": "쿠폰과 세일을 동시에 사용할 수 있나요?",
  "intent_list": ["쿠폰_및_세일_중복적용_문의", "환불_문의", "VIP_정책_문의"],
  "mode": "rag"
}
```

### 2. 임베딩 생성 API
```bash
POST /embed
Content-Type: application/json

{
  "texts": ["안녕하세요", "환불하고 싶어요"]
}
```

## 트러블슈팅

### 일반적인 문제들

1. **서비스 시작 실패**
   - 환경 변수 `OPENAI_API_KEY`가 올바르게 설정되었는지 확인
   - FAISS 인덱스 파일이 올바르게 포함되었는지 확인

2. **헬스체크 실패**
   - 포트 8000이 올바르게 노출되었는지 확인
   - `/` 엔드포인트가 정상적으로 응답하는지 확인

3. **메모리 부족**
   - App Runner 서비스의 메모리를 2GB 이상으로 설정
   - FAISS 인덱스 크기를 확인하고 필요시 최적화

### 로그 확인

App Runner 콘솔에서 CloudWatch 로그를 확인하여 문제를 진단할 수 있습니다.

## 비용 최적화

1. **자동 스케일링 설정**
   - 최소 인스턴스: 1
   - 최대 인스턴스: 3
   - CPU 임계값: 70%

2. **리소스 최적화**
   - 사용량에 따라 vCPU와 메모리 조정
   - 사용하지 않을 때 서비스 중지

## 보안 고려사항

1. **환경 변수**
   - 민감한 정보는 AWS Secrets Manager 사용 권장
   - API 키는 App Runner 환경 변수로만 설정

2. **네트워크**
   - 필요시 VPC 연결 설정
   - 보안 그룹으로 접근 제한

3. **모니터링**
   - CloudWatch를 통한 로그 및 메트릭 모니터링
   - 알람 설정으로 이상 상황 감지
