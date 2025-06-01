import streamlit as st
import requests
import os
from dotenv import load_dotenv
import json

# 환경변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="RAG 문서 질의응답 시스템",
    page_icon="📚",
    layout="wide"
)

# API 엔드포인트
API_BASE = "http://localhost:8000"

def check_api_connection():
    """API 서버 연결 확인"""
    try:
        response = requests.get(f"{API_BASE}/status/", timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except:
        return False, None

def main():
    st.title("📚 RAG 기반 문서 질의응답 시스템")
    st.markdown("문서를 업로드하고 AI에게 자연어로 질문해보세요!")
    
    # API 연결 상태 확인
    is_connected, status_info = check_api_connection()
    
    if not is_connected:
        st.error("⚠️ API 서버에 연결할 수 없습니다. 서버가 실행중인지 확인해주세요.")
        st.code("python main.py")
        st.stop()
    
    # 상태 정보 표시
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("서버 상태", "🟢 연결됨")
    with col2:
        st.metric("저장된 문서", f"{status_info.get('documents_count', 0)}개")
    with col3:
        st.metric("LLM 모델", "Gemini-1.5-Flash")
    
    # 사이드바: 문서 업로드
    with st.sidebar:
        st.header("📁 문서 업로드")
        
        uploaded_files = st.file_uploader(
            "문서를 선택하세요 (PDF, DOCX, TXT)",
            type=['pdf', 'docx', 'txt'],
            accept_multiple_files=True,
            help="여러 파일을 동시에 업로드할 수 있습니다"
        )
        
        if uploaded_files:
            st.write(f"선택된 파일: {len(uploaded_files)}개")
            for file in uploaded_files:
                st.write(f"- {file.name} ({file.size:,} bytes)")
        
        if st.button("📤 문서 처리하기", disabled=not uploaded_files):
            if uploaded_files:
                with st.spinner("문서를 처리중입니다... 잠시만 기다려주세요."):
                    try:
                        # 파일 데이터 준비
                        files_data = []
                        for file in uploaded_files:
                            files_data.append(
                                ("files", (file.name, file.getvalue(), file.type))
                            )
                        
                        # API 호출
                        response = requests.post(
                            f"{API_BASE}/upload-documents/",
                            files=files_data,
                            timeout=120
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success("✅ 문서 처리 완료!")
                            
                            # 처리 결과 표시
                            st.json(result)
                            
                            # 페이지 새로고침을 위한 상태 업데이트
                            st.rerun()
                            
                        else:
                            st.error(f"❌ 문서 처리 실패: {response.text}")
                            
                    except requests.exceptions.Timeout:
                        st.error("⏰ 처리 시간이 너무 오래 걸립니다. 파일 크기를 확인해주세요.")
                    except Exception as e:
                        st.error(f"❌ 오류 발생: {str(e)}")
        
        # 시스템 정보
        with st.expander("🔧 시스템 정보"):
            if status_info:
                st.json(status_info)
    
    # 메인 영역: 질의응답
    st.header("💬 질의응답")
    
    # 문서가 없는 경우 안내
    if status_info and status_info.get('documents_count', 0) == 0:
        st.info("👈 먼저 사이드바에서 문서를 업로드해주세요!")
    
    # 질문 입력
    question = st.text_input(
        "💭 질문을 입력하세요:",
        placeholder="업로드한 문서에 대해 궁금한 것을 물어보세요...",
        help="예: '이 문서의 주요 내용은 무엇인가요?', '핵심 결론을 요약해주세요'"
    )
    
    # 질문 버튼
    col1, col2 = st.columns([1, 4])
    with col1:
        ask_button = st.button("🚀 질문하기", disabled=not question.strip())
    with col2:
        if st.button("🗑️ 질문 지우기"):
            st.rerun()
    
    # 질문 처리
    if ask_button and question.strip():
        with st.spinner("🤖 AI가 답변을 생성중입니다..."):
            try:
                response = requests.post(
                    f"{API_BASE}/ask/",
                    data={"question": question},
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # 답변 표시
                    st.subheader("🤖 AI 답변")
                    st.write(result["answer"])
                    
                    # 참고 문서 표시
                    if result["source_documents"]:
                        with st.expander("📖 참고 문서 (클릭하여 펼치기)"):
                            for i, doc in enumerate(result["source_documents"], 1):
                                st.write(f"**📄 참고 문서 {i}:**")
                                
                                # 문서가 너무 길면 일부만 표시
                                if len(doc) > 500:
                                    st.write(doc[:500] + "...")
                                    with st.expander(f"전체 내용 보기 (문서 {i})"):
                                        st.write(doc)
                                else:
                                    st.write(doc)
                                
                                if i < len(result["source_documents"]):
                                    st.divider()
                    
                    # 질문 히스토리 저장 (세션 상태)
                    if 'qa_history' not in st.session_state:
                        st.session_state.qa_history = []
                    
                    st.session_state.qa_history.append({
                        'question': question,
                        'answer': result["answer"]
                    })
                    
                else:
                    st.error(f"❌ 답변 생성 실패: {response.text}")
                    
            except requests.exceptions.Timeout:
                st.error("⏰ 답변 생성 시간이 너무 오래 걸립니다. 다시 시도해주세요.")
            except Exception as e:
                st.error(f"❌ 오류 발생: {str(e)}")
    
    # 질문 히스토리
    if 'qa_history' in st.session_state and st.session_state.qa_history:
        st.subheader("📝 질문 히스토리")
        
        for i, qa in enumerate(reversed(st.session_state.qa_history[-5:]), 1):
            with st.expander(f"Q{len(st.session_state.qa_history) - i + 1}: {qa['question'][:50]}..."):
                st.write(f"**질문:** {qa['question']}")
                st.write(f"**답변:** {qa['answer']}")
        
        if st.button("🗑️ 히스토리 지우기"):
            st.session_state.qa_history = []
            st.rerun()
    
    # 사용법 안내
    with st.expander("📋 시스템 사용법"):
        st.markdown("""
        ### 🚀 빠른 시작 가이드
        
        1. **📁 문서 업로드**
           - 사이드바에서 PDF, DOCX, TXT 파일을 선택하세요
           - 여러 파일을 동시에 업로드할 수 있습니다
           - '문서 처리하기' 버튼을 클릭하세요
        
        2. **💬 질문하기**
           - 업로드한 문서 내용에 대해 자연어로 질문하세요
           - 구체적이고 명확한 질문일수록 좋은 답변을 얻을 수 있습니다
        
        3. **📖 답변 확인**
           - AI가 문서를 바탕으로 생성한 답변을 확인하세요
           - '참고 문서' 섹션에서 답변의 근거를 확인할 수 있습니다
        
        ### 💡 효과적인 질문 예시
        - "이 문서의 주요 내용을 요약해주세요"
        - "핵심 결론이나 권장사항은 무엇인가요?"
        - "특정 개념에 대해 어떻게 설명하고 있나요?"
        - "문서에서 언급된 통계나 수치를 알려주세요"
        
        ### ⚠️ 주의사항
        - 문서에 없는 내용은 AI가 추측하지 않습니다
        - 대용량 파일은 처리에 시간이 걸릴 수 있습니다
        - API 호출 제한으로 인해 빈번한 질문 시 지연될 수 있습니다
        """)

if __name__ == "__main__":
    main()