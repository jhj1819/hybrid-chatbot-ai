# 🤖 Hybrid Chatbot AI

AI 기반 의도 분류 및 임베딩 생성 API 서버입니다. Strategy Pattern을 활용하여 RAG(Retrieval-Augmented Generation) 모드와 No-RAG 모드를 동적으로 전환할 수 있는 하이브리드 챗봇 시스템입니다.

## 📋 프로젝트 개요

### 배경 및 목적
기존 챗봇 시스템의 한계를 해결하기 위해 개발된 프로젝트입니다:
- **문제점**: 단순한 규칙 기반 챗봇은 복잡한 의도 분류에 한계가 있음
- **해결책**: LLM과 RAG를 결합한 하이브리드 접근 방식으로 정확도와 유연성 확보
- **차별점**: 상황에 따라 RAG/No-RAG 모드를 동적으로 선택하여 성능과 비용 최적화

### 핵심 성과
- ✅ **Strategy Pattern**을 통한 확장 가능한 아키텍처 설계
- ✅ **FAISS 벡터 검색**을 활용한 고속 유사도 검색 구현
- ✅ **AWS EC2 배포** 및 비용 최적화 (스팟 인스턴스 활용으로 최대 90% 비용 절감)
- ✅ **Docker 컨테이너화**를 통한 배포 자동화
- ✅ **성능 평가 시스템** 구축으로 모델 정확도 측정

## ✨ 주요 기능

- **하이브리드 의도 분류**: RAG 모드와 No-RAG 모드를 동적으로 선택하여 사용자의 질문 의도를 분류
- **벡터 검색 기반 RAG**: FAISS를 활용한 고속 유사도 검색으로 관련 문서를 검색하여 정확도 향상
- **임베딩 생성 API**: 텍스트를 벡터로 변환하는 임베딩 생성 엔드포인트 제공
- **전략 패턴 구현**: 확장 가능한 아키텍처로 새로운 분류 전략을 쉽게 추가 가능
- **RESTful API**: FastAPI 기반의 자동 문서화된 API 제공
- **성능 평가 도구**: 테스트 데이터셋을 활용한 모델 정확도 측정

## 🛠️ 기술 스택

### Backend
- **Python 3.12**: 최신 Python 버전, 타입 힌팅 지원
- **FastAPI**: 고성능 비동기 웹 프레임워크, 자동 API 문서 생성
- **Uvicorn**: ASGI 서버, 비동기 처리 지원

### AI/ML
- **OpenAI GPT-4o**: 의도 분류를 위한 LLM
- **LangChain**: LLM 애플리케이션 구축 프레임워크
- **FAISS**: Facebook AI Similarity Search - 벡터 유사도 검색 라이브러리
- **OpenAI Embeddings (text-embedding-3-small)**: 텍스트 임베딩 생성

### 인프라 & DevOps
- **Docker & Docker Compose**: 컨테이너화 및 배포 자동화
- **AWS EC2**: 클라우드 서버 배포
- **GitHub Actions**: CI/CD 파이프라인 (선택사항)

### 기타
- **Pydantic**: 데이터 검증 및 타입 안정성
- **python-dotenv**: 환경 변수 관리

## 🏗️ 아키텍처 설계

### 디자인 패턴: Strategy Pattern

이 프로젝트의 핵심은 **Strategy Pattern**을 활용한 확장 가능한 아키텍처입니다:

```
ClassificationStrategy (추상 클래스)
    ├── RagStrategy: RAG를 활용한 의도 분류
    │   ├── FAISS 벡터 검색으로 관련 문서 검색
    │   ├── 검색된 문서를 컨텍스트로 활용
    │   └── GPT-4o로 의도 분류 수행
    │
    └── NoRagStrategy: RAG 없이 LLM만으로 의도 분류
        ├── 빠른 응답 시간
        └── LLM의 기본 능력 활용

StrategyFactory: 모드에 따라 적절한 전략 인스턴스 생성
```

### 기술 선택 이유

1. **FastAPI 선택**
   - 비동기 처리로 높은 성능
   - 자동 API 문서 생성 (Swagger UI)
   - Pydantic을 통한 타입 안정성

2. **FAISS 선택**
   - 메모리 기반 벡터 검색으로 빠른 응답 시간
   - 대규모 벡터 데이터 처리 가능
   - LangChain과의 원활한 통합

3. **Strategy Pattern 선택**
   - 새로운 분류 전략 추가가 용이
   - 코드 재사용성 및 유지보수성 향상
   - 런타임에 전략 선택 가능

## 📁 프로젝트 구조

```
hybrid-chatbot-ai/
├── app/
│   ├── main.py                 # FastAPI 애플리케이션 메인 파일
│   └── strategies/
│       ├── base.py             # 추상 전략 클래스
│       ├── factory.py          # 전략 팩토리
│       ├── rag_strategy.py     # RAG 기반 의도 분류 전략
│       └── no_rag_strategy.py  # No-RAG 기반 의도 분류 전략
├── knowledge/                  # 지식 베이스 문서 (RAG용)
│   ├── collaboration_policy.txt
│   ├── refund_procedure.txt
│   └── ...
├── faiss_index/                # FAISS 벡터 인덱스
├── create_vectorstore.py       # 벡터스토어 생성 스크립트
├── evaluate.py                 # 성능 평가 스크립트
├── test_questions.csv          # 테스트 데이터셋
├── run_server.py               # 서버 실행 스크립트
├── requirements.txt            # Python 의존성
├── Dockerfile                  # Docker 이미지 설정
├── docker-compose.yml          # Docker Compose 설정
├── deploy-ec2.sh               # AWS EC2 배포 스크립트
└── README.md                   # 프로젝트 문서
```

## 🚀 빠른 시작

### 1. 저장소 클론

```bash
git clone https://github.com/your-username/hybrid-chatbot-ai.git
cd hybrid-chatbot-ai
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 OpenAI API 키를 설정합니다:

```bash
cp env.example .env
```

`.env` 파일을 열어 `OPENAI_API_KEY`를 설정하세요:

```env
OPENAI_API_KEY=your_openai_api_key_here
PORT=8000
WORKERS=1
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 벡터스토어 생성

지식 베이스 문서를 벡터로 변환하여 FAISS 인덱스를 생성합니다:

```bash
python create_vectorstore.py
```

이 스크립트는 `knowledge/` 폴더의 모든 `.txt` 파일을 읽어 벡터 인덱스를 생성하고 `faiss_index/` 폴더에 저장합니다.

### 5. 서버 실행

```bash
python run_server.py
```

서버가 실행되면 다음 URL에서 접근할 수 있습니다:
- API 서버: `http://localhost:8000`
- API 문서: `http://localhost:8000/docs`
- 대화형 API 문서: `http://localhost:8000/redoc`

## 🐳 Docker를 사용한 실행

### Docker Compose 사용 (권장)

```bash
docker-compose up -d
```

### Docker 직접 사용

```bash
# 이미지 빌드
docker build -t hybrid-chatbot-ai .

# 컨테이너 실행
docker run -p 8000:8000 --env-file .env hybrid-chatbot-ai
```

## 📡 API 사용법

### 1. 의도 분류 API

사용자의 질문을 분석하여 의도를 분류합니다.

**엔드포인트**: `POST /zeroshot-intent`

**요청 예시**:

```json
{
  "user_question": "쿠폰과 세일을 동시에 사용할 수 있나요?",
  "intent_list": [
    "쿠폰_및_세일_중복적용_문의",
    "특별세일_상품_환불_문의",
    "VIP_정책_문의"
  ],
  "mode": "rag"  // "rag" 또는 "no_rag"
}
```

**응답 예시**:

```json
{
  "final_intent": "쿠폰_및_세일_중복적용_문의",
  "bot_response": "'rag' 모드로 '쿠폰_및_세일_중복적용_문의' 분류됨",
  "engine": "strategy-rag"
}
```

**모드 설명**:
- `rag`: FAISS 벡터 검색을 통해 관련 문서를 검색한 후 의도 분류 (더 정확하지만 느림)
- `no_rag`: LLM의 기본 능력만으로 의도 분류 (빠르지만 컨텍스트 없음)

### 2. 임베딩 생성 API

텍스트를 벡터로 변환합니다.

**엔드포인트**: `POST /embed`

**요청 예시**:

```json
{
  "texts": [
    "쿠폰과 세일을 동시에 사용할 수 있나요?",
    "환불 절차를 알려주세요"
  ]
}
```

**응답 예시**:

```json
{
  "embeddings": [
    [0.123, -0.456, 0.789, ...],
    [-0.234, 0.567, -0.890, ...]
  ]
}
```

### 3. 헬스 체크

서버 상태를 확인합니다.

**엔드포인트**: `GET /`

**응답 예시**:

```json
{
  "status": "AI server is running"
}
```

## 🧪 성능 평가

프로젝트에는 성능 평가 스크립트가 포함되어 있습니다:

```bash
python evaluate.py
```

이 스크립트는 `test_questions.csv`의 테스트 데이터를 사용하여 모델의 정확도를 측정합니다.

**평가 지표**:
- 정확도 (Accuracy): 전체 질문 중 올바르게 분류된 비율
- 모드별 성능 비교: RAG 모드 vs No-RAG 모드

## ☁️ 배포 및 운영

### AWS EC2 배포

프로젝트는 AWS EC2에 배포할 수 있도록 스크립트가 포함되어 있습니다:

```bash
./deploy-ec2.sh ap-northeast-2 my-key-pair
```

### 비용 최적화 전략

- **스팟 인스턴스 활용**: 최대 90% 비용 절감
- **인스턴스 타입 최적화**: t3.micro (월 $8.5) → 스팟 인스턴스 (월 $1-3)
- **자동 스케일링**: 트래픽에 따라 인스턴스 타입 자동 조정
- **CloudWatch 모니터링**: CPU/메모리 사용률 모니터링 및 알림

자세한 내용은 `cost-optimization.md`를 참조하세요.

### Docker 배포

프로덕션 환경에서는 Docker를 사용한 배포를 권장합니다:

```bash
docker-compose up -d
```

## 🔧 환경 변수

| 변수명 | 설명 | 필수 | 기본값 |
|--------|------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 키 | ✅ | - |
| `PORT` | 서버 포트 | ❌ | 8000 |
| `WORKERS` | 워커 프로세스 수 | ❌ | 1 |
| `LOG_LEVEL` | 로그 레벨 | ❌ | info |

## 🔒 보안 주의사항

### ⚠️ Public 저장소 전환 전 확인사항

이 저장소를 public으로 전환하기 전에 다음 사항을 확인하세요:

1. **`.env` 파일이 커밋되지 않았는지 확인**
   ```bash
   git ls-files | grep .env
   ```
   - `.env` 파일이 목록에 나타나면 **즉시 삭제**하고 Git 히스토리에서 제거하세요
   - `.gitignore`에 `.env`가 포함되어 있는지 확인하세요

2. **실제 API 키가 코드에 하드코딩되지 않았는지 확인**
   - 모든 스크립트 파일의 API 키는 플레이스홀더(`sk-your-actual-openai-api-key-REPLACE-THIS`)만 포함되어야 합니다
   - 실제 키가 발견되면 즉시 키를 재발급하고 코드에서 제거하세요

3. **Git 히스토리 확인**
   ```bash
   # Git 히스토리에서 API 키 검색
   git log -p | grep -i "sk-[a-zA-Z0-9]"
   ```
   - 과거 커밋에 실제 키가 있다면 `git filter-branch` 또는 `BFG Repo-Cleaner`를 사용하여 제거하세요

4. **배포 스크립트 확인**
   - 배포 스크립트(`deploy-ec2.sh`, `ec2-user-data.sh` 등)에는 플레이스홀더만 포함되어 있어야 합니다
   - 실제 배포 시에는 환경 변수나 AWS Secrets Manager를 사용하세요

### ✅ 현재 상태

- ✅ `.gitignore`에 `.env` 파일이 포함되어 있음
- ✅ 모든 스크립트에 플레이스홀더만 사용됨
- ✅ 실제 API 키는 코드에 포함되지 않음

### 🛡️ 권장 보안 사례

1. **환경 변수 사용**: 항상 `.env` 파일을 사용하고 Git에 커밋하지 않기
2. **AWS Secrets Manager**: 프로덕션 환경에서는 AWS Secrets Manager 사용 권장
3. **키 로테이션**: 정기적으로 API 키를 재발급하고 업데이트
4. **접근 제어**: API 키에 최소 권한 원칙 적용

## 📝 지식 베이스 관리

`knowledge/` 폴더에 `.txt` 파일을 추가하여 지식 베이스를 확장할 수 있습니다. 새로운 문서를 추가한 후 벡터스토어를 재생성하세요:

```bash
python create_vectorstore.py
```

## 🎯 핵심 기술 경험

이 프로젝트를 통해 얻은 주요 기술 경험:

1. **아키텍처 설계**
   - Strategy Pattern을 활용한 확장 가능한 시스템 설계
   - 추상화를 통한 코드 재사용성 향상

2. **RAG 구현**
   - FAISS를 활용한 벡터 검색 시스템 구축
   - 문서 임베딩 및 청킹 전략 수립

3. **클라우드 배포**
   - AWS EC2 인스턴스 배포 및 운영
   - Docker 컨테이너화 및 배포 자동화
   - 비용 최적화 전략 수립

4. **성능 최적화**
   - 모드별 성능 비교 및 평가
   - 응답 시간과 정확도의 트레이드오프 관리

5. **API 설계**
   - RESTful API 설계 및 문서화
   - Pydantic을 통한 데이터 검증

## 🚧 향후 개선 계획

- [ ] **캐싱 시스템 도입**: Redis를 활용한 응답 캐싱으로 응답 시간 단축
- [ ] **로깅 및 모니터링 강화**: ELK Stack 또는 CloudWatch를 통한 상세 로깅
- [ ] **멀티 모델 지원**: GPT-4o 외 다른 LLM 모델 지원 (Claude, Gemini 등)
- [ ] **실시간 스트리밍**: SSE(Server-Sent Events)를 통한 실시간 응답 스트리밍
- [ ] **인증 및 보안**: API 키 기반 인증 시스템 추가
- [ ] **테스트 코드 작성**: Unit Test 및 Integration Test 추가

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📧 문의

프로젝트에 대한 질문이나 제안사항이 있으시면 이슈를 생성해주세요.

---

⭐ 이 프로젝트가 도움이 되었다면 Star를 눌러주세요!
