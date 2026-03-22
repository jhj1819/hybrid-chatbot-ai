"""
환각 레이블링 보조 도구
experiment_results.csv의 llm_only 응답을 ground_truth_db.json과 대조하여
환각 여부를 수동으로 레이블링합니다.
"""

import csv
import json

RESULTS_PATH = "experiment_results.csv"
GT_DB_PATH = "ground_truth_db.json"
OUTPUT_PATH = "experiment_results_labeled.csv"

with open(GT_DB_PATH, 'r', encoding='utf-8') as f:
    gt_db = json.load(f)

with open(RESULTS_PATH, 'r', encoding='utf-8-sig') as f:
    results = list(csv.DictReader(f))

# LLM-only 결과만 필터링
llm_results = [r for r in results if r["system"] == "llm_only"]

print("=" * 60)
print("🔍 환각 레이블링 시작")
print(f"   LLM-only 응답 {len(llm_results)}개를 검토합니다.")
print("   각 응답을 정답 DB와 비교하여 판정해주세요.")
print("   입력: y(환각) / n(정상) / s(판단보류)")
print("=" * 60)

labeled_count = 0
for r in llm_results:
    print(f"\n[{r['id']}] 질의: {r['query']}")
    print(f"  카테고리: {r['category']} / 난이도: {r['difficulty']}")
    print(f"  정답 기준: {r['hallu_check_ref']}")
    print(f"  LLM 응답: {r['response'][:200]}...")

    label = input("  → 환각인가요? (y/n/s): ").strip().lower()

    if label == 'y':
        r['hallucination'] = 'hallucination'
        labeled_count += 1
    elif label == 'n':
        r['hallucination'] = 'normal'
    else:
        r['hallucination'] = 'uncertain'

# 레이블을 원본 results에 반영
llm_map = {r['id']: r['hallucination'] for r in llm_results}
for r in results:
    if r['system'] == 'llm_only' and r['id'] in llm_map:
        r['hallucination'] = llm_map[r['id']]
    elif r['system'] == 'rule_only':
        r['hallucination'] = 'normal'  # Rule-only는 환각 없음
    elif r['system'] == 'hybrid_rag':
        # Hybrid도 검토 필요하지만, 환각이 거의 없을 것으로 예상
        r['hallucination'] = ''  # 별도 검토

# 저장
with open(OUTPUT_PATH, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print(f"\n✅ 레이블링 완료! {labeled_count}개 환각 발견")
print(f"   저장: {OUTPUT_PATH}")
