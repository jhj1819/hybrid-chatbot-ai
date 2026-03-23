# create_vectorstore.py (디버깅 버전)

import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY가 .env 파일에 설정되지 않았습니다.")

loader = DirectoryLoader(
    './knowledge',
    glob="**/*.txt",
    loader_cls=TextLoader,
    loader_kwargs={'encoding': 'utf-8'}
)
documents = loader.load()
print(f"총 {len(documents)}개의 문서를 불러왔습니다.")

# --- ✨ 여기에 디버깅 코드를 추가했습니다! ---
# TextLoader가 실제로 어떤 내용을 읽어왔는지 우리 눈으로 직접 확인해봅니다.
print("--- 불러온 문서 내용 ---")
print(documents)
print("----------------------")


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100
)
texts = text_splitter.split_documents(documents)
print(f"문서를 총 {len(texts)}개의 조각으로 나누었습니다.")

# texts 리스트가 비어있으면 더 진행하지 않고 오류 메시지를 출력합니다.
if not texts:
    raise ValueError("문서 조각이 생성되지 않았습니다. knowledge 폴더의 .txt 파일 내용을 확인해주세요.")

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = FAISS.from_documents(texts, embeddings)

vectorstore.save_local("faiss_index")
print("벡터 데이터베이스 생성이 완료되어 'faiss_index' 폴더에 저장되었습니다.")