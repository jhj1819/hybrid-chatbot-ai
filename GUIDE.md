# Hybrid Chatbot AI - 상세 설명서

## 목차

1. [프로젝트 전체 구조](#1-프로젝트-전체-구조)
2. [핵심 아키텍처: Strategy Pattern](#2-핵심-아키텍처-strategy-pattern)
3. [코어 애플리케이션 코드 상세](#3-코어-애플리케이션-코드-상세)
4. [Knowledge Base & FAISS 벡터 검색](#4-knowledge-base--faiss-벡터-검색)
5. [실험 및 평가 시스템](#5-실험-및-평가-시스템)
6. [환경 설정 및 실행 방법](#6-환경-설정-및-실행-방법)
7. [Docker 배포](#7-docker-배포)
8. [API 명세서](#8-api-명세서)
9. [파일별 상세 설명](#9-파일별-상세-설명)
10. [명령어 모음 (Quick Reference)](#10-명령어-모음-quick-reference)
11. [트러블슈팅](#11-트러블슈팅)

---

## 1. 프로젝트 전체 구조

```
hybrid-chatbot-ai/
│
├── app/                              # [핵심] FastAPI 애플리케이션
│   ├── __init__.py                   # Python 패키지 선언
│   ├── main.py                       # FastAPI 앱 진입점, API 엔드포인트 정의
│   └── strategies/                   # Strategy Pattern 구현
│       ├── __init__.py
│       ├── base.py                   # 추상 클래스 (설계도)
│       ├── factory.py                # 전략 팩토리 (모드별 전략 생성)
│       ├── rag_strategy.py           # RAG 전략 (문서 검색 + LLM)
│       └── no_rag_strategy.py        # No-RAG 전략 (LLM만 사용)
│
├── knowledge/                        # [데이터] RAG용 지식 베이스 문서 (10개)
│   ├── refund_procedure.txt          # 환불 정책
│   ├── exchange_policy.txt           # 교환 정책
│   ├── delivery_policy.txt           # 배송 정책
│   ├── order_cancel_policy.txt       # 주문 취소 정책
│   ├── coupon_policy.txt             # 쿠폰/세일 정책
│   ├── vip_policy.txt                # VIP 등급 정책
│   ├── point_policy.txt              # 적립금 정책
│   ├── collaboration_policy.txt      # 콜라보 한정판 정책
│   ├── intent_쿠폰_및_세일_중복적용_문의.txt
│   └── intent_특별세일_상품_환불_문의.txt
│
├── faiss_index/                      # [자동생성] FAISS 벡터 인덱스
│   ├── index.faiss                   # 벡터 데이터
│   └── index.pkl                     # 메타데이터
│
├── create_vectorstore.py             # [유틸] 벡터스토어 생성 스크립트
├── run_server.py                     # [유틸] 서버 실행 스크립트
├── evaluate.py                       # [평가] 기본 평가 스크립트 (RAG/No-RAG)
├── run_3way_experiment.py            # [실험] 3-Way 비교 실험
├── auto_label_hallucination.py       # [실험] 자동 환각 레이블링
├── label_hallucination.py            # [실험] 수동 환각 레이블링
├── analyze_results.py                # [실험] 결과 분석 + 차트 생성
├── fix_rule_only_time.py             # [실험] Rule-only 응답시간 보정
│
├── test_dataset.csv                  # [데이터] 100개 테스트 질의
├── test_questions.csv                # [데이터] 기존 8개 테스트 질의
├── ground_truth_db.json              # [데이터] 정답 DB (환각 판정 기준)
├── intent_list.json                  # [데이터] 인텐트 목록 (10개)
├── experiment_results.csv            # [결과] 실험 원본 결과
├── experiment_results_labeled.csv    # [결과] 환각 레이블 포함 결과
├── experiment_charts.png             # [결과] 시각화 차트
│
├── .env                              # [설정] 환경 변수 (gitignore됨)
├── env.example                       # [설정] .env 예시 파일
├── requirements.txt                  # [설정] Python 패키지 의존성
├── Dockerfile                        # [배포] Docker 이미지 정의
├── docker-compose.yml                # [배포] Docker Compose 설정
└── README.md                         # 프로젝트 소개 + 실험 결과
```

---

## 2. 핵심 아키텍처: Strategy Pattern

### 2-1. 왜 Strategy Pattern인가?

이 프로젝트는 **의도 분류(Intent Classification)** 를 수행하는데, 분류 방식이 두 가지입니다:

| 모드 | 방식 | 장점 | 단점 |
|:---|:---|:---|:---|
| **RAG** | 지식 문서를 검색한 뒤 LLM에게 전달 | 정확도 높음, 환각 적음 | 느림 (검색 + LLM) |
| **No-RAG** | LLM에게 바로 질문 | 빠름 | 정확도 낮음, 환각 위험 |

Strategy Pattern을 사용하면 `mode` 값 하나로 분류 방식을 런타임에 전환할 수 있습니다.

### 2-2. 클래스 다이어그램

```
         ┌─────────────────────────┐
         │  ClassificationStrategy │  ← 추상 클래스 (base.py)
         │  ───────────────────── │
         │  + classify()          │  ← 모든 전략이 반드시 구현해야 하는 메서드
         └────────┬───────────────┘
                  │
         ┌────────┴────────┐
         │                 │
   ┌─────▼──────┐   ┌─────▼──────┐
   │ RagStrategy│   │NoRagStrategy│
   │            │   │             │
   │ 1. 검색   │   │ LLM에게    │
   │ 2. 프롬프트│   │ 바로 질문  │
   │ 3. LLM    │   │             │
   └────────────┘   └─────────────┘
         │                 │
         └────────┬────────┘
                  │
        ┌─────────▼──────────┐
        │  StrategyFactory   │  ← mode에 따라 적절한 전략 생성
        │  get_strategy()    │
        └────────────────────┘
```

### 2-3. 요청 처리 흐름

```
사용자 요청 (mode="rag")
       │
       ▼
  FastAPI (main.py)
       │
       ▼
  StrategyFactory.get_strategy("rag")
       │
       ▼
  RagStrategy 인스턴스 생성
       │
       ▼
  RagStrategy.classify()
       │
       ├── 1단계: FAISS에서 관련 문서 3개 검색 (Retrieve)
       ├── 2단계: 검색된 문서를 프롬프트에 포함 (Augment)
       └── 3단계: GPT-4o에게 의도 분류 요청 (Generate)
       │
       ▼
  분류 결과 반환: "환불_절차_문의"
```

---

## 3. 코어 애플리케이션 코드 상세

### 3-1. `app/main.py` — FastAPI 앱 진입점

**역할**: 전체 시스템의 중심. 서버 초기화, API 엔드포인트 정의, 요청/응답 처리를 담당합니다.

**서버 초기화 시 하는 일** (서버가 켜질 때 한 번만 실행):
1. `.env` 파일에서 `OPENAI_API_KEY`를 로드
2. OpenAI 클라이언트 생성
3. `text-embedding-3-small` 모델로 FAISS 벡터스토어를 로드
4. FAISS에서 Retriever 생성 (유사 문서 3개 검색하도록 설정)
5. StrategyFactory 생성 (OpenAI 클라이언트 + Retriever 주입)

**API 엔드포인트**:
- `GET /` — 서버 상태 확인 (헬스 체크)
- `POST /zeroshot-intent` — 의도 분류 (핵심 기능)
- `POST /embed` — 텍스트를 벡터로 변환

**요청/응답 DTO**:
```python
# 요청
class IntentRequest:
    user_question: str      # 사용자 질문
    intent_list: list[str]  # 분류 대상 인텐트 목록
    mode: str = "rag"       # "rag" 또는 "no_rag"

# 응답
class IntentResponse:
    final_intent: str       # 분류된 인텐트
    bot_response: str       # 응답 메시지
    engine: str             # 사용된 엔진 정보
```

**안전장치**: LLM이 인텐트 목록에 없는 답변을 하면 `"Default Fallback Intent"`로 대체합니다.

---

### 3-2. `app/strategies/base.py` — 추상 클래스 (설계도)

**역할**: 모든 전략 클래스가 반드시 따라야 하는 인터페이스를 정의합니다.

```python
class ClassificationStrategy(ABC):
    @abstractmethod
    def classify(self, user_question: str, intent_list: list[str]) -> str:
        pass
```

- `ABC`를 상속받아 추상 클래스임을 선언
- `@abstractmethod`로 `classify()` 메서드 구현을 강제
- 새로운 전략을 만들 때 이 클래스를 상속받으면 됨

---

### 3-3. `app/strategies/rag_strategy.py` — RAG 전략

**역할**: 지식 베이스에서 관련 문서를 검색한 후, 해당 문서를 참고하여 LLM이 의도를 분류합니다.

**동작 과정 (RAG = Retrieve → Augment → Generate)**:

1. **Retrieve (검색)**: `self.retriever.invoke(user_question)`
   - 사용자 질문을 벡터로 변환
   - FAISS 인덱스에서 가장 유사한 문서 3개를 검색
   - 예: "환불 어떻게 해요?" → `refund_procedure.txt`, `exchange_policy.txt`, `vip_policy.txt`

2. **Augment (프롬프트 보강)**: 검색된 문서 내용을 프롬프트에 `[참고 자료]`로 삽입
   ```
   [참고 자료]
   환불은 수령 후 7일 이내 신청 가능...

   [의도 목록]
   환불_절차_문의, 교환_요청, 배송_조회, ...

   [질문]
   환불 어떻게 해요?
   ```

3. **Generate (생성)**: GPT-4o에게 분류 요청
   - `temperature=0`: 매번 동일한 결과를 보장 (결정적 응답)
   - `max_tokens=50`: 인텐트 이름만 짧게 반환

---

### 3-4. `app/strategies/no_rag_strategy.py` — No-RAG 전략

**역할**: 문서 검색 없이 LLM의 기본 지식만으로 의도를 분류합니다.

**RagStrategy와의 차이**:
- 검색 단계가 없음 → 더 빠름
- `[참고 자료]` 섹션이 없는 프롬프트 사용
- LLM이 자체 학습 데이터에만 의존 → 정확도 낮을 수 있음

---

### 3-5. `app/strategies/factory.py` — 전략 팩토리

**역할**: `mode` 문자열을 받아서 적절한 전략 인스턴스를 생성합니다.

```python
factory.get_strategy("rag")     → RagStrategy 인스턴스 반환
factory.get_strategy("no_rag")  → NoRagStrategy 인스턴스 반환
factory.get_strategy("xxx")     → ValueError 발생
```

**의존성 주입 (DI)**: 팩토리가 OpenAI 클라이언트와 Retriever를 보유하고 있다가, 전략 생성 시 주입합니다.

---

## 4. Knowledge Base & FAISS 벡터 검색

### 4-1. Knowledge Base (`knowledge/` 폴더)

10개의 `.txt` 파일로 구성된 지식 베이스입니다. RAG 전략이 이 문서들을 검색하여 참고합니다.

| 파일 | 내용 | 용도 |
|:---|:---|:---|
| `refund_procedure.txt` | 환불 규정 (기간, 조건, 환불 수단) | 환불_절차_문의 |
| `exchange_policy.txt` | 교환 정책 (조건, 비용, 절차) | 교환_요청 |
| `delivery_policy.txt` | 배송 정책 (소요 시간, 배송비, 택배사) | 배송_조회 |
| `order_cancel_policy.txt` | 주문 취소 정책 (시점, 부분 취소, 환불) | 주문_취소 |
| `coupon_policy.txt` | 쿠폰/세일 중복 적용 규칙 | 쿠폰_및_세일_중복적용_문의 |
| `vip_policy.txt` | VIP 등급 기준, 혜택, 제한사항 | VIP_정책_문의 |
| `point_policy.txt` | 적립금 적립/사용/유효기간 | 적립금_문의 |
| `collaboration_policy.txt` | 콜라보 한정판 구매 조건 | 특별 상품 관련 |
| `intent_쿠폰_및_세일_...` | 쿠폰+세일 복합 질문 의도 설명 | 의도 분류 보조 |
| `intent_특별세일_상품_...` | 특별세일 환불 의도 설명 | 의도 분류 보조 |

### 4-2. `create_vectorstore.py` — 벡터스토어 생성

**역할**: `knowledge/` 폴더의 모든 `.txt` 파일을 읽어서 FAISS 벡터 인덱스로 변환합니다.

**동작 과정**:
```
knowledge/*.txt 파일들
        │
        ▼
  DirectoryLoader로 로드 (UTF-8)
        │
        ▼
  RecursiveCharacterTextSplitter로 분할
  (chunk_size=1000자, overlap=100자)
        │
        ▼
  OpenAI text-embedding-3-small로 벡터 변환
        │
        ▼
  FAISS 인덱스로 저장 → faiss_index/ 폴더
```

**실행 명령어**:
```bash
python create_vectorstore.py
```

**주의사항**:
- `.env` 파일에 `OPENAI_API_KEY`가 설정되어 있어야 함
- `knowledge/` 폴더에 `.txt` 파일이 최소 1개 이상 있어야 함
- knowledge 파일을 추가/수정한 후에는 반드시 이 스크립트를 다시 실행해야 함
- OpenAI API 호출 비용이 발생 (매우 소액, 보통 $0.01 미만)

---

## 5. 실험 및 평가 시스템

### 5-1. 테스트 데이터 구성

**`test_dataset.csv`** (100개 질의):

| 컬럼 | 설명 | 예시 |
|:---|:---|:---|
| `id` | 질의 ID | A01, B15, C03 |
| `query` | 사용자 질문 | "환불 신청 어떻게 해요?" |
| `category` | 난이도 카테고리 | A_정형, B_복잡, C_환각유발 |
| `difficulty` | 난이도 | Easy, Medium, Hard |
| `gt_intent` | 정답 인텐트 | 환불_절차_문의 |
| `hallu_check_ref` | 환각 판정 기준 | "환불: 수령 후 7일 이내" |

카테고리 분포:
- **A_정형 (40개)**: 단순하고 직관적인 질문
- **B_복잡 (35개)**: 복합 조건, 여러 정책이 걸리는 질문
- **C_환각유발 (25개)**: LLM이 잘못된 정보를 생성하기 쉬운 함정 질문

**`intent_list.json`** (10개 인텐트):
```json
{
  "intent_list": [
    "환불_절차_문의", "교환_요청", "배송_조회", "주문_취소",
    "쿠폰_및_세일_중복적용_문의", "특별세일_상품_환불_문의",
    "VIP_정책_문의", "적립금_문의", "상품_문의", "결제_문의"
  ]
}
```

**`ground_truth_db.json`**: 각 정책별 정답 정보가 담긴 DB. 환각 판정 시 이 데이터를 기준으로 LLM 응답의 사실 여부를 검증합니다.

---

### 5-2. `run_3way_experiment.py` — 3-Way 비교 실험

**역할**: 동일한 100개 질의에 대해 3가지 시스템의 성능을 비교 측정합니다.

**3가지 시스템**:

| 시스템 | 구현 방식 | 설명 |
|:---|:---|:---|
| `rule_only` | AI서버 no_rag 모드 + 사전 정의 응답 | Dialogflow 시뮬레이션 |
| `llm_only` | OpenAI GPT-4o 직접 호출 | RAG 없이 LLM만 사용 |
| `hybrid_rag` | AI서버 rag 모드 | FAISS 검색 + LLM (우리 시스템) |

**실행 전 조건**:
- AI 서버가 `http://localhost:8000`에서 실행 중이어야 함
- `.env`에 `OPENAI_API_KEY` 설정 필요

**실행 명령어**:
```bash
# 터미널 1: 서버 실행
python run_server.py

# 터미널 2: 실험 실행
python run_3way_experiment.py
```

**소요 시간**: 약 30~60분 (100개 × 3시스템 = 300번 API 호출)
**예상 비용**: ~$1-3 (GPT-4o API 호출)

**출력 파일**: `experiment_results.csv` (300행 = 100질의 × 3시스템)

---

### 5-3. `auto_label_hallucination.py` — 자동 환각 레이블링

**역할**: GPT-4o를 사용하여 LLM-only와 Hybrid RAG 응답의 환각 여부를 자동 판정합니다.

**동작 방식**:
1. `experiment_results.csv`에서 LLM-only, Hybrid RAG 응답 추출 (200개)
2. 각 응답을 `ground_truth_db.json`의 정답과 비교
3. GPT-4o에게 환각 판정 요청
4. 판정 결과: `hallucination`, `normal`, `uncertain`
5. Rule-only는 사전 정의 응답이므로 자동으로 `normal` 처리

**실행 명령어**:
```bash
python auto_label_hallucination.py
```

**출력 파일**: `experiment_results_labeled.csv`

---

### 5-4. `label_hallucination.py` — 수동 환각 레이블링

**역할**: 자동 레이블링 대신 사람이 직접 LLM-only 응답을 검토하여 환각 여부를 판정합니다.

**실행 방식**: 터미널에서 각 응답에 대해 `y(환각)/n(정상)/s(보류)` 입력

```bash
python label_hallucination.py
```

---

### 5-5. `analyze_results.py` — 결과 분석 + 차트

**역할**: 레이블링된 결과를 분석하고 시각화 차트를 생성합니다.

**분석 항목**:
1. 의도 인식 정확도 (시스템별)
2. 환각 발생률 (시스템별)
3. 평균 응답 시간 (시스템별)
4. 카테고리별 정확도 (A_정형 / B_복잡 / C_환각유발)

**실행 명령어**:
```bash
python analyze_results.py
```

**출력 파일**: `experiment_charts.png` (3개 차트: 정확도, 환각률, 응답시간)

---

### 5-6. `fix_rule_only_time.py` — 응답시간 보정

**역할**: Rule-only의 응답 시간을 Dialogflow 추정치(200~400ms)로 보정합니다.

**배경**: Rule-only 실험에서 실제로는 GPT-4o를 사용하여 의도 분류를 했기 때문에, 응답 시간이 실제 Dialogflow와 다릅니다. 이 스크립트로 Dialogflow의 일반적인 응답 시간으로 보정합니다.

```bash
python fix_rule_only_time.py
```

---

### 5-7. `evaluate.py` — 기본 평가 스크립트

**역할**: 기존 8개 테스트 질의(`test_questions.csv`)로 RAG 또는 No-RAG 모드의 정확도를 간단히 측정합니다.

**모드 변경**: 파일 상단의 `TEST_MODE` 변수를 수정
```python
TEST_MODE = "rag"     # RAG 모드로 테스트
TEST_MODE = "no_rag"  # No-RAG 모드로 테스트
```

```bash
python evaluate.py
```

---

## 6. 환경 설정 및 실행 방법

### 6-1. 사전 요구사항

- Python 3.11 이상
- OpenAI API 키 (GPT-4o, text-embedding-3-small 사용)
- pip (Python 패키지 관리자)

### 6-2. 초기 설정 (최초 1회)

```bash
# 1. 프로젝트 클론
git clone https://github.com/jhj1819/hybrid-chatbot-ai.git
cd hybrid-chatbot-ai

# 2. 가상환경 생성 + 활성화 (권장)
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 환경 변수 설정
cp env.example .env
# .env 파일을 열어 OPENAI_API_KEY에 실제 키 입력

# 5. FAISS 벡터 인덱스 생성
python create_vectorstore.py
```

### 6-3. 서버 실행

```bash
python run_server.py
```

실행되면 아래와 같은 메시지가 표시됩니다:
```
🚀 AI 서버를 시작합니다...
📍 호스트: 0.0.0.0
🔌 포트: 8000
👥 워커 수: 1
🌐 외부 접근 URL: http://xxx.xxx.xxx.xxx:8000
📖 API 문서: http://xxx.xxx.xxx.xxx:8000/docs
```

- API 서버: `http://localhost:8000`
- Swagger UI (API 테스트 가능): `http://localhost:8000/docs`
- ReDoc (API 문서): `http://localhost:8000/redoc`

### 6-4. API 테스트 (Python)

```python
import requests

# 헬스 체크
r = requests.get("http://localhost:8000/")
print(r.json())
# → {"status": "AI server is running"}

# RAG 모드 의도 분류
r = requests.post("http://localhost:8000/zeroshot-intent", json={
    "user_question": "환불 절차 알려주세요",
    "intent_list": ["환불_절차_문의", "교환_요청", "배송_조회", "주문_취소"],
    "mode": "rag"
})
print(r.json())
# → {"final_intent": "환불_절차_문의", "bot_response": "...", "engine": "strategy-rag"}

# No-RAG 모드
r = requests.post("http://localhost:8000/zeroshot-intent", json={
    "user_question": "환불 절차 알려주세요",
    "intent_list": ["환불_절차_문의", "교환_요청", "배송_조회", "주문_취소"],
    "mode": "no_rag"
})
print(r.json())
# → {"final_intent": "환불_절차_문의", "bot_response": "...", "engine": "strategy-no_rag"}
```

### 6-5. 전체 실험 실행 순서

```bash
# 1. 서버 실행 (터미널 1)
python run_server.py

# 2. 3-Way 비교 실험 (터미널 2, ~30-60분)
python run_3way_experiment.py

# 3. 자동 환각 레이블링 (~10-15분)
python auto_label_hallucination.py

# 4. Rule-only 응답시간 보정
python fix_rule_only_time.py

# 5. 결과 분석 + 차트 생성
python analyze_results.py
```

---

## 7. Docker 배포

### 7-1. Dockerfile 구성

```dockerfile
FROM python:3.11-slim           # 가벼운 Python 이미지
WORKDIR /app                    # 작업 디렉토리
RUN apt-get install -y gcc ...  # FAISS 빌드에 필요한 시스템 패키지
COPY requirements.txt .         # 의존성 파일 복사
RUN pip install -r requirements.txt  # 패키지 설치
COPY . .                        # 앱 코드 복사
RUN useradd appuser && ...      # 보안을 위한 비루트 사용자
USER appuser
EXPOSE 8000
CMD ["python", "run_server.py"] # 서버 실행
```

### 7-2. Docker Compose 실행

```bash
# 빌드 + 실행 (백그라운드)
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

`docker-compose.yml`은 다음을 설정합니다:
- 포트 8000 노출
- `.env` 파일에서 환경 변수 로드
- `faiss_index/`, `knowledge/` 폴더를 볼륨 마운트
- 30초마다 헬스 체크
- 비정상 종료 시 자동 재시작

### 7-3. Docker 직접 빌드

```bash
# 이미지 빌드
docker build -t hybrid-chatbot-ai .

# 컨테이너 실행
docker run -p 8000:8000 --env-file .env hybrid-chatbot-ai
```

---

## 8. API 명세서

### 8-1. `GET /` — 헬스 체크

서버 동작 상태를 확인합니다.

| 항목 | 값 |
|:---|:---|
| URL | `GET /` |
| 인증 | 불필요 |
| 응답 코드 | 200 OK |

**응답 예시**:
```json
{ "status": "AI server is running" }
```

---

### 8-2. `POST /zeroshot-intent` — 의도 분류

사용자 질문의 의도를 분류합니다. 핵심 API입니다.

| 항목 | 값 |
|:---|:---|
| URL | `POST /zeroshot-intent` |
| Content-Type | `application/json` |
| 인증 | 불필요 |
| 응답 코드 | 200 OK / 400 Bad Request / 500 Server Error |

**요청 파라미터**:

| 필드 | 타입 | 필수 | 기본값 | 설명 |
|:---|:---|:---:|:---|:---|
| `user_question` | string | O | - | 사용자의 질문 |
| `intent_list` | string[] | O | - | 분류 대상 인텐트 목록 |
| `mode` | string | | `"rag"` | 분류 모드 (`"rag"` 또는 `"no_rag"`) |

**요청 예시**:
```json
{
  "user_question": "쿠폰과 세일을 동시에 사용할 수 있나요?",
  "intent_list": [
    "환불_절차_문의", "교환_요청", "배송_조회",
    "쿠폰_및_세일_중복적용_문의", "VIP_정책_문의"
  ],
  "mode": "rag"
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

**에러 응답**:
```json
// 400: 잘못된 모드
{ "detail": "알 수 없는 전략 모드입니다: invalid" }

// 500: 서버 초기화 실패
{ "detail": "전략 공장이 준비되지 않았습니다." }
```

---

### 8-3. `POST /embed` — 임베딩 생성

텍스트를 벡터(숫자 배열)로 변환합니다.

| 항목 | 값 |
|:---|:---|
| URL | `POST /embed` |
| Content-Type | `application/json` |
| 모델 | `text-embedding-3-small` |

**요청 예시**:
```json
{
  "texts": [
    "환불 절차 알려주세요",
    "배송 언제 오나요?"
  ]
}
```

**응답 예시**:
```json
{
  "embeddings": [
    [0.0123, -0.0456, 0.0789, ...],   // 1536차원 벡터
    [-0.0234, 0.0567, -0.089, ...]     // 1536차원 벡터
  ]
}
```

---

## 9. 파일별 상세 설명

### 설정 파일

| 파일 | 설명 |
|:---|:---|
| `.env` | 환경 변수 (API 키 등). **절대 git에 올리지 않음** |
| `env.example` | `.env` 템플릿. 복사해서 사용 |
| `requirements.txt` | Python 패키지 목록과 버전 |
| `.gitignore` | git이 무시할 파일/폴더 패턴 |
| `Dockerfile` | Docker 이미지 빌드 설정 |
| `docker-compose.yml` | Docker Compose 서비스 설정 |

### 주요 패키지 (`requirements.txt`)

| 패키지 | 버전 | 역할 |
|:---|:---|:---|
| `fastapi` | 0.116.2 | 웹 프레임워크 (API 서버) |
| `uvicorn` | 0.35.0 | ASGI 서버 (FastAPI 실행) |
| `openai` | 1.108.0 | OpenAI API 클라이언트 (GPT-4o) |
| `langchain` | 0.3.7 | LLM 오케스트레이션 프레임워크 |
| `langchain-openai` | 0.2.8 | LangChain의 OpenAI 연동 |
| `langchain-community` | 0.3.7 | LangChain 커뮤니티 도구 (FAISS 로더 등) |
| `faiss-cpu` | 1.12.0 | 벡터 유사도 검색 (Facebook AI) |
| `python-dotenv` | 1.1.1 | `.env` 파일 로드 |
| `pydantic` | 2.11.9 | 데이터 검증 (요청/응답 DTO) |
| `requests` | 2.32.5 | HTTP 클라이언트 |
| `numpy` | >=1.26, <2.0 | 수치 연산 (FAISS 내부 사용) |

---

## 10. 명령어 모음 (Quick Reference)

### 서버 관련

```bash
# 서버 실행
python run_server.py

# Docker로 서버 실행
docker-compose up -d

# Docker 로그 확인
docker-compose logs -f

# Docker 중지
docker-compose down
```

### 벡터 인덱스 관련

```bash
# knowledge 파일 확인
ls knowledge/

# FAISS 인덱스 재생성 (knowledge 파일 수정 후 필수)
python create_vectorstore.py
```

### 실험 관련

```bash
# 3-Way 비교 실험 (서버 실행 상태에서)
python run_3way_experiment.py

# 자동 환각 레이블링
python auto_label_hallucination.py

# 수동 환각 레이블링 (터미널 대화형)
python label_hallucination.py

# Rule-only 응답시간 보정
python fix_rule_only_time.py

# 결과 분석 + 차트 생성
python analyze_results.py

# 기본 평가 (8개 질의)
python evaluate.py
```

### Git 관련

```bash
# 상태 확인
git status

# .env가 추적되지 않는지 확인 (아무것도 안 나와야 안전)
git ls-files | grep .env

# 코드에 API 키가 하드코딩되지 않았는지 확인
git log -p | grep "sk-proj"
```

### 환경 설정

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt

# .env 파일 생성
cp env.example .env
```

---

## 11. 트러블슈팅

### "OPENAI_API_KEY가 .env 파일에 설정되지 않았습니다"
- `.env` 파일이 프로젝트 루트에 있는지 확인
- `OPENAI_API_KEY=sk-...` 형태로 올바르게 입력되어 있는지 확인
- 키 앞뒤에 공백이나 따옴표가 없는지 확인

### "ModuleNotFoundError: No module named 'xxx'"
```bash
pip install -r requirements.txt
```
가상환경이 활성화된 상태인지 확인하세요.

### "FAISS 인덱스 로드 실패"
```bash
python create_vectorstore.py
```
`faiss_index/` 폴더에 `index.faiss`, `index.pkl` 파일이 생성되었는지 확인하세요.

### "서버 포트 8000이 이미 사용 중"
- 이전에 실행한 서버가 아직 돌아가고 있을 수 있음
- Windows: `netstat -ano | findstr :8000` 으로 PID 확인 후 `taskkill /F /PID {PID}`
- macOS/Linux: `lsof -i :8000` → `kill {PID}`

### "API 호출 시 timeout"
- 서버가 정상적으로 실행 중인지 확인: `http://localhost:8000/docs`
- GPT-4o API 호출이 느릴 수 있음 (평균 2~3초)
- 네트워크 연결 확인

### Docker 관련
```bash
# 빌드 캐시 초기화
docker-compose build --no-cache

# 모든 컨테이너 + 이미지 정리
docker-compose down --rmi all
```
