"""
자동 환각 레이블링 도구
GPT-4o를 사용하여 experiment_results.csv의 LLM-only/Hybrid 응답을
ground_truth_db.json과 대조하여 환각 여부를 자동 판정합니다.
"""

import csv
import json
import time
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

RESULTS_PATH = "experiment_results.csv"
GT_DB_PATH = "ground_truth_db.json"
OUTPUT_PATH = "experiment_results_labeled.csv"

with open(GT_DB_PATH, 'r', encoding='utf-8') as f:
    gt_db = json.load(f)

with open(RESULTS_PATH, 'r', encoding='utf-8-sig') as f:
    results = list(csv.DictReader(f))

gt_text = json.dumps(gt_db, ensure_ascii=False, indent=2)


def check_hallucination(query: str, response: str, hallu_ref: str) -> str:
    """GPT-4o를 사용하여 응답의 환각 여부를 판정"""
    try:
        result = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "당신은 챗봇 응답의 환각(hallucination) 여부를 판정하는 전문가입니다.\n"
                        "아래 정답 DB(ground truth)를 기준으로, 챗봇 응답이 사실과 다른 정보를 포함하는지 판단하세요.\n\n"
                        f"[정답 DB]\n{gt_text}\n\n"
                        "판정 기준:\n"
                        "- hallucination: 정답 DB에 없는 정보를 사실처럼 언급하거나, 정답 DB와 모순되는 내용이 있는 경우\n"
                        "- normal: 정답 DB의 내용과 일치하거나, 일반적인 안내 수준의 응답인 경우\n"
                        "- uncertain: 판단하기 어려운 경우\n\n"
                        "반드시 'hallucination', 'normal', 'uncertain' 중 하나만 출력하세요."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"[사용자 질문] {query}\n"
                        f"[환각 체크 기준] {hallu_ref}\n"
                        f"[챗봇 응답] {response}\n\n"
                        "이 응답은 환각인가요?"
                    )
                }
            ],
            max_tokens=10,
            temperature=0
        )
        answer = result.choices[0].message.content.strip().lower()
        if "hallucination" in answer:
            return "hallucination"
        elif "normal" in answer:
            return "normal"
        else:
            return "uncertain"
    except Exception as e:
        print(f"  ⚠️ API 오류: {e}")
        return "uncertain"


# LLM-only와 hybrid_rag 결과에 대해 환각 판정
targets = [r for r in results if r["system"] in ("llm_only", "hybrid_rag")]
print("=" * 60)
print(f"🔍 자동 환각 레이블링 시작 ({len(targets)}개 응답 검토)")
print("=" * 60)

hallu_count = {"llm_only": 0, "hybrid_rag": 0}
total_count = {"llm_only": 0, "hybrid_rag": 0}

for i, r in enumerate(targets):
    sys_name = r["system"]
    total_count[sys_name] += 1

    label = check_hallucination(r["query"], r["response"], r["hallu_check_ref"])
    r["hallucination"] = label

    if label == "hallucination":
        hallu_count[sys_name] += 1

    status = "🔴" if label == "hallucination" else ("🟢" if label == "normal" else "🟡")
    print(f"  [{i+1}/{len(targets)}] {sys_name} | {status} {label} | {r['query'][:40]}...")

    time.sleep(0.3)

# Rule-only는 사전 정의 응답이므로 환각 없음
for r in results:
    if r["system"] == "rule_only":
        r["hallucination"] = "normal"

# 저장
with open(OUTPUT_PATH, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print(f"\n{'=' * 60}")
print(f"✅ 자동 레이블링 완료!")
print(f"   Rule-only: 환각 0개 (사전 정의 응답)")
print(f"   LLM-only: 환각 {hallu_count['llm_only']}/{total_count['llm_only']}개")
print(f"   Hybrid RAG: 환각 {hallu_count['hybrid_rag']}/{total_count['hybrid_rag']}개")
print(f"   저장: {OUTPUT_PATH}")
