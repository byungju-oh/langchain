# main.py (업데이트된 버전)
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import os
from typing import List
from doc import DocumentProcessor
from rag import RAGSystem
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 전역 변수
doc_processor = None
rag_system = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # 시작 시 실행
    global doc_processor, rag_system
    
    print("🚀 서버 시작 중...")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise Exception("GOOGLE_API_KEY 환경변수가 설정되지 않았습니다!")
    
    doc_processor = DocumentProcessor()
    rag_system = RAGSystem(google_api_key=api_key)
    
    print("✅ 서버가 성공적으로 시작되었습니다!")
    
    yield  # 서버 실행 중
    
    # 종료 시 실행 (필요한 경우)
    print("🛑 서버를 종료합니다...")

# FastAPI 앱 생성 (lifespan 이벤트 적용)
app = FastAPI(
    title="RAG Document QA System",
    description="문서 업로드 후 AI에게 질문할 수 있는 시스템",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def root():
    """메인 페이지"""
    return """
    <html>
        <head>
            <title>RAG Document QA System</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .feature { background: #f0f0f0; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .endpoint { background: #e8f4f8; padding: 10px; margin: 5px 0; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>📚 RAG Document QA System</h1>
            <p>API가 정상적으로 실행중입니다!</p>
            <div class="feature">
                <h2>🚀 사용 가능한 엔드포인트:</h2>
                <div class="endpoint"><strong>POST /upload-documents/</strong> - 문서 업로드</div>
                <div class="endpoint"><strong>POST /ask/</strong> - 질문하기</div>
                <div class="endpoint"><strong>GET /status/</strong> - 시스템 상태 확인</div>
                <div class="endpoint"><strong>GET /docs</strong> - API 문서</div>
            </div>
            <p><strong>Streamlit 앱 실행:</strong></p>
            <code>streamlit run streamlit_app.py</code>
        </body>
    </html>
    """

@app.post("/upload-documents/")
async def upload_documents(files: List[UploadFile] = File(...)):
    """문서 업로드 및 처리"""
    if not files:
        raise HTTPException(status_code=400, detail="파일을 선택해주세요")
    
    processed_docs = []
    processed_files = []
    errors = []
    
    for file in files:
        try:
            # 파일 내용 읽기
            content = await file.read()
            
            # 파일 처리
            chunks = doc_processor.process_file(content, file.filename)
            processed_docs.extend(chunks)
            processed_files.append({
                "filename": file.filename,
                "chunks": len(chunks),
                "size": len(content)
            })
            
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    if processed_docs:
        # RAG 시스템에 문서 추가
        rag_system.add_documents(processed_docs)
    
    return {
        "message": f"총 {len(processed_files)}개 파일 처리 완료",
        "processed_files": processed_files,
        "total_chunks": len(processed_docs),
        "errors": errors,
        "total_documents_in_db": rag_system.get_document_count()
    }

@app.post("/ask/")
async def ask_question(question: str = Form(...)):
    """질문에 대한 답변 생성"""
    if not question.strip():
        raise HTTPException(status_code=400, detail="질문을 입력해주세요")
    
    result = rag_system.query(question)
    return result

@app.get("/status/")
async def get_status():
    """시스템 상태 확인"""
    return {
        "status": "running",
        "documents_count": rag_system.get_document_count(),
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "llm_model": "gemini-1.5-flash"
    }

# Jupyter에서 실행할 때는 이 부분을 주석 처리하세요
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)