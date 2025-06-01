# 📚 RAG 기반 문서 질의응답 시스템

> **RAG (Retrieval-Augmented Generation)** 기술을 활용한 지능형 문서 분석 및 질의응답 시스템

## 🌟 프로젝트 개요

이 프로젝트는 사용자가 업로드한 문서(PDF, DOCX, TXT)를 AI가 이해하고, 자연어 질문에 대해 문서 내용을 바탕으로 정확한 답변을 제공하는 시스템입니다. 로컬 임베딩 모델과 Google Gemini API를 결합하여 효율적이고 정확한 RAG 시스템을 구현했습니다.

## ✨ 주요 기능

### 🔍 **문서 처리 및 분석**
- **다양한 파일 형식 지원**: PDF, DOCX, TXT 파일 처리
- **지능형 텍스트 청킹**: 의미 단위로 문서를 분할하여 검색 효율성 향상
- **멀티파일 업로드**: 여러 문서를 동시에 처리 가능

### 🤖 **AI 기반 질의응답**
- **자연어 질문 처리**: 일상적인 언어로 문서에 대해 질문 가능
- **컨텍스트 기반 답변**: 업로드된 문서만을 기반으로 한 정확한 답변 생성
- **참고 문서 제공**: 답변의 근거가 되는 원문 내용 함께 제공

### 🌐 **사용자 친화적 인터페이스**
- **Streamlit 웹 앱**: 직관적이고 반응형 웹 인터페이스
- **실시간 상태 표시**: 서버 연결 상태 및 처리 현황 실시간 확인
- **질문 히스토리**: 이전 질문과 답변 내역 관리

## 🏗️ 시스템 아키텍처

```
📂 사용자 문서 업로드
    ↓
📄 문서 처리 (doc.py)
    ├── PDF → PyPDF2
    ├── DOCX → python-docx  
    └── TXT → 인코딩 처리
    ↓
🔤 텍스트 청킹 (의미 단위 분할)
    ↓
🧠 임베딩 생성 (sentence-transformers)
    ↓
💾 벡터 DB 저장 (ChromaDB)
    ↓
❓ 사용자 질문
    ↓
🔍 유사 문서 검색 (코사인 유사도)
    ↓
🤖 답변 생성 (Google Gemini 1.5 Flash)
    ↓
💬 최종 답변 제공
```

## 🚀 기술 스택

### **백엔드**
- **FastAPI**: 고성능 웹 API 프레임워크
- **ChromaDB**: 벡터 데이터베이스 (로컬 저장)
- **Sentence Transformers**: 로컬 임베딩 모델
- **Google Generative AI**: 답변 생성 LLM

### **프론트엔드**
- **Streamlit**: 웹 애플리케이션 인터페이스
- **Requests**: API 통신

### **문서 처리**
- **PyPDF2**: PDF 파일 처리
- **python-docx**: DOCX 파일 처리
- **다중 인코딩 지원**: UTF-8, CP949, Latin-1

## 📋 설치 및 실행

### **1. 환경 설정**

```bash
# 저장소 클론
git clone https://github.com/yourusername/rag-document-qa.git
cd rag-document-qa

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

### **2. 환경 변수 설정**

`.env` 파일을 생성하고 Google API 키를 설정하세요:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

> 📌 **Google API 키 발급**: [Google AI Studio](https://makersuite.google.com/app/apikey)에서 무료로 발급받을 수 있습니다.

### **3. 서버 실행**

```bash
# FastAPI 서버 실행
python main.py

# 새 터미널에서 Streamlit 앱 실행
streamlit run streaml.py
```

### **4. 접속**

- **웹 앱**: http://localhost:8501
- **API 문서**: http://localhost:8000/docs

## 🎯 사용법

### **1단계: 문서 업로드**
1. 웹 앱 사이드바에서 파일 선택
2. PDF, DOCX, TXT 파일을 하나 이상 업로드
3. "문서 처리하기" 버튼 클릭

### **2단계: 질문하기**
1. 메인 화면에서 질문 입력
2. "질문하기" 버튼 클릭
3. AI가 문서를 바탕으로 생성한 답변 확인

### **3단계: 결과 확인**
- 답변과 함께 참고한 문서 내용 확인 가능
- 질문 히스토리에서 이전 대화 내역 확인

## 💡 효과적인 질문 예시

```
✅ 좋은 질문들:
• "이 문서의 주요 내용을 요약해주세요"
• "핵심 결론이나 권장사항은 무엇인가요?"
• "○○에 대해 어떻게 설명하고 있나요?"
• "문서에서 언급된 통계나 수치를 알려주세요"

❌ 피해야 할 질문들:
• 문서에 없는 일반적인 지식에 대한 질문
• 개인적인 의견을 요구하는 질문
• 추측이나 예측을 요구하는 질문
```

## 🛠️ API 엔드포인트

| 메서드 | 엔드포인트 | 설명 |
|--------|------------|------|
| `GET` | `/` | 시스템 상태 페이지 |
| `POST` | `/upload-documents/` | 문서 업로드 및 처리 |
| `POST` | `/ask/` | 질문 처리 및 답변 생성 |
| `GET` | `/status/` | 시스템 현재 상태 조회 |

## 📁 프로젝트 구조

```
rag-document-qa/
├── main.py              # FastAPI 서버
├── streaml.py           # Streamlit 웹 앱
├── doc.py               # 문서 처리 모듈
├── rag.py               # RAG 시스템 핵심 로직
├── requirements.txt     # 의존성 패키지
├── .env                 # 환경 변수 (생성 필요)
├── .gitignore          # Git 제외 파일
├── chroma_db/          # 벡터 DB 저장소 (자동 생성)
└── README.md           # 프로젝트 문서
```

## ⚡ 성능 최적화

- **로컬 임베딩**: sentence-transformers 모델을 로컬에서 실행하여 API 호출 비용 절약
- **영구 저장**: ChromaDB를 이용한 벡터 데이터베이스 로컬 저장
- **청킹 최적화**: 문장 단위로 분할하여 의미 보존
- **비동기 처리**: FastAPI의 비동기 기능으로 성능 향상

## 🔒 보안 및 제한사항

- 모든 데이터는 로컬에 저장되어 개인정보 보호
- Google API 사용량 제한 고려 필요
- 대용량 파일 처리 시 메모리 사용량 증가 가능

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 🙋‍♂️ 지원 및 문의

프로젝트에 대한 질문이나 제안사항이 있으시면 Issues를 통해 연락해주세요.

---

⭐ 이 프로젝트가 도움이 되셨다면 Star를 눌러주세요!
