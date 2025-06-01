import PyPDF2
import docx
from typing import List
import re
import io

class DocumentProcessor:
    def __init__(self):
        pass
    
    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """PDF 바이트에서 텍스트 추출"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"PDF 처리 오류: {e}")
            return ""
    
    def extract_text_from_docx(self, file_content: bytes) -> str:
        """DOCX 바이트에서 텍스트 추출"""
        try:
            doc = docx.Document(io.BytesIO(file_content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            print(f"DOCX 처리 오류: {e}")
            return ""
    
    def extract_text_from_txt(self, file_content: bytes) -> str:
        """TXT 바이트에서 텍스트 추출"""
        try:
            return file_content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return file_content.decode('cp949')
            except UnicodeDecodeError:
                return file_content.decode('latin-1')
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """텍스트를 청크로 분할"""
        if not text or len(text) < chunk_size:
            return [text] if text else []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = min(start + chunk_size, text_length)
            
            # 문장 단위로 자르기 시도
            if end < text_length:
                last_period = text.rfind('.', start, end)
                last_newline = text.rfind('\n', start, end)
                cut_point = max(last_period, last_newline)
                
                if cut_point > start:
                    end = cut_point + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap if end < text_length else end
            
        return chunks

    def process_file(self, file_content: bytes, filename: str) -> List[str]:
        """파일 처리 통합 함수"""
        text = ""
        
        if filename.lower().endswith('.pdf'):
            text = self.extract_text_from_pdf(file_content)
        elif filename.lower().endswith('.docx'):
            text = self.extract_text_from_docx(file_content)
        elif filename.lower().endswith('.txt'):
            text = self.extract_text_from_txt(file_content)
        else:
            raise ValueError(f"지원하지 않는 파일 형식: {filename}")
        
        if not text.strip():
            raise ValueError(f"파일에서 텍스트를 추출할 수 없습니다: {filename}")
        
        return self.chunk_text(text)