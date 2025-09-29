# app/main.py

import os
from dotenv import load_dotenv
import openai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- 우리가 만든 부품들을 불러옵니다 ---
# langchain 관련 import 제거 (의존성 충돌 방지)
# from langchain_openai import OpenAIEmbeddings
# from langchain_community.vectorstores import FAISS
# from app.strategies.factory import StrategyFactory # ✨ 전략 공장 import

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
    # 2. RAG 기능 비활성화 (의존성 충돌 방지)
    embeddings = None
    retriever = None
    strategy_factory = None
    print("시스템 초기화 완료: 기본 OpenAI 클라이언트가 준비되었습니다.")
    print("⚠️  RAG 기능은 비활성화되었습니다. (langchain 의존성 충돌 방지)")
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

# --- ✨ 간단한 의도 분류 API (RAG 없이) ---
@app.post("/zeroshot-intent", response_model=IntentResponse)
async def classify_intent_simple(request: IntentRequest):
    if client is None:
        raise HTTPException(status_code=500, detail="OpenAI 클라이언트가 준비되지 않았습니다.")

    try:
        # 간단한 의도 분류 (RAG 없이)
        prompt = f"""
다음 질문을 주어진 의도 목록 중에서 가장 적절한 하나로 분류해주세요.

질문: {request.user_question}

의도 목록: {', '.join(request.intent_list)}

가장 적절한 의도를 하나만 선택해서 답변해주세요.
"""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.1
        )
        
        classified_intent = response.choices[0].message.content.strip()
        
        # LLM이 목록에 없는 답변을 할 경우의 안전장치
        if classified_intent not in request.intent_list:
            print(f"경고: LLM이 목록에 없는 의도 '{classified_intent}'를 반환했습니다. Fallback을 사용합니다.")
            classified_intent = request.intent_list[0] if request.intent_list else "Default Fallback Intent"

        return IntentResponse(
            final_intent=classified_intent,
            bot_response=f"'{request.mode}' 모드로 '{classified_intent}' 분류됨",
            engine="openai-gpt-3.5-turbo"
        )
    except Exception as e:
        print(f"의도 분류 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="의도 분류 중 서버 오류가 발생했습니다.")
    
@app.post("/embed", response_model=EmbeddingResponse)
async def get_embeddings(request: EmbeddingRequest):
    """
    주어진 텍스트 리스트를 임베딩 벡터 리스트로 변환 (OpenAI API 직접 사용)
    """
    if client is None:
        raise HTTPException(status_code=500, detail="OpenAI 클라이언트가 준비되지 않았습니다.")
    
    try:
        # OpenAI 임베딩 API를 직접 사용
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=request.texts
        )
        
        # 임베딩 벡터 추출
        embedding_vectors = [data.embedding for data in response.data]
        return EmbeddingResponse(embeddings=embedding_vectors)
    except Exception as e:
        print(f"임베딩 생성 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="임베딩 생성 중 서버 오류가 발생했습니다.")