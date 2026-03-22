"""
실험 결과 분석 + 시각화 차트 생성
"""

import csv
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from collections import Counter, defaultdict

matplotlib.rcParams['font.family'] = 'DejaVu Sans'  # 한글 폰트가 있으면 변경
plt.style.use('seaborn-v0_8-whitegrid')

RESULTS_PATH = "experiment_results_labeled.csv"

with open(RESULTS_PATH, 'r', encoding='utf-8-sig') as f:
    results = list(csv.DictReader(f))

systems = ["rule_only", "llm_only", "hybrid_rag"]
system_labels = {"rule_only": "Rule-only", "llm_only": "LLM-only", "hybrid_rag": "Hybrid (Ours)"}
colors = {"rule_only": "#6699CC", "llm_only": "#CC6666", "hybrid_rag": "#66CC99"}

# ── 1. 의도 인식 정확도 ──
print("=" * 50)
print("📊 1. 의도 인식 정확도")
accuracies = {}
for sys in systems:
    sys_results = [r for r in results if r["system"] == sys]
    correct = sum(1 for r in sys_results if r["intent_correct"] == "1")
    total = len(sys_results)
    acc = correct / total * 100 if total > 0 else 0
    accuracies[sys] = acc
    print(f"  {system_labels[sys]}: {acc:.1f}% ({correct}/{total})")

# ── 2. 환각 발생률 ──
print(f"\n📊 2. 환각 발생률")
hallu_rates = {}
for sys in systems:
    sys_results = [r for r in results if r["system"] == sys]
    hallu = sum(1 for r in sys_results if r.get("hallucination") == "hallucination")
    total = len(sys_results)
    rate = hallu / total * 100 if total > 0 else 0
    hallu_rates[sys] = rate
    print(f"  {system_labels[sys]}: {rate:.1f}% ({hallu}/{total})")

# ── 3. 평균 응답 시간 ──
print(f"\n📊 3. 평균 응답 시간")
avg_times = {}
for sys in systems:
    sys_results = [r for r in results if r["system"] == sys]
    times = [int(r["response_time_ms"]) for r in sys_results if r["response_time_ms"]]
    avg = sum(times) / len(times) if times else 0
    avg_times[sys] = avg
    print(f"  {system_labels[sys]}: {avg:.0f}ms")

# ── 4. 카테고리별 정확도 ──
print(f"\n📊 4. 카테고리별 정확도")
categories = ["A_정형", "B_복잡", "C_환각유발"]
for cat in categories:
    print(f"\n  [{cat}]")
    for sys in systems:
        sys_results = [r for r in results if r["system"] == sys and r["category"] == cat]
        correct = sum(1 for r in sys_results if r["intent_correct"] == "1")
        total = len(sys_results)
        acc = correct / total * 100 if total > 0 else 0
        print(f"    {system_labels[sys]}: {acc:.1f}% ({correct}/{total})")

# ── 차트 생성 ──
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Chart 1: Intent Accuracy
ax1 = axes[0]
bars1 = ax1.bar(
    [system_labels[s] for s in systems],
    [accuracies[s] for s in systems],
    color=[colors[s] for s in systems]
)
ax1.set_title("Intent Recognition Accuracy (%)", fontsize=13, fontweight='bold')
ax1.set_ylim(0, 100)
for bar, val in zip(bars1, [accuracies[s] for s in systems]):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f"{val:.1f}%",
             ha='center', fontsize=11, fontweight='bold')

# Chart 2: Hallucination Rate
ax2 = axes[1]
bars2 = ax2.bar(
    [system_labels[s] for s in systems],
    [hallu_rates[s] for s in systems],
    color=[colors[s] for s in systems]
)
ax2.set_title("Hallucination Rate (%)", fontsize=13, fontweight='bold')
ax2.set_ylim(0, max(hallu_rates.values()) * 1.3 + 5)
for bar, val in zip(bars2, [hallu_rates[s] for s in systems]):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f"{val:.1f}%",
             ha='center', fontsize=11, fontweight='bold')

# Chart 3: Response Time
ax3 = axes[2]
bars3 = ax3.bar(
    [system_labels[s] for s in systems],
    [avg_times[s] for s in systems],
    color=[colors[s] for s in systems]
)
ax3.set_title("Avg Response Time (ms)", fontsize=13, fontweight='bold')
for bar, val in zip(bars3, [avg_times[s] for s in systems]):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20, f"{val:.0f}ms",
             ha='center', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig("experiment_charts.png", dpi=150, bbox_inches='tight')
print(f"\n✅ 차트 저장: experiment_charts.png")
# plt.show()  # GUI 환경에서만 사용
