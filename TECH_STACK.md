# 프로젝트 기술 스택 및 사용 사례

## 1. **Python 3.12**
- **특징**: 최신 Python 버전, 타입 힌팅 및 성능 개선
- **사용 사례**: 프로젝트의 메인 프로그래밍 언어로 사용

## 2. **FastAPI**
- **특징**: 고성능 비동기 웹 프레임워크, 자동 API 문서 생성, 타입 검증
- **사용 사례**: 
  - RESTful API 엔드포인트 구현 (`/zeroshot-intent`, `/embed`)
  - CORS 미들웨어로 외부 접근 허용
  - Pydantic 모델을 통한 요청/응답 검증

## 3. **Uvicorn**
- **특징**: ASGI 서버, 비동기 처리 지원
- **사용 사례**: FastAPI 애플리케이션의 프로덕션 서버로 사용

## 4. **OpenAI API**
- **특징**: GPT-4o 모델, 텍스트 임베딩 모델 제공
- **사용 사례**:
  - `gpt-4o` 모델로 의도 분류 수행
  - `text-embedding-3-small` 모델로 문서 임베딩 생성

## 5. **LangChain**
- **특징**: LLM 애플리케이션 구축 프레임워크, 체이닝 및 모듈화 지원
- **사용 사례**:
  - `OpenAIEmbeddings`: 텍스트를 벡터로 변환
  - `FAISS` 벡터스토어와 통합하여 RAG 구현
  - `DirectoryLoader`, `TextLoader`: 지식 베이스 문서 로딩
  - `RecursiveCharacterTextSplitter`: 문서 청킹

## 6. **FAISS (Facebook AI Similarity Search)**
- **특징**: 고성능 벡터 유사도 검색 라이브러리
- **사용 사례**:
  - 지식 베이스 문서를 벡터로 변환하여 저장
  - 사용자 질문과 유사한 문서 검색 (Top-K: 3개)
  - RAG 전략에서 컨텍스트 검색에 활용

## 7. **Pydantic**
- **특징**: 데이터 검증 및 설정 관리, 타입 안정성
- **사용 사례**:
  - `IntentRequest`, `IntentResponse`, `EmbeddingRequest`, `EmbeddingResponse` 모델 정의
  - API 요청/응답 데이터 자동 검증

## 8. **Docker & Docker Compose**
- **특징**: 컨테이너화, 환경 일관성 보장
- **사용 사례**:
  - Python 3.12 기반 컨테이너 이미지 생성
  - FAISS 컴파일을 위한 시스템 패키지 설치
  - 볼륨 마운트로 FAISS 인덱스 및 지식 베이스 관리
  - 헬스체크 설정으로 서비스 모니터링

## 9. **python-dotenv**
- **특징**: 환경 변수 관리
- **사용 사례**: `.env` 파일에서 `OPENAI_API_KEY` 등 민감 정보 로드

## 10. **NumPy**
- **특징**: 수치 연산 라이브러리
- **사용 사례**: FAISS 및 벡터 연산의 기반 라이브러리로 사용

## 11. **Strategy Pattern (디자인 패턴)**
- **특징**: 알고리즘을 캡슐화하여 런타임에 전략 선택 가능
- **사용 사례**:
  - `ClassificationStrategy` 추상 클래스로 인터페이스 정의
  - `RagStrategy`: RAG를 활용한 의도 분류
  - `NoRagStrategy`: RAG 없이 LLM만으로 의도 분류
  - `StrategyFactory`: 모드에 따라 적절한 전략 인스턴스 생성

## 12. **Requests**
- **특징**: HTTP 클라이언트 라이브러리
- **사용 사례**: Docker 헬스체크에서 서버 상태 확인

---

## 아키텍처 특징
- **하이브리드 접근**: RAG 모드와 No-RAG 모드를 동적으로 전환 가능
- **전략 패턴**: 확장 가능한 의도 분류 시스템
- **벡터 검색**: FAISS를 통한 고속 유사도 검색
- **RESTful API**: 표준 HTTP 메서드로 외부 시스템과 통신



