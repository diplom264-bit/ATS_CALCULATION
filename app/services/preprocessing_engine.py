"""
Production Preprocessing Engine
Extracts clean text with layout information for any resume format
"""
import fitz  # PyMuPDF
import re
import unicodedata
from typing import Dict, List, Tuple
from pathlib import Path

class PreprocessingEngine:
    """
    Layout-aware document preprocessor
    Extracts text + spatial coordinates + font metadata
    """
    
    def __init__(self):
        self.section_keywords = [
            'SUMMARY', 'OBJECTIVE', 'PROFILE',
            'EXPERIENCE', 'WORK HISTORY', 'EMPLOYMENT',
            'EDUCATION', 'ACADEMIC',
            'SKILLS', 'TECHNICAL SKILLS', 'COMPETENCIES',
            'PROJECTS', 'CERTIFICATIONS', 'ACHIEVEMENTS'
        ]
    
    def process(self, file_path: str) -> Dict:
        """
        Process document and extract structured data
        
        Returns:
            {
                'raw_text': str,
                'clean_text': str,
                'sections': List[Dict],
                'blocks': List[Dict],
                'metadata': Dict
            }
        """
        path = Path(file_path)
        
        if not path.exists():
            return {'error': 'File not found', 'status': 'error'}
        
        ext = path.suffix.lower()
        
        if ext == '.pdf':
            return self._process_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            return self._process_docx(file_path)
        elif ext == '.txt':
            return self._process_txt(file_path)
        else:
            return {'error': 'Unsupported format', 'status': 'error'}
    
    def _process_pdf(self, file_path: str) -> Dict:
        """Process PDF with layout awareness"""
        try:
            doc = fitz.open(file_path)
        except Exception as e:
            return {'error': str(e), 'status': 'error'}
        
        all_blocks = []
        raw_text_parts = []
        page_count = len(doc)
        
        for page_num, page in enumerate(doc):
            # Extract text blocks with metadata
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if block.get("type") == 0:  # Text block
                    bbox = block["bbox"]  # (x0, y0, x1, y1)
                    
                    # Extract text from lines
                    text_parts = []
                    font_sizes = []
                    is_bold = False
                    
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            text_parts.append(span["text"])
                            font_sizes.append(span["size"])
                            
                            # Check if bold
                            font_name = span.get("font", "").lower()
                            if "bold" in font_name or span.get("flags", 0) & 2**4:
                                is_bold = True
                    
                    text = " ".join(text_parts)
                    avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 11
                    
                    all_blocks.append({
                        'text': text,
                        'bbox': bbox,
                        'page': page_num,
                        'font_size': avg_font_size,
                        'is_bold': is_bold,
                        'x0': bbox[0],
                        'y0': bbox[1],
                        'x1': bbox[2],
                        'y1': bbox[3]
                    })
                    
                    raw_text_parts.append(text)
        
        doc.close()
        
        # Sort blocks by reading order (top to bottom, left to right)
        all_blocks.sort(key=lambda b: (b['page'], b['y0'], b['x0']))
        
        # Build raw text
        raw_text = '\n'.join(raw_text_parts)
        
        # Clean text
        clean_text = self._clean_text(raw_text)
        
        # Detect sections
        sections = self._detect_sections(all_blocks, clean_text)
        
        # Metadata
        metadata = {
            'pages': page_count,
            'format': 'pdf',
            'total_blocks': len(all_blocks)
        }
        
        return {
            'raw_text': raw_text,
            'clean_text': clean_text,
            'sections': sections,
            'blocks': all_blocks,
            'metadata': metadata,
            'status': 'ok'
        }
    
    def _process_docx(self, file_path: str) -> Dict:
        """Process DOCX (no layout info available)"""
        try:
            from docx import Document
            doc = Document(file_path)
            
            paragraphs = []
            for para in doc.paragraphs:
                if para.text.strip():
                    paragraphs.append(para.text)
            
            raw_text = '\n'.join(paragraphs)
            clean_text = self._clean_text(raw_text)
            
            # Simple section detection without layout
            sections = self._detect_sections_text_only(clean_text)
            
            return {
                'raw_text': raw_text,
                'clean_text': clean_text,
                'sections': sections,
                'blocks': [],
                'metadata': {'format': 'docx'},
                'status': 'ok'
            }
        except Exception as e:
            return {'error': str(e), 'status': 'error'}
    
    def _process_txt(self, file_path: str) -> Dict:
        """Process TXT"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                raw_text = f.read()
            
            clean_text = self._clean_text(raw_text)
            sections = self._detect_sections_text_only(clean_text)
            
            return {
                'raw_text': raw_text,
                'clean_text': clean_text,
                'sections': sections,
                'blocks': [],
                'metadata': {'format': 'txt'},
                'status': 'ok'
            }
        except Exception as e:
            return {'error': str(e), 'status': 'error'}
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Unicode normalization
        text = unicodedata.normalize('NFKD', text)
        
        # Fix common ligatures
        text = text.replace('ﬁ', 'fi').replace('ﬂ', 'fl')
        
        # Remove page numbers
        text = re.sub(r'Page \d+ of \d+', '', text, flags=re.IGNORECASE)
        
        # Normalize whitespace but preserve structure
        text = re.sub(r' +', ' ', text)  # Multiple spaces to single
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Max 2 newlines
        
        return text.strip()
    
    def _detect_sections(self, blocks: List[Dict], text: str) -> List[Dict]:
        """Detect sections using layout + keywords"""
        if not blocks:
            return []
        
        sections = []
        section_indices = []  # Track which blocks are section headers
        
        # Strategy: Identify section headers first
        avg_font_size = sum(b['font_size'] for b in blocks) / len(blocks)
        
        for i, block in enumerate(blocks):
            text_upper = block['text'].strip().upper()
            
            is_section = False
            section_name = None
            confidence = 0.0
            
            # Check 1: Keyword match
            for keyword in self.section_keywords:
                if keyword in text_upper and len(block['text'].strip()) < 80:
                    is_section = True
                    section_name = keyword
                    confidence = 0.7
                    break
            
            # Check 2: Font-based (bold + larger than average)
            if block['is_bold'] and block['font_size'] > avg_font_size * 1.05:
                if not is_section and len(block['text'].strip()) < 80:
                    is_section = True
                    section_name = text_upper
                confidence = max(confidence, 0.8)
            
            if is_section:
                section_indices.append((i, section_name, confidence, block))
        
        # Now extract content between section headers
        for idx, (i, section_name, confidence, header_block) in enumerate(section_indices):
            # Find next section index
            next_section_idx = section_indices[idx + 1][0] if idx + 1 < len(section_indices) else len(blocks)
            
            # Extract all blocks between this section and next
            section_blocks = blocks[i + 1:next_section_idx]
            section_text = '\n'.join(b['text'] for b in section_blocks)
            
            sections.append({
                'name': section_name,
                'text': section_text.strip(),
                'bbox': header_block['bbox'],
                'confidence': confidence,
                'font_size': header_block['font_size'],
                'is_bold': header_block['is_bold']
            })
        
        return sections
    
    def _detect_sections_text_only(self, text: str) -> List[Dict]:
        """Detect sections without layout info (fallback)"""
        sections = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line_upper = line.strip().upper()
            
            for keyword in self.section_keywords:
                if keyword in line_upper and len(line.strip()) < 50:
                    # Found section header
                    # Extract content until next section
                    content_lines = []
                    for j in range(i + 1, len(lines)):
                        next_line = lines[j].strip().upper()
                        if any(kw in next_line for kw in self.section_keywords) and len(lines[j].strip()) < 50:
                            break
                        content_lines.append(lines[j])
                    
                    sections.append({
                        'name': keyword,
                        'text': '\n'.join(content_lines),
                        'bbox': None,
                        'confidence': 0.7,
                        'font_size': None,
                        'is_bold': None
                    })
                    break
        
        return sections
