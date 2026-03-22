"""
3-Way 비교 실험: Rule-only vs LLM-only vs Hybrid
- Rule-only: Dialogflow만 (Confidence 무시, NLP 응답만)
- LLM-only: GPT-4o에 직접 질문 → 응답 생성 (환각 가능)
- Hybrid: 기존 시스템 (Confidence 기반 분기 + RAG/No-RAG Strategy)
"""

import csv
import json
import time
import requests
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ── 설정 ──
AI_SERVER_URL = "http://localhost:8000"
DATASET_PATH = "test_dataset.csv"
INTENT_LIST_PATH = "intent_list.json"
OUTPUT_PATH = "experiment_results.csv"

with open(INTENT_LIST_PATH, 'r', encoding='utf-8') as f:
    INTENT_LIST = json.load(f)["intent_list"]


def call_hybrid(query: str, mode: str = "rag") -> dict:
    """기존 하이브리드 시스템 호출 (RAG 또는 No-RAG)"""
    start = time.time()
    try:
        resp = requests.post(
            f"{AI_SERVER_URL}/zeroshot-intent",
            json={
                "user_question": query,
                "intent_list": INTENT_LIST,
                "mode": mode
            },
            timeout=30
        )
        elapsed = time.time() - start
        data = resp.json()
        return {
            "detected_intent": data.get("final_intent", ""),
            "response": data.get("bot_response", ""),
            "engine": data.get("engine", ""),
            "response_time_ms": round(elapsed * 1000)
        }
    except Exception as e:
        return {
            "detected_intent": "ERROR",
            "response": str(e),
            "engine": "error",
            "response_time_ms": 0
        }


def call_llm_only(query: str) -> dict:
    """
    LLM-only: GPT-4o에 직접 질문하여 응답 생성
    ⚠️ 이것은 환각을 유발할 수 있는 비교 대상임
    """
    start = time.time()
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "당신은 온라인 쇼핑몰 고객센터 챗봇입니다. "
                        "고객의 질문에 친절하고 구체적으로 답변해주세요. "
                        "환불, 교환, 배송, 쿠폰 등에 대해 안내합니다."
                    )
                },
                {"role": "user", "content": query}
            ],
            max_tokens=300,
            temperature=0.3
        )
        elapsed = time.time() - start
        answer = response.choices[0].message.content

        # 의도 분류도 별도 수행 (비교용)
        intent_resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"사용자 질문의 의도를 다음 목록 중 하나로 분류하세요. "
                        f"의도 목록: {INTENT_LIST}\n"
                        f"반드시 목록에 있는 의도 중 하나만 출력하세요. 다른 말은 하지 마세요."
                    )
                },
                {"role": "user", "content": query}
            ],
            max_tokens=50,
            temperature=0
        )
        detected = intent_resp.choices[0].message.content.strip()

        return {
            "detected_intent": detected,
            "response": answer,
            "engine": "llm-only-gpt4o",
            "response_time_ms": round(elapsed * 1000)
        }
    except Exception as e:
        return {
            "detected_intent": "ERROR",
            "response": str(e),
            "engine": "error",
            "response_time_ms": 0
        }


def call_rule_only(query: str) -> dict:
    """
    Rule-only: Dialogflow만 사용하는 것을 시뮬레이션
    → AI 서버의 No-RAG 모드를 사용하되, 응답은 "NLP 직접 응답"으로 제한
    → 실제로는 Dialogflow가 필요하지만, 여기서는 AI 서버로 의도만 분류하고
      "사전 정의된 응답"을 반환하는 것으로 시뮬레이션
    """
    start = time.time()
    try:
        # 의도 분류는 AI 서버의 no_rag 모드 사용
        resp = requests.post(
            f"{AI_SERVER_URL}/zeroshot-intent",
            json={
                "user_question": query,
                "intent_list": INTENT_LIST,
                "mode": "no_rag"
            },
            timeout=30
        )
        elapsed = time.time() - start
        data = resp.json()
        detected = data.get("final_intent", "")

        # Rule-only는 사전 정의된 응답만 반환 (knowledge DB에서)
        # 실제 Dialogflow 시뮬레이션
        rule_responses = {
            "환불_절차_문의": "마이페이지 > 주문내역에서 환불 신청이 가능합니다. 수령 후 7일 이내, 미개봉 상태에서 신청해주세요.",
            "교환_요청": "마이페이지 > 주문내역에서 교환 접수가 가능합니다. 수령 후 7일 이내, 미착용 상태여야 합니다.",
            "배송_조회": "마이페이지 > 주문내역에서 배송 현황을 확인할 수 있습니다.",
            "주문_취소": "마이페이지 > 주문내역에서 배송 전 주문 취소가 가능합니다.",
            "쿠폰_및_세일_중복적용_문의": "쿠폰은 결제 페이지에서 선택 적용할 수 있습니다. 일부 쿠폰만 세일과 병행 가능합니다.",
            "특별세일_상품_환불_문의": "세일 상품도 환불 가능합니다. 실결제 금액 기준으로 환불됩니다.",
            "VIP_정책_문의": "VIP 등급 및 혜택은 마이페이지 > 회원등급에서 확인하실 수 있습니다.",
            "적립금_문의": "적립금은 마이페이지 > 적립금에서 확인 가능합니다. 1,000원 이상 보유 시 사용 가능합니다.",
            "상품_문의": "해당 상품 페이지에서 상세 정보를 확인하시거나, 고객센터로 문의해주세요.",
            "결제_문의": "결제 관련 문의는 고객센터(1588-0000)로 연락 부탁드립니다."
        }

        response_text = rule_responses.get(detected, "죄송합니다. 해당 문의에 대한 답변을 찾지 못했습니다. 고객센터로 문의해주세요.")

        return {
            "detected_intent": detected,
            "response": response_text,
            "engine": "rule-only-simulated",
            "response_time_ms": round(elapsed * 1000)
        }
    except Exception as e:
        return {
            "detected_intent": "ERROR",
            "response": str(e),
            "engine": "error",
            "response_time_ms": 0
        }


def run_experiment():
    """메인 실험 실행"""
    # 데이터셋 로드
    with open(DATASET_PATH, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        dataset = list(reader)

    print(f"📊 테스트셋 로드: {len(dataset)}개 질의")
    print(f"📋 인텐트 목록: {len(INTENT_LIST)}개")
    print("=" * 60)

    results = []
    systems = [
        ("rule_only", call_rule_only),
        ("llm_only", call_llm_only),
        ("hybrid_rag", lambda q: call_hybrid(q, "rag")),
    ]

    for i, row in enumerate(dataset):
        query = row["query"]
        gt_intent = row["gt_intent"]
        category = row["category"]
        difficulty = row["difficulty"]

        print(f"\n[{i+1}/{len(dataset)}] {query}")

        for system_name, system_fn in systems:
            result = system_fn(query)
            intent_correct = 1 if result["detected_intent"] == gt_intent else 0

            results.append({
                "id": row["id"],
                "query": query,
                "category": category,
                "difficulty": difficulty,
                "gt_intent": gt_intent,
                "system": system_name,
                "detected_intent": result["detected_intent"],
                "intent_correct": intent_correct,
                "response": result["response"],
                "engine": result["engine"],
                "response_time_ms": result["response_time_ms"],
                "hallu_check_ref": row["hallu_check_ref"],
                "hallucination": "",  # ← 수동 레이블링 필요
            })

            status = "✅" if intent_correct else "❌"
            print(f"  {system_name}: {result['detected_intent']} {status} ({result['response_time_ms']}ms)")

    # 결과 저장
    with open(OUTPUT_PATH, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"\n{'=' * 60}")
    print(f"✅ 실험 완료! 결과 저장: {OUTPUT_PATH}")
    print(f"총 {len(results)}개 결과 ({len(dataset)} 질의 × {len(systems)} 시스템)")

    # 간단 요약
    print(f"\n📊 의도 인식 정확도 요약:")
    for sys_name, _ in systems:
        sys_results = [r for r in results if r["system"] == sys_name]
        correct = sum(r["intent_correct"] for r in sys_results)
        total = len(sys_results)
        acc = correct / total * 100 if total > 0 else 0
        avg_time = sum(r["response_time_ms"] for r in sys_results) / total if total > 0 else 0
        print(f"  {sys_name}: {acc:.1f}% ({correct}/{total}), 평균 {avg_time:.0f}ms")


if __name__ == "__main__":
    run_experiment()
