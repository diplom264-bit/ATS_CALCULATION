"""
Production Resume Extractor
Final implementation combining preprocessing + NER + rules
"""
import re
import spacy
from typing import Dict, List, Tuple
from collections import Counter

class ProductionExtractor:
    """
    Production-grade extractor:
    1. PyMuPDF preprocessing for clean text + layout
    2. spaCy NER for entities
    3. Layout-aware section detection
    4. Rule-based aggregation
    5. Validation and confidence scoring
    """
    
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            self.nlp = None
        
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
        self.linkedin_pattern = re.compile(r'linkedin\.com/in/[\w-]+')
        self.github_pattern = re.compile(r'github\.com/[\w-]+')
        
        # Tools/technologies to exclude from companies
        self.tech_terms = {
            'power bi', 'sql', 'excel', 'python', 'java', 'javascript',
            'react', 'angular', 'node', 'aws', 'azure', 'docker',
            'kubernetes', 'mysql', 'postgresql', 'mongodb', 'redis',
            'dax', 'etl', 'rls', 'kpi', 'yoy', 'mtd', 'ytd'
        }
    
    def extract(self, preprocessed_data: Dict) -> Dict:
        """Extract all entities from preprocessed document"""
        
        result = {
            "name": "",
            "email": "",
            "phone": "",
            "linkedin": "",
            "github": "",
            "skills": [],
            "degrees": [],
            "job_titles": [],
            "companies": [],
            "universities": [],
            "locations": []
        }
        
        if preprocessed_data.get('status') != 'ok':
            return result
        
        text = preprocessed_data['clean_text']
        blocks = preprocessed_data.get('blocks', [])
        
        # 1. Extract PII (highest confidence)
        header = text[:500]
        
        email_match = self.email_pattern.search(header)
        if email_match:
            result['email'] = email_match.group(0)
        
        phone_match = self.phone_pattern.search(header)
        if phone_match:
            result['phone'] = phone_match.group(0)
        
        linkedin_match = self.linkedin_pattern.search(header)
        if linkedin_match:
            result['linkedin'] = linkedin_match.group(0)
        
        github_match = self.github_pattern.search(header)
        if github_match:
            result['github'] = github_match.group(0)
        
        # 2. Extract name (layout + NER)
        result['name'] = self._extract_name(header, blocks)
        
        # 3. Detect sections (text-based is more reliable)
        sections = self._detect_sections_text(text)
        
        # Enhance with layout if available
        if not sections and blocks:
            sections = self._detect_sections_layout(text, blocks)
        
        # 4. Extract from each section
        for section_type, section_text in sections.items():
            if section_type == 'SKILLS':
                result['skills'] = self._extract_skills(section_text)
            
            elif section_type == 'EDUCATION':
                result['degrees'] = self._extract_degrees(section_text)
                if self.nlp:
                    doc = self.nlp(section_text[:2000])
                    result['universities'] = [ent.text for ent in doc.ents if ent.label_ == 'ORG'][:3]
            
            elif section_type == 'EXPERIENCE':
                companies, titles = self._extract_experience(section_text)
                result['companies'] = companies
                result['job_titles'] = titles
        
        # 5. Extract locations using NER
        if self.nlp:
            doc = self.nlp(text[:5000])
            result['locations'] = list(set([ent.text for ent in doc.ents if ent.label_ == 'GPE']))[:5]
        
        return result
    
    def _extract_name(self, header: str, blocks: List[Dict]) -> str:
        """Extract name using layout (largest font) + validation"""
        
        # Strategy 1: Largest font in header blocks
        if blocks:
            header_blocks = [b for b in blocks[:5] if b['y0'] < 150]
            if header_blocks:
                # Sort by font size
                sorted_blocks = sorted(header_blocks, key=lambda b: b['font_size'], reverse=True)
                
                for block in sorted_blocks:
                    text = block['text'].strip()
                    
                    # Validate: 2-3 words, all alpha, capitalized
                    words = text.split()
                    if 2 <= len(words) <= 3:
                        if all(w.isalpha() and w[0].isupper() for w in words):
                            return text
        
        # Strategy 2: First line with 2-3 capitalized words
        lines = header.split('\n')
        for line in lines[:5]:
            line = line.strip()
            words = line.split()
            if 2 <= len(words) <= 3:
                if all(w.isalpha() and w[0].isupper() for w in words):
                    if '@' not in line and '|' not in line:
                        return line
        
        # Strategy 3: Use NER
        if self.nlp:
            doc = self.nlp(header)
            persons = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']
            if persons:
                # Return first person that looks like a name
                for person in persons:
                    words = person.split()
                    if 2 <= len(words) <= 3 and all(w.isalpha() for w in words):
                        return person
        
        return ""
    
    def _detect_sections_layout(self, text: str, blocks: List[Dict]) -> Dict[str, str]:
        """Detect sections using layout information"""
        
        sections = {}
        
        if not blocks:
            # Fallback to text-based detection
            return self._detect_sections_text(text)
        
        # Find section headers (bold + larger font)
        avg_font_size = sum(b['font_size'] for b in blocks) / len(blocks)
        
        section_keywords = {
            'SKILLS': ['skill', 'technical', 'competenc'],
            'EXPERIENCE': ['experience', 'employment', 'work'],
            'EDUCATION': ['education', 'academic', 'qualification']
        }
        
        section_blocks = []
        
        for i, block in enumerate(blocks):
            text_lower = block['text'].lower().strip()
            
            # Check if this is a section header
            is_header = False
            matched_section = None
            
            # Check 1: Bold + larger font
            if block['is_bold'] and block['font_size'] > avg_font_size * 1.05:
                # Check if matches section keywords
                for section_type, keywords in section_keywords.items():
                    if any(kw in text_lower for kw in keywords):
                        is_header = True
                        matched_section = section_type
                        break
            
            if is_header:
                section_blocks.append((i, matched_section))
        
        # Extract text between section headers
        for idx, (block_idx, section_type) in enumerate(section_blocks):
            # Find next section
            next_idx = section_blocks[idx + 1][0] if idx + 1 < len(section_blocks) else len(blocks)
            
            # Get all text between this section and next
            section_text_parts = []
            for i in range(block_idx + 1, next_idx):
                section_text_parts.append(blocks[i]['text'])
            
            sections[section_type] = '\n'.join(section_text_parts).strip()
        
        return sections
    
    def _detect_sections_text(self, text: str) -> Dict[str, str]:
        """Fallback: text-based section detection"""
        sections = {}
        lines = text.split('\n')
        
        section_patterns = {
            'SKILLS': r'(?i)(?:technical\s*)?skills?',
            'EXPERIENCE': r'(?i)(?:work\s*)?experience|employment',
            'EDUCATION': r'(?i)education|academic'
        }
        
        for section_type, pattern in section_patterns.items():
            for i, line in enumerate(lines):
                if re.search(pattern, line) and len(line.strip()) < 50:
                    # Found section header
                    # Extract until next section
                    section_lines = []
                    for j in range(i + 1, len(lines)):
                        # Check if next section
                        is_next_section = any(
                            re.search(p, lines[j]) and len(lines[j].strip()) < 50
                            for p in section_patterns.values()
                        )
                        if is_next_section:
                            break
                        section_lines.append(lines[j])
                    
                    sections[section_type] = '\n'.join(section_lines).strip()
                    break
        
        return sections
    
    def _extract_skills(self, skills_text: str) -> List[str]:
        """Extract skills"""
        skills = []
        items = re.split(r'[,;•\n|]', skills_text)
        
        for item in items:
            item = item.strip()
            item = re.sub(r'^[A-Za-z\s]+:\s*', '', item)
            item = re.sub(r'^[:\-•\s]+', '', item)
            item = re.sub(r'\s+', ' ', item)
            
            if item and 2 < len(item) < 50:
                if not item.endswith(':'):
                    skills.append(item)
        
        return list(dict.fromkeys(skills))[:20]  # Deduplicate preserving order
    
    def _extract_degrees(self, edu_text: str) -> List[str]:
        """Extract degrees"""
        pattern = r'(?:Bachelor|Master|PhD|B\.?S\.?|M\.?S\.?|MBA|B\.?Tech|M\.?Tech|PGDM)[^\n]{0,100}'
        degrees = re.findall(pattern, edu_text, re.IGNORECASE)
        return list(set([d.strip() for d in degrees if len(d.strip()) > 5]))[:5]
    
    def _extract_experience(self, exp_text: str) -> Tuple[List[str], List[str]]:
        """Extract companies and titles using NER + rules"""
        companies = []
        titles = []
        
        # Use NER to find ORG entities
        if self.nlp:
            doc = self.nlp(exp_text[:5000])
            org_entities = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
            
            # Filter out tech terms
            for org in org_entities:
                if org.lower() not in self.tech_terms and len(org) > 3:
                    if org not in companies:
                        companies.append(org)
        
        # Extract titles using keywords
        lines = [l.strip() for l in exp_text.split('\n') if l.strip()]
        
        job_keywords = ['developer', 'engineer', 'analyst', 'manager', 'consultant', 'specialist', 'architect']
        
        for line in lines:
            if line.startswith('•') or line.startswith('-') or len(line) > 100:
                continue
            
            if any(kw in line.lower() for kw in job_keywords):
                # Clean title
                title = re.sub(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|20\d{2})\b.*', '', line, flags=re.IGNORECASE)
                title = re.sub(r'\b(Delhi|Mumbai|Bangalore|Jaipur|India)\b.*', '', title, flags=re.IGNORECASE)
                title = re.sub(r'\s+', ' ', title).strip()
                
                if title and 5 < len(title) < 80 and title not in titles:
                    titles.append(title)
        
        return companies[:5], titles[:5]
