"""
Universal File Parser - Extracts text from PDF/DOCX/TXT
"""
import re
from pathlib import Path
from typing import Dict

class FileParser:
    """Universal text extractor for resumes and JDs"""
    
    @staticmethod
    def parse(file_path: str) -> Dict:
        """
        Extract text from file
        
        Returns:
            {'text': str, 'format': str, 'status': str}
        """
        path = Path(file_path)
        
        if not path.exists():
            return {'text': '', 'format': 'unknown', 'status': 'error', 'error': 'File not found'}
        
        ext = path.suffix.lower()
        
        try:
            if ext == '.pdf':
                text = FileParser._parse_pdf(file_path)
            elif ext in ['.docx', '.doc']:
                text = FileParser._parse_docx(file_path)
            elif ext == '.txt':
                text = FileParser._parse_txt(file_path)
            else:
                return {'text': '', 'format': ext, 'status': 'error', 'error': 'Unsupported format'}
            
            # Clean text
            text = FileParser._clean_text(text)
            
            return {
                'text': text,
                'format': ext[1:],
                'status': 'ok',
                'length': len(text)
            }
        except Exception as e:
            return {'text': '', 'format': ext[1:], 'status': 'error', 'error': str(e)}
    
    @staticmethod
    def _parse_pdf(file_path: str) -> str:
        """Extract text from PDF"""
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                text = '\n'.join(page.extract_text() or '' for page in pdf.pages)
            return text
        except:
            # Fallback to PyPDF2
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = '\n'.join(page.extract_text() for page in reader.pages)
            return text
    
    @staticmethod
    def _parse_docx(file_path: str) -> str:
        """Extract text from DOCX"""
        from docx import Document
        doc = Document(file_path)
        return '\n'.join(para.text for para in doc.paragraphs)
    
    @staticmethod
    def _parse_txt(file_path: str) -> str:
        """Extract text from TXT"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean and normalize text"""
        # Remove common headers/footers
        text = re.sub(r'Page \d+ of \d+', '', text, flags=re.IGNORECASE)
        # Normalize line breaks but preserve structure
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        # Don't collapse all whitespace - preserve line structure
        return text.strip()
