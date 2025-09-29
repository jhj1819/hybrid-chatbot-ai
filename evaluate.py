# evaluate.py

import csv
import requests
import time

# --- ✨ [설정] 여기서 테스트하고 싶은 모드를 선택하세요! ---
# "rag" 또는 "no_rag"
TEST_MODE = "no_rag"
# ----------------------------------------------------

# --- 나머지 설정값 ---
API_URL = "http://127.0.0.1:8000/zeroshot-intent"
TEST_FILE = "test_questions.csv"
# ✨ AI 서버에 전달할 전체 의도 목록을 최종 11개로 업데이트합니다.
INTENT_LIST = [
    # 그룹 A: RAG가 해결할 복잡한 의도
    "환불절차문의_VIP혜택",
    "환불금액문의_쿠폰사용",
    "환불혜택문의_등급변경",
    "콜라보상품_중복할인_문의",
    "이벤트_중복할인_문의",
    "콜라보상품_환불_문의",
    # 그룹 B: Dialogflow가 기본적으로 학습할 단순 의도
    "배송_조회",
    "일반_환불_문의",
    "일반_교환_문의",
    "주문_수정",
    "주문_취소"
]

def run_evaluation():
    """
    설정된 모드에 따라 API 성능을 평가하고 정확도를 계산합니다.
    """
    print(f"🤖 AI 모델 성능 평가를 시작합니다... (테스트 모드: {TEST_MODE})")

    test_data = []
    try:
        with open(TEST_FILE, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                test_data.append(row)
    except FileNotFoundError:
        print(f"❌ '{TEST_FILE}' 파일을 찾을 수 없습니다.")
        return

    if not test_data:
        print("❌ 테스트 데이터가 없습니다.")
        return

    correct_predictions = 0
    total_questions = len(test_data)

    for i, item in enumerate(test_data):
        question = item["question"]
        correct_intent = item["correct_intent"]

        # ✨ API에 보낼 데이터에 'mode'를 추가합니다.
        payload = {
            "user_question": question,
            "intent_list": INTENT_LIST,
            "mode": TEST_MODE
        }

        try:
            response = requests.post(API_URL, json=payload)
            response.raise_for_status()

            result = response.json()
            predicted_intent = result["final_intent"]
            engine = result["engine"]

            print(f"\n({i+1}/{total_questions}) 질문: {question}")
            print(f"    - 정답 의도: {correct_intent}")
            print(f"    - AI 예측: {predicted_intent} (엔진: {engine})")

            if predicted_intent == correct_intent:
                correct_predictions += 1
                print("    - 결과: ✅ 정답")
            else:
                print(f"    - 결과: ❌ 오답 (예측: {predicted_intent})")

        except requests.exceptions.RequestException as e:
            print(f"\n({i+1}/{total_questions}) 질문 '{question}'에 대한 API 호출 실패: {e}")

        time.sleep(1)

    accuracy = (correct_predictions / total_questions) * 100 if total_questions > 0 else 0

    print(f"\n\n--- 📊 최종 성능 평가 결과 (모드: {TEST_MODE}) ---")
    print(f"총 질문 수: {total_questions}개")
    print(f"정답 수: {correct_predictions}개")
    print(f"정확도(Accuracy): {accuracy:.2f}%")
    print("---------------------------------------")


if __name__ == "__main__":
    run_evaluation()