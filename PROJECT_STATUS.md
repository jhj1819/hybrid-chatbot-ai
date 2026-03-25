# Hybrid Chatbot AI - 프로젝트 현황 브리핑

> 이 문서는 전략 수립 AI에게 현재 프로젝트 상태를 전달하기 위한 핸드오프 문서입니다.

---

## 1. 프로젝트 개요

**목표:** 온라인 쇼핑몰 고객센터 챗봇에서 Rule-only(Dialogflow), LLM-only(GPT-4o), Hybrid RAG 세 가지 아키텍처를 비교하여, Hybrid RAG의 우위를 정량적으로 입증하는 것.

**기술 스택:** FastAPI + GPT-4o + FAISS 벡터 검색 + LangChain + Strategy Pattern

**레포지토리:** hybrid-chatbot-ai (AI 서버), hybrid-chatbot-backend (백엔드), hybrid-chatbot-frontend (프론트엔드)

---

## 2. 현재 진행 상태

### 완료된 작업

| 단계 | 작업 | 산출물 | 상태 |
|------|------|--------|------|
| 1 | AI 서버 개발 | `app/main.py`, Strategy Pattern 구현 | 완료 |
| 2 | Knowledge Base 구축 | `knowledge/` 폴더 (10개 정책 문서) | 완료 |
| 3 | FAISS 벡터 인덱스 생성 | `faiss_index/index.faiss` | 완료 |
| 4 | 테스트 데이터셋 설계 | `test_dataset.csv` (100개 질의) | 완료 |
| 5 | 정답 DB 구축 | `ground_truth_db.json` (8개 정책, 51개 규정) | 완료 |
| 6 | 3-Way 비교 실험 실행 | `experiment_results.csv` (300행) | 완료 |
| 7 | 자동 환각 레이블링 | `experiment_results_labeled.csv` | 완료 |
| 8 | 응답시간 보정 | `fix_rule_only_time.py` 실행 완료 | 완료 |
| 9 | 결과 분석 및 차트 생성 | `experiment_charts.png` | 완료 |
| 10 | 실험 보고서 작성 | `EXPERIMENT_REPORT.md` | 완료 |

### 미완료 / 추가 가능한 작업

| 작업 | 설명 | 우선순위 |
|------|------|----------|
| 논문/발표자료 작성 | 실험 결과를 학술적 형식으로 정리 | 미정 |
| 실서비스 배포 | AWS App Runner/EC2 배포 (스크립트는 준비됨) | 미정 |
| 프론트엔드-백엔드 통합 테스트 | 3개 레포 연동 테스트 | 미정 |
| Dialogflow 실제 연동 | 시뮬레이션 → 실제 Dialogflow 연결 | 미정 |
| 추가 실험 | 데이터셋 확장, 다른 LLM 모델 비교 등 | 미정 |

---

## 3. 실험 결과 요약 (3-Way 비교)

### 핵심 수치

| 지표 | Rule-only | LLM-only | Hybrid RAG (Ours) |
|------|-----------|----------|-------------------|
| 의도 인식 정확도 | 73.0% | 73.0% | **85.0%** |
| 환각 발생률 | 0.0% | 30.0% | **5.0%** |
| 평균 응답시간 | 299ms | 2,896ms | **1,935ms** |

### 카테고리별 정확도

| 카테고리 | 설명 | Rule-only | LLM-only | Hybrid RAG |
|----------|------|-----------|----------|------------|
| A_정형 (40개) | 단순 질문 | 90.0% | 90.0% | 90.0% |
| B_복잡 (35개) | 복합 질문 | 65.7% | 68.6% | **77.1%** |
| C_환각유발 (25개) | 함정 질문 | 56.0% | 52.0% | **88.0%** |

### 핵심 발견

1. **Hybrid RAG가 어려운 질문에서 압도적 우위** — C_환각유발에서 32~36%p 차이
2. **LLM에게 응답 생성을 맡기면 30%가 환각** — RAG 없이 LLM만 쓰는 것은 위험
3. **Hybrid는 속도-정확도 균형 달성** — 쉬운 질문은 Dialogflow(~300ms), 어려운 질문만 RAG+LLM(~3초)

### 실험 설계의 주의점

- Rule-only/Hybrid는 **의도 분류만** LLM이 수행하고 응답은 시스템이 구성
- LLM-only만 **응답 생성까지** LLM이 직접 수행 (환각 비교는 동일 조건이 아님)
- Rule-only는 실제 Dialogflow가 아닌 GPT-4o no_rag 모드로 시뮬레이션
- 환각 판정은 GPT-4o를 심판으로 사용 (LLM-as-a-Judge)

---

## 4. 시스템 아키텍처 현황

```
[프론트엔드] ──→ [백엔드 서버] ──→ [AI 서버 (이 레포)]
                    │                    │
                    │                    ├─ /zeroshot-intent (mode=rag)
                    │                    │   └─ FAISS 검색 + GPT-4o 의도 분류
                    │                    │
                    │                    ├─ /zeroshot-intent (mode=no_rag)
                    │                    │   └─ GPT-4o 의도 분류 (참고자료 없이)
                    │                    │
                    │                    └─ /embed
                    │                        └─ 텍스트 임베딩 생성
                    │
                    └─ Dialogflow (Google NLP)
                        └─ 1차 의도 분류 + confidence 판단
```

**실제 운영 흐름:**
1. 사용자 질문 → Dialogflow가 1차 분류
2. confidence 높으면 → 백엔드가 정해진 응답 반환 (빠름)
3. confidence 낮으면 → AI 서버 RAG 모드로 2차 분류 → 백엔드가 응답 구성

---

## 5. 파일 구조 및 역할

### 핵심 코드
```
app/
├── main.py                    # FastAPI 앱 (엔드포인트 정의)
└── strategies/
    ├── base.py                # 전략 추상 클래스
    ├── factory.py             # 전략 팩토리 (rag/no_rag 선택)
    ├── rag_strategy.py        # RAG 전략 (FAISS 검색 + GPT-4o)
    └── no_rag_strategy.py     # No-RAG 전략 (GPT-4o만)
```

### 실험 관련
```
run_3way_experiment.py         # 3-Way 비교 실험 실행
auto_label_hallucination.py    # GPT-4o 자동 환각 레이블링
label_hallucination.py         # 수동 환각 레이블링
fix_rule_only_time.py          # 응답시간 보정
analyze_results.py             # 결과 분석 + 차트 생성
```

### 데이터
```
test_dataset.csv               # 테스트 질의 100개
ground_truth_db.json           # 정답 정책 DB (51개 규정)
intent_list.json               # 의도 목록 (10개)
experiment_results.csv         # 실험 원본 결과
experiment_results_labeled.csv # 환각 레이블 포함 최종 결과
experiment_charts.png          # 시각화 차트
```

### Knowledge Base (RAG 검색 대상)
```
knowledge/
├── refund_procedure.txt       # 환불 절차
├── exchange_policy.txt        # 교환 정책
├── delivery_policy.txt        # 배송 정책
├── order_cancel_policy.txt    # 주문취소 정책
├── coupon_policy.txt          # 쿠폰 정책
├── vip_policy.txt             # VIP 정책
├── point_policy.txt           # 적립금 정책
├── collaboration_policy.txt   # 콜라보 정책
├── intent_쿠폰_및_세일_중복적용_문의.txt
└── intent_특별세일_상품_환불_문의.txt
```

### 문서
```
README.md                      # 프로젝트 소개
GUIDE.md                       # 상세 가이드 (아키텍처, API, 사용법)
EXPERIMENT_REPORT.md           # 실험 보고서 (방법론, 결과, 분석)
TECH_STACK.md                  # 기술 스택 정리
```

### 배포 (준비됨, 미실행)
```
Dockerfile, docker-compose.yml
deploy.sh, deploy-ec2.sh, deploy-apprunner.sh
.github/workflows/             # CI/CD 파이프라인
```

---

## 6. 현재 이슈 및 한계

1. **Rule-only 시뮬레이션:** 실제 Dialogflow 대신 GPT-4o no_rag로 대체. 실제 Dialogflow 연동 시 결과가 달라질 수 있음.
2. **Hybrid uncertain 88%:** AI 서버가 분류 결과 문자열만 반환하므로 환각 심판이 판정 어려움. 실제 백엔드 응답 기준으로 재평가 필요할 수 있음.
3. **데이터셋 규모:** 100개 질의로 통계적 유의성이 제한적. 확장 시 더 신뢰성 있는 결과 가능.
4. **단일 LLM 의존:** GPT-4o만 사용. Claude, Gemini 등 다른 모델 비교 미수행.
5. **비용:** 실험 1회 실행에 약 $1-3 (GPT-4o API), 환각 레이블링에 추가 $1-2.

---

## 7. 전략 수립 시 고려사항

- 이 프로젝트는 **연구/실험 단계가 완료**된 상태
- 다음 단계는 **결과 활용** (논문, 발표, 실서비스 적용 등)
- 3개 레포(AI, 백엔드, 프론트엔드)가 분리되어 있으며, 이 레포는 AI 서버 + 실험에 집중
- 배포 인프라(Docker, AWS 스크립트, CI/CD)는 이미 준비되어 있음
