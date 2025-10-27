# app/strategies/factory.py
from __future__ import annotations

from app.strategies.base import ClassificationStrategy
from app.strategies.no_rag_strategy import NoRagStrategy
from app.strategies.rag_strategy import RagStrategy
import openai
from langchain_core.retrievers import BaseRetriever

class StrategyFactory:
    """
    주어진 모드(mode)에 따라 적절한 의도 분류 전략 객체를 생성하는 공장 클래스입니다.
    """
    def __init__(self, client: openai.OpenAI, retriever: BaseRetriever):
        """
        공장을 초기화할 때, 모든 전략을 만드는 데 필요한 재료들을 미리 받아둡니다.
        """
        self.client = client
        self.retriever = retriever

    def get_strategy(self, mode: str) -> ClassificationStrategy:
        """
        모드 이름을 입력받아, 그에 맞는 전략 부품을 만들어 반환합니다.
        """
        if mode == "rag":
            print("LOG: RagStrategy를 생성합니다.")
            return RagStrategy(self.client, self.retriever)
        elif mode == "no_rag":
            print("LOG: NoRagStrategy를 생성합니다.")
            return NoRagStrategy(self.client)
        else:
            # 만약 알 수 없는 모드가 들어오면, 오류를 발생시켜 잘못된 요청임을 알립니다.
            raise ValueError(f"알 수 없는 전략 모드입니다: {mode}")