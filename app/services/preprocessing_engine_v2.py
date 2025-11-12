"""
Preprocessing Engine V2
Line-level extraction with multi-signal section detection
"""
import fitz
import re
import unicodedata
from typing import Dict, List, Tuple
from pathlib import Path

class PreprocessingEngineV2:
    """
    Production preprocessing with:
    1. Line-level extraction (not block-level)
    2. Multi-signal section detection
    3. Proper reading order
    4. Confidence scoring
    """
    
    def __init__(self):
        self.section_keywords = [
            'summary', 'objective', 'profile',
            'experience', 'work', 'employment',
            'education', 'academic', 'qualification',
            'skills', 'technical', 'competencies',
            'projects', 'certifications', 'awards'
        ]
    
    def process(self, file_path: str) -> Dict:
        """Process document and extract structured data"""
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
        """Process PDF with line-level extraction"""
        try:
            doc = fitz.open(file_path)
        except Exception as e:
            return {'error': str(e), 'status': 'error'}
        
        all_lines = []
        page_count = len(doc)
        
        # Extract lines (not blocks)
        for page_num, page in enumerate(doc):
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if block.get("type") != 0:  # Skip non-text blocks
                    continue
                
                for line in block.get("lines", []):
                    bbox = line["bbox"]
                    
                    # Extract text and font info from spans
                    line_text = ""
                    font_sizes = []
                    is_bold = False
                    
                    for span in line.get("spans", []):
                        line_text += span["text"]
                        font_sizes.append(span["size"])
                        
                        # Check if bold
                        font_name = span.get("font", "").lower()
                        if "bold" in font_name or span.get("flags", 0) & 2**4:
                            is_bold = True
                    
                    if not line_text.strip():
                        continue
                    
                    avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 11
                    
                    all_lines.append({
                        'text': line_text.strip(),
                        'bbox': bbox,
                        'page': page_num,
                        'font_size': avg_font_size,
                        'is_bold': is_bold,
                        'x0': bbox[0],
                        'y0': bbox[1],
                        'x1': bbox[2],
                        'y1': bbox[3]
                    })
        
        doc.close()
        
        # Sort by reading order (top to bottom, left to right)
        all_lines.sort(key=lambda l: (l['page'], l['y0'], l['x0']))
        
        # Calculate average font size
        avg_font_size = sum(l['font_size'] for l in all_lines) / len(all_lines) if all_lines else 11
        
        # Detect section headers with confidence
        for i, line in enumerate(all_lines):
            prev_line = all_lines[i-1] if i > 0 else None
            next_line = all_lines[i+1] if i < len(all_lines) - 1 else None
            
            is_header, confidence = self._is_section_header(
                line, avg_font_size, prev_line, next_line
            )
            
            line['is_section_header'] = is_header
            line['section_confidence'] = confidence
        
        # Build clean text
        clean_text = self._build_clean_text(all_lines)
        
        # Extract sections
        sections = self._extract_sections(all_lines)
        
        # Metadata
        metadata = {
            'pages': page_count,
            'format': 'pdf',
            'total_lines': len(all_lines),
            'avg_font_size': avg_font_size
        }
        
        return {
            'raw_text': '\n'.join(l['text'] for l in all_lines),
            'clean_text': clean_text,
            'lines': all_lines,
            'sections': sections,
            'metadata': metadata,
            'status': 'ok'
        }
    
    def _process_docx(self, file_path: str) -> Dict:
        """Process DOCX"""
        try:
            from docx import Document
            doc = Document(file_path)
            
            lines = []
            for para in doc.paragraphs:
                if para.text.strip():
                    lines.append({
                        'text': para.text.strip(),
                        'font_size': 11,
                        'is_bold': para.runs[0].bold if para.runs else False
                    })
            
            clean_text = '\n'.join(l['text'] for l in lines)
            sections = self._extract_sections_simple(clean_text)
            
            return {
                'raw_text': clean_text,
                'clean_text': clean_text,
                'lines': lines,
                'sections': sections,
                'metadata': {'format': 'docx'},
                'status': 'ok'
            }
        except Exception as e:
            return {'error': str(e), 'status': 'error'}
    
    def _process_txt(self, file_path: str) -> Dict:
        """Process TXT"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            
            lines = [{'text': l.strip(), 'font_size': 11, 'is_bold': False} 
                     for l in text.split('\n') if l.strip()]
            
            sections = self._extract_sections_simple(text)
            
            return {
                'raw_text': text,
                'clean_text': text,
                'lines': lines,
                'sections': sections,
                'metadata': {'format': 'txt'},
                'status': 'ok'
            }
        except Exception as e:
            return {'error': str(e), 'status': 'error'}
    
    def _is_section_header(self, line: Dict, avg_font_size: float, 
                          prev_line: Dict, next_line: Dict) -> Tuple[bool, float]:
        """
        Multi-signal section header detection
        Returns: (is_header, confidence_score)
        """
        score = 0.0
        text = line['text'].strip()
        
        # Skip if too long
        if len(text) > 80:
            return False, 0.0
        
        # Negative signals (disqualifiers)
        # Skip if starts with bullet
        if text.startswith('•') or text.startswith('-'):
            return False, 0.0
        
        # Skip if contains dates (likely not a section header)
        if re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|20\d{2})\b', text):
            return False, 0.0
        
        # Skip if ends with punctuation (likely sentence, not header)
        if text.endswith('.') or text.endswith(','):
            return False, 0.0
        
        # Positive signals
        # Signal 1: Font size larger than average (weight: 0.3)
        if line['font_size'] > avg_font_size * 1.08:
            score += 0.3
        
        # Signal 2: Bold (weight: 0.25)
        if line['is_bold']:
            score += 0.25
        
        # Signal 3: Short line (weight: 0.15)
        if len(text) < 50:
            score += 0.15
        
        # Signal 4: Isolated (blank before/after) (weight: 0.1)
        if prev_line and not prev_line['text'].strip():
            score += 0.05
        if next_line and not next_line['text'].strip():
            score += 0.05
        
        # Signal 5: All caps or title case (weight: 0.1)
        if text.isupper() or (text.istitle() and len(text.split()) <= 4):
            score += 0.1
        
        # Signal 6: Keyword match (weight: 0.15 - increased)
        text_lower = text.lower()
        if any(kw in text_lower for kw in self.section_keywords):
            score += 0.15
        
        # Threshold: 0.5 for likely section header (increased from 0.4)
        is_header = score >= 0.5
        
        return is_header, score
    
    def _build_clean_text(self, lines: List[Dict]) -> str:
        """Build clean text with proper line breaks"""
        if not lines:
            return ""
        
        result = []
        
        for i, line in enumerate(lines):
            text = line['text']
            
            # Add paragraph break if Y-gap is large
            if i > 0:
                prev = lines[i-1]
                y_gap = line['y0'] - prev['y1']
                
                # New paragraph if gap > 10 points
                if y_gap > 10:
                    result.append('\n')
            
            result.append(text)
        
        return '\n'.join(result)
    
    def _extract_sections(self, lines: List[Dict]) -> Dict:
        """Extract sections from lines with headers"""
        sections = {}
        major_sections = {'SKILLS', 'EXPERIENCE', 'EDUCATION', 'SUMMARY', 'PROJECTS', 'CERTIFICATIONS'}
        
        # Find all section headers
        headers = []
        for i, line in enumerate(lines):
            if line.get('is_section_header', False):
                headers.append((i, line['text'], line['section_confidence']))
        
        # Extract content between headers
        for idx, (line_idx, header_text, confidence) in enumerate(headers):
            # Normalize section name
            section_name = self._normalize_section_name(header_text)
            
            # Only keep major sections, skip duplicates
            if section_name not in major_sections:
                continue
            
            if section_name in sections:
                # Already have this section, skip
                continue
            
            # Find next major section header
            next_idx = len(lines)
            for j in range(idx + 1, len(headers)):
                next_header_text = headers[j][1]
                next_section_name = self._normalize_section_name(next_header_text)
                if next_section_name in major_sections:
                    next_idx = headers[j][0]
                    break
            
            # Extract lines between this header and next
            section_lines = lines[line_idx + 1:next_idx]
            section_text = '\n'.join(l['text'] for l in section_lines)
            
            sections[section_name] = {
                'text': section_text.strip(),
                'start_line': line_idx,
                'end_line': next_idx,
                'confidence': confidence
            }
        
        return sections
    
    def _normalize_section_name(self, text: str) -> str:
        """Normalize section header to standard name"""
        text_lower = text.lower()
        
        if any(kw in text_lower for kw in ['experience', 'work', 'employment']):
            return 'EXPERIENCE'
        elif any(kw in text_lower for kw in ['education', 'academic']):
            return 'EDUCATION'
        elif any(kw in text_lower for kw in ['skill', 'technical', 'competenc']):
            return 'SKILLS'
        elif any(kw in text_lower for kw in ['summary', 'objective', 'profile']):
            return 'SUMMARY'
        elif any(kw in text_lower for kw in ['project']):
            return 'PROJECTS'
        elif any(kw in text_lower for kw in ['certif', 'award']):
            return 'CERTIFICATIONS'
        else:
            return text.upper()
    
    def _extract_sections_simple(self, text: str) -> Dict:
        """Simple text-based section extraction (fallback)"""
        sections = {}
        lines = text.split('\n')
        
        patterns = {
            'SKILLS': r'(?i)(?:technical\s*)?skills?',
            'EXPERIENCE': r'(?i)(?:work\s*)?experience|employment',
            'EDUCATION': r'(?i)education|academic'
        }
        
        for section_name, pattern in patterns.items():
            for i, line in enumerate(lines):
                if re.search(pattern, line) and len(line.strip()) < 50:
                    # Found header, extract until next section
                    section_lines = []
                    for j in range(i + 1, len(lines)):
                        # Check if next section
                        is_next = any(re.search(p, lines[j]) and len(lines[j].strip()) < 50 
                                     for p in patterns.values())
                        if is_next:
                            break
                        section_lines.append(lines[j])
                    
                    sections[section_name] = {
                        'text': '\n'.join(section_lines).strip(),
                        'confidence': 0.7
                    }
                    break
        
        return sections
