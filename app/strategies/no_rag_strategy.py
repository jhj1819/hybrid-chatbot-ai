# app/strategies/no_rag_strategy.py

from .base import ClassificationStrategy
import openai

class NoRagStrategy(ClassificationStrategy):
    """
    RAG를 사용하지 않고, LLM의 기본 능력만으로 의도를 분류하는 전략입니다.
    """
    def __init__(self, client: openai.OpenAI):
        self.client = client

    def classify(self, user_question: str, intent_list: list[str]) -> str:
        """
        참고 자료 없이, LLM에게 직접 의도 분류를 요청합니다.
        """
        prompt = f"""
당신은 사용자의 질문을 가장 적절한 의도(Intent)로 분류하는 역할을 맡은 AI 어시스턴트입니다.
주어진 '의도 목록' 중에서 사용자의 '질문'과 가장 관련이 높은 의도를 딱 하나만 골라주세요.
다른 설명 없이, 선택한 의도의 이름만 정확하게 답변해야 합니다.

[의도 목록]
{', '.join(intent_list)}

[질문]
{user_question}

[가장 적합한 의도]
"""
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 의도 분류를 수행하는 챗봇입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=50,
        )
        return response.choices[0].message.content.strip()