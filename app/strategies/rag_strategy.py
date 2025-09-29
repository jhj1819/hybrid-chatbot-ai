# app/strategies/rag_strategy.py

from app.strategies.base import ClassificationStrategy
from langchain_core.retrievers import BaseRetriever
import openai

class RagStrategy(ClassificationStrategy):
    """
    RAG를 사용하여 '의도 설명서'를 참고하여 의도를 분류하는 전략입니다.
    """
    def __init__(self, client: openai.OpenAI, retriever: BaseRetriever):
        self.client = client
        self.retriever = retriever

    def classify(self, user_question: str, intent_list: list[str]) -> str:
        """
        먼저 관련 문서를 검색한 후, 그 내용을 참고하여 LLM에게 의도 분류를 요청합니다.
        """
        # 1. 검색 (Retrieve)
        retrieved_docs = self.retriever.invoke(user_question)
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])

        # 2. 프롬프트 생성 (Augment)
        prompt = f"""
당신은 사용자의 질문 의도를 가장 정확하게 분류하는 AI 어시스턴트입니다.
주어진 [참고 자료]를 깊이 있게 분석하고, 이를 바탕으로 사용자의 [질문]이 [의도 목록] 중 어디에 해당하는지 판단해주세요.
다른 설명 없이, 가장 적합한 의도의 이름 하나만 정확하게 답변해야 합니다.

[참고 자료]
{context}

[의도 목록]
{', '.join(intent_list)}

[질문]
{user_question}

[가장 적합한 의도]
"""
        # 3. 생성 (Generate)
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 RAG를 활용하여 의도를 분류하는 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=50,
        )
        return response.choices[0].message.content.strip()