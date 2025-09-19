# app/main.py

import os
from dotenv import load_dotenv
import openai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# --- RAG를 위한 도구들을 불러옵니다 ---
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS

# .env 파일 로드 및 OpenAI 클라이언트 초기화
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY가 .env 파일에 설정되지 않았습니다.")
client = openai.OpenAI(api_key=api_key)

# FastAPI 앱 생성
app = FastAPI()

# --- RAG 시스템 초기화 ---
# 서버가 켜질 때, 우리가 만든 faiss_index 파일을 미리 불러옵니다.
try:
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    # 벡터 스토어에서 문서를 검색하는 '검색기(retriever)'를 준비합니다.
    retriever = vectorstore.as_retriever(search_kwargs={'k': 3}) # 가장 유사한 문서 3개를 찾도록 설정
    print("FAISS 인덱스를 성공적으로 불러왔습니다.")
except Exception as e:
    print(f"FAISS 인덱스 로딩 중 오류 발생: {e}")
    retriever = None

# --- DTO 정의 (변경 없음) ---
class IntentRequest(BaseModel):
    user_question: str
    intent_list: list[str]

class IntentResponse(BaseModel):
    final_intent: str
    bot_response: str # Java에서는 이 값을 사용하지 않지만, DTO 형식을 위해 남겨둡니다.
    engine: str

# --- API 엔드포인트 ---
@app.get("/")
def read_root():
    return {"status": "AI server is running"}

# --- ✨ 여기가 바로 RAG로 업그레이드된 의도 분류 API 입니다! ---
@app.post("/zeroshot-intent", response_model=IntentResponse)
async def classify_intent_with_rag(request: IntentRequest):
    if retriever is None:
        raise HTTPException(status_code=500, detail="Retriever(벡터 스토어)가 준비되지 않았습니다.")

    # --- 1. 검색 (Retrieve) ---
    # 사용자 질문과 가장 관련 있는 '의도 설명서' 문서 3개를 찾아옵니다.
    retrieved_docs = retriever.invoke(request.user_question)
    
    # 검색된 문서들의 내용을 하나의 문자열로 합칩니다.
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    # --- 2. 프롬프트 생성 (Augment) ---
    # '검색된 의도 설명서'를 참고자료로 포함하여 LLM에게 보낼 최종 프롬프트를 만듭니다.
    prompt = f"""
당신은 사용자의 질문 의도를 가장 정확하게 분류하는 AI 어시스턴트입니다.
주어진 [참고 자료]를 깊이 있게 분석하고, 이를 바탕으로 사용자의 [질문]이 [의도 목록] 중 어디에 해당하는지 판단해주세요.
다른 설명 없이, 가장 적합한 의도의 이름 하나만 정확하게 답변해야 합니다.

[참고 자료]
{context}

[의도 목록]
{', '.join(request.intent_list)}

[질문]
{request.user_question}

[가장 적합한 의도]
"""

    try:
        # --- 3. 생성 (Generate) - 여기서는 '분류 결과'를 생성합니다 ---
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 RAG를 활용하여 의도를 분류하는 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=50,
        )

        classified_intent = response.choices[0].message.content.strip()

        # LLM이 목록에 없는 답변을 할 경우의 안전장치
        if classified_intent not in request.intent_list:
            print(f"경고: LLM이 목록에 없는 의도 '{classified_intent}'를 반환했습니다. Fallback을 사용합니다.")
            classified_intent = "Default Fallback Intent" # 예: 기본 Fallback 의도로 지정

        return IntentResponse(
            final_intent=classified_intent,
            bot_response=f"RAG를 통해 '{classified_intent}'로 분류됨", # 이 값은 Java에서 사용되지 않음
            engine="rag-intent-classifier"
        )
    except Exception as e:
        print(f"OpenAI API 호출 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="OpenAI API 처리 중 오류가 발생했습니다.")