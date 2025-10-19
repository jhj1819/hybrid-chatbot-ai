# AWS App Runner 배포 PowerShell 스크립트
# 사용법: .\deploy-apprunner.ps1 -AccountId <AWS_ACCOUNT_ID> -Region <AWS_REGION>

param(
    [Parameter(Mandatory=$true)]
    [string]$AccountId,
    
    [Parameter(Mandatory=$true)]
    [string]$Region
)

# 색상 함수 정의
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# 변수 설정
$RepositoryName = "hybrid-chatbot-ai"
$ImageTag = "latest"
$EcrUri = "$AccountId.dkr.ecr.$Region.amazonaws.com/$RepositoryName`:$ImageTag"

Write-Info "AWS App Runner 배포를 시작합니다..."
Write-Info "AWS Account ID: $AccountId"
Write-Info "AWS Region: $Region"
Write-Info "Repository: $RepositoryName"

try {
    # ECR 로그인
    Write-Info "ECR에 로그인 중..."
    $loginCommand = "aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin $AccountId.dkr.ecr.$Region.amazonaws.com"
    Invoke-Expression $loginCommand

    # ECR 리포지토리 존재 확인 및 생성
    Write-Info "ECR 리포지토리 확인 중..."
    try {
        aws ecr describe-repositories --repository-names $RepositoryName --region $Region | Out-Null
        Write-Info "ECR 리포지토리가 이미 존재합니다."
    }
    catch {
        Write-Info "ECR 리포지토리를 생성합니다..."
        aws ecr create-repository --repository-name $RepositoryName --region $Region
    }

    # Docker 이미지 빌드
    Write-Info "Docker 이미지를 빌드합니다..."
    docker build -t $RepositoryName`:$ImageTag .

    # ECR에 태그 지정
    Write-Info "이미지에 ECR 태그를 지정합니다: $EcrUri"
    docker tag $RepositoryName`:$ImageTag $EcrUri

    # ECR에 푸시
    Write-Info "이미지를 ECR에 푸시합니다..."
    docker push $EcrUri

    Write-Info "배포 준비가 완료되었습니다!"
    Write-Info ""
    Write-Info "다음 단계를 수행하세요:"
    Write-Info "1. AWS App Runner 콘솔로 이동"
    Write-Info "2. 'Create service' 클릭"
    Write-Info "3. 소스 설정:"
    Write-Info "   - Source type: Container registry"
    Write-Info "   - Provider: Amazon ECR"
    Write-Info "   - Container image URI: $EcrUri"
    Write-Info "4. 서비스 설정:"
    Write-Info "   - Service name: $RepositoryName"
    Write-Info "   - Virtual CPU: 1 vCPU"
    Write-Info "   - Virtual memory: 2 GB"
    Write-Info "5. 환경 변수 설정:"
    Write-Info "   - OPENAI_API_KEY: your_openai_api_key_here"
    Write-Info "   - PORT: 8000"
    Write-Info "   - PYTHONPATH: /app"
    Write-Info "   - ENVIRONMENT: production"
    Write-Info "6. 네트워크 설정:"
    Write-Info "   - Port: 8000"
    Write-Info "   - Health check path: /"
    Write-Info ""
    Write-Warning "배포 후 서비스 URL을 확인하고 API 테스트를 수행하세요."
    Write-Info "API 문서: https://your-service-url.region.awsapprunner.com/docs"
}
catch {
    Write-Error "배포 중 오류가 발생했습니다: $($_.Exception.Message)"
    exit 1
}
