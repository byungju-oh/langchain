import chromadb
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from typing import List, Dict
import os
from datetime import datetime
import hashlib

class RAGSystem:
    def __init__(self, google_api_key: str):
        if not google_api_key:
            raise ValueError("Google API 키가 필요합니다")
        
        # 로컬 임베딩 모델 로드
        print("임베딩 모델을 로드중입니다...")
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        print("임베딩 모델 로드 완료!")
        
        # ChromaDB 클라이언트 (로컬)
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.chroma_client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Google AI 설정
        genai.configure(api_key=google_api_key)
        self.llm = genai.GenerativeModel('gemini-1.5-flash')
        
        print("RAG 시스템 초기화 완료!")
    
    def add_documents(self, documents: List[str], metadata: List[Dict] = None):
        """문서들을 벡터 데이터베이스에 추가"""
        if not documents:
            return
        
        print(f"{len(documents)}개 문서를 처리중입니다...")
        
        # 문서 ID 생성
        doc_ids = []
        for i, doc in enumerate(documents):
            doc_hash = hashlib.md5(doc.encode()).hexdigest()[:8]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            doc_ids.append(f"doc_{timestamp}_{i}_{doc_hash}")
        
        # 로컬에서 임베딩 생성
        print("임베딩을 생성중입니다...")
        embeddings = self.embedding_model.encode(documents, show_progress_bar=True).tolist()
        
        # ChromaDB에 저장
        print("벡터 데이터베이스에 저장중입니다...")
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            ids=doc_ids,
            metadatas=metadata or [{"source": "uploaded"} for _ in documents]
        )
        
        print(f"총 {len(documents)}개 문서가 성공적으로 저장되었습니다!")
    
    def search_similar_documents(self, query: str, top_k: int = 3) -> List[str]:
        """쿼리와 유사한 문서 검색"""
        if not query.strip():
            return []
        
        try:
            # 로컬에서 쿼리 임베딩 생성
            query_embedding = self.embedding_model.encode([query]).tolist()
            
            # 유사 문서 검색
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=min(top_k, self.collection.count())
            )
            
            return results['documents'][0] if results['documents'] else []
        
        except Exception as e:
            print(f"검색 중 오류 발생: {e}")
            return []
    
    def generate_answer(self, query: str, context_docs: List[str]) -> str:
        """Google AI Studio API로 답변 생성"""
        if not context_docs:
            return "관련 문서를 찾을 수 없습니다. 먼저 문서를 업로드해주세요."
        
        context = "\n\n".join([f"문서 {i+1}: {doc}" for i, doc in enumerate(context_docs)])
        
        prompt = f"""다음은 사용자가 업로드한 문서들입니다:

{context}

질문: {query}

위 문서들을 참고하여 질문에 답해주세요. 다음 규칙을 따라주세요:
1. 제공된 문서 내용만을 기반으로 답변하세요
2. 문서에 없는 내용은 추측하지 마세요  
3. 한국어로 자세하고 정확하게 답변하세요
4. 답변의 근거가 되는 문서 부분을 언급하세요
5. 확신할 수 없는 경우 "문서에서 명확한 정보를 찾을 수 없습니다"라고 말하세요

답변:"""
        
        try:
            response = self.llm.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"답변 생성 중 오류가 발생했습니다: {str(e)}"
    
    def query(self, question: str) -> Dict:
        """RAG 파이프라인 실행"""
        if not question.strip():
            return {
                "question": question,
                "answer": "질문을 입력해주세요.",
                "source_documents": []
            }
        
        # 1. 관련 문서 검색 (로컬)
        relevant_docs = self.search_similar_documents(question, top_k=3)
        
        # 2. 답변 생성 (Google AI Studio API)
        answer = self.generate_answer(question, relevant_docs)
        
        return {
            "question": question,
            "answer": answer,
            "source_documents": relevant_docs
        }
    
    def get_document_count(self) -> int:
        """저장된 문서 수 반환"""
        try:
            return self.collection.count()
        except:
            return 0