"""
Final Resume Parser
Complete pipeline: Preprocessing V2 + NER + Rules
"""
import re
import spacy
from typing import Dict, List, Tuple
from .preprocessing_engine_v2 import PreprocessingEngineV2

class FinalResumeParser:
    """
    Production resume parser combining:
    1. Preprocessing V2 (line-level extraction)
    2. spaCy NER for entities
    3. Rule-based extraction
    4. Validation
    """
    
    def __init__(self):
        self.preprocessor = PreprocessingEngineV2()
        
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            self.nlp = None
        
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
        self.linkedin_pattern = re.compile(r'linkedin\.com/in/[\w-]+')
        self.github_pattern = re.compile(r'github\.com/[\w-]+')
        
        self.tech_terms = {
            'power bi', 'sql', 'excel', 'python', 'java', 'javascript',
            'dax', 'etl', 'kpi', 'yoy', 'mtd', 'ytd', 'rls'
        }
    
    def parse(self, file_path: str) -> Dict:
        """Parse resume and extract all entities"""
        
        # Step 1: Preprocess
        preprocessed = self.preprocessor.process(file_path)
        
        if preprocessed['status'] != 'ok':
            return {'error': preprocessed.get('error'), 'status': 'error'}
        
        # Step 2: Extract entities
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
        
        text = preprocessed['clean_text']
        sections = preprocessed['sections']
        lines = preprocessed['lines']
        
        # Extract PII from header
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
        
        # Extract name from first few lines
        result['name'] = self._extract_name(lines[:10])
        
        # Extract skills from full text (not just skills section)
        result['skills'] = self._extract_skills(text)
        
        # Extract from sections
        for section_name, section_data in sections.items():
            section_text = section_data['text']
            
            if section_name == 'EDUCATION':
                result['degrees'] = self._extract_degrees(section_text, text)
                if self.nlp and section_text:
                    doc = self.nlp(section_text[:2000])
                    result['universities'] = [ent.text for ent in doc.ents if ent.label_ == 'ORG'][:3]
            
            elif section_name == 'EXPERIENCE':
                companies, titles = self._extract_experience(section_text)
                result['companies'] = companies
                result['job_titles'] = titles
        
        # Extract locations using NER
        if self.nlp:
            doc = self.nlp(text[:5000])
            result['locations'] = list(set([ent.text for ent in doc.ents if ent.label_ == 'GPE']))[:5]
        
        # Validation
        result = self._validate(result)
        
        return {
            **result,
            'status': 'ok',
            'metadata': preprocessed['metadata']
        }
    
    def _validate(self, result: Dict) -> Dict:
        """Validate and add confidence scores"""
        result['confidence'] = {}
        
        # Email validation
        if result['email']:
            result['confidence']['email'] = 1.0 if '@' in result['email'] and '.' in result['email'] else 0.5
        
        # Phone validation
        if result['phone']:
            digits = ''.join(c for c in result['phone'] if c.isdigit())
            result['confidence']['phone'] = 1.0 if len(digits) >= 10 else 0.7
        
        # Name validation
        if result['name']:
            words = result['name'].split()
            result['confidence']['name'] = 1.0 if 2 <= len(words) <= 3 else 0.7
        
        return result
    
    def _extract_name(self, header_lines: List[Dict]) -> str:
        """Extract name from header lines"""
        for line in header_lines:
            text = line['text'].strip()
            words = text.split()
            
            # Name: 2-3 words, all alpha, capitalized, no special chars
            if 2 <= len(words) <= 3:
                if all(w.isalpha() and w[0].isupper() for w in words):
                    if '@' not in text and '|' not in text and 'http' not in text.lower():
                        return text
        
        return ""
    
    def _extract_skills(self, full_text: str) -> List[str]:
        """Extract skills using KB with smart filtering"""
        from .kb_singleton import get_kb_instance
        
        kb = get_kb_instance()
        if not kb:
            return []
        
        text_lower = full_text.lower()
        
        # Lower threshold to get more candidates
        extracted = kb.extract_skills(full_text, top_k=100, threshold=0.3)
        
        skills = []
        seen = set()
        
        for item in extracted:
            label = item['label']
            score = item['score']
            
            # Extract skill name from "Name (description)" format
            if '(' in label:
                skill_name = label.split('(')[0].strip()
            else:
                skill_name = label
            
            skill_lower = skill_name.lower()
            
            # Skip if already seen
            if skill_lower in seen:
                continue
            
            # Filter out generic verb phrases
            if skill_lower.startswith(('use ', 'apply ', 'implement ', 'design ', 'develop ', 'create ', 'manage ', 'perform ')):
                continue
            
            # Keep if: high score OR short name (likely actual tech)
            if score > 0.5 or (len(skill_name.split()) <= 2 and len(skill_name) < 25):
                # Final check: skill name should appear in text (fuzzy match)
                # This prevents KB from hallucinating skills
                text_lower = full_text.lower()
                skill_words = skill_lower.split()
                
                # Check if any word from skill appears in text
                if any(word in text_lower for word in skill_words if len(word) > 3):
                    skills.append(skill_name)
                    seen.add(skill_lower)
        
        return skills[:30]
    
    def _extract_degrees(self, edu_text: str, full_text: str = '') -> List[str]:
        """Extract degrees with fallback to full text"""
        pattern = r'(?:Bachelor|Master|PhD|B\.?S\.?|M\.?S\.?|MBA|B\.?Tech|M\.?Tech|PGDM)[^\n]{0,100}'
        
        # Try section first
        degrees = re.findall(pattern, edu_text, re.IGNORECASE) if edu_text else []
        
        # Fallback to full text if section empty
        if not degrees and full_text:
            degrees = re.findall(pattern, full_text, re.IGNORECASE)
        
        return list(set([d.strip() for d in degrees if len(d.strip()) > 5]))[:5]
    
    def _extract_experience(self, exp_text: str) -> Tuple[List[str], List[str]]:
        """Extract companies and titles"""
        companies = []
        titles = []
        
        # Use NER for companies
        if self.nlp:
            doc = self.nlp(exp_text[:5000])
            org_entities = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
            
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
                title = re.sub(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|20\d{2})\b.*', '', line, flags=re.IGNORECASE)
                title = re.sub(r'\b(Delhi|Mumbai|Bangalore|Jaipur|India)\b.*', '', title, flags=re.IGNORECASE)
                title = re.sub(r'\s+', ' ', title).strip()
                
                if title and 5 < len(title) < 80 and title not in titles:
                    titles.append(title)
        
        return companies[:5], titles[:5]
