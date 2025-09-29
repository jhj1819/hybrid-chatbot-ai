# app/strategies/base.py

from abc import ABC, abstractmethod

# ABC(Abstract Base Class)를 상속받아, 이 클래스가 '설계도'임을 명시합니다.
class ClassificationStrategy(ABC):
    """
    모든 의도 분류 전략들이 따라야 하는 기본 설계도(추상 클래스)입니다.
    """

    # @abstractmethod는 이 설계도를 사용하는 모든 자식 클래스가
    # 반드시 이 메서드를 직접 구현해야 한다고 강제하는 규칙입니다.
    @abstractmethod
    def classify(self, user_question: str, intent_list: list[str]) -> str:
        """
        사용자의 질문을 분석하여 가장 적합한 의도를 반환합니다.

        :param user_question: 사용자의 원본 질문
        :param intent_list: 분류 대상이 되는 전체 의도 목록
        :return: 분류된 최종 의도 이름 (문자열)
        """
        pass