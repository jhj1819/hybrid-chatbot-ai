# app/main.py
from __future__ import annotations

import os
from dotenv import load_dotenv
import openai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- 우리가 만든 부품들을 불러옵니다 ---
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from app.strategies.factory import StrategyFactory # ✨ 전략 공장 import

from typing import List

# .env 파일 로드
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY가 .env 파일에 설정되지 않았습니다.")

# FastAPI 앱 생성
app = FastAPI(
    title="Hybrid Chatbot AI API",
    description="AI 기반 의도 분류 및 임베딩 생성 API",
    version="1.0.0"
)

# CORS 설정 - 외부 네트워크에서 접근 가능하도록 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한하세요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 시스템 초기화 ---
# 서버가 켜질 때, 모든 부품들을 준비시킵니다.
try:
    # 1. OpenAI 클라이언트 준비
    client = openai.OpenAI(api_key=api_key)
    # 2. RAG를 위한 Retriever 준비
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    retriever = vectorstore.as_retriever(search_kwargs={'k': 3})
    # 3. 전략 공장(StrategyFactory) 건설
    strategy_factory = StrategyFactory(client=client, retriever=retriever)
    print("시스템 초기화 완료: FAISS 인덱스와 전략 공장이 준비되었습니다.")
except Exception as e:
    print(f"시스템 초기화 중 오류 발생: {e}")
    strategy_factory = None

# --- DTO 수정: mode 파라미터 추가 ---
class IntentRequest(BaseModel):
    user_question: str
    intent_list: list[str]
    mode: str = "rag"  # ✨ 'mode' 파라미터를 추가하고, 기본값을 "rag"로 설정

class IntentResponse(BaseModel):
    final_intent: str
    bot_response: str
    engine: str

# --- ✨ 임베딩을 위한 새로운 DTO 추가 ---
class EmbeddingRequest(BaseModel):
    texts: List[str] # 번역할 문장들의 리스트

class EmbeddingResponse(BaseModel):
    embeddings: List[List[float]] # 각 문장에 대한 벡터(숫자 리스트)들의 리스트

# --- API 엔드포인트 ---
@app.get("/")
def read_root():
    return {"status": "AI server is running"}

# --- ✨ 스트래티지 패턴이 적용된 최종 API ---
@app.post("/zeroshot-intent", response_model=IntentResponse)
async def classify_intent_with_strategy(request: IntentRequest):
    if strategy_factory is None:
        raise HTTPException(status_code=500, detail="전략 공장이 준비되지 않았습니다.")

    try:
        # 1. 공장에 mode를 알려주고, 알맞은 전략 부품을 주문합니다.
        strategy = strategy_factory.get_strategy(request.mode)

        # 2. 주문한 전략 부품을 사용하여 의도 분류를 실행합니다.
        classified_intent = strategy.classify(request.user_question, request.intent_list)
        
        # LLM이 목록에 없는 답변을 할 경우의 안전장치
        if classified_intent not in request.intent_list:
            print(f"경고: LLM이 목록에 없는 의도 '{classified_intent}'를 반환했습니다. Fallback을 사용합니다.")
            classified_intent = "Default Fallback Intent"

        return IntentResponse(
            final_intent=classified_intent,
            bot_response=f"'{request.mode}' 모드로 '{classified_intent}' 분류됨",
            engine=f"strategy-{request.mode}"
        )
    except ValueError as e:
        # 공장에서 잘못된 모드라는 에러를 보낸 경우
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 그 외의 모든 에러 처리
        print(f"의도 분류 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="의도 분류 중 서버 오류가 발생했습니다.")
    
@app.post("/embed", response_model=EmbeddingResponse)
async def get_embeddings(request: EmbeddingRequest):
    """
    주어진 텍스트 리스트를 임베딩 벡터 리스트로 변환
    """
    if embeddings is None:
        raise HTTPException(status_code=500, detail="임베딩 모델이 준비되지 않았습니다.")
    try:
        # OpenAI 임베딩 모델을 사용하여 여러 텍스트를 한 번에 벡터로 변환
        embedding_vectors = embeddings.embed_documents(request.texts)
        return EmbeddingResponse(embeddings=embedding_vectors)
    except Exception as e:
        print(f"임베딩 생성 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="임베딩 생성 중 서버 오류가 발생했습니다.")