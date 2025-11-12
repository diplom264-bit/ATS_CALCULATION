"""
Production-Ready Entity Extractor
Architecture: BERT NER + spaCy + Layout Awareness
"""
import re
import spacy
from transformers import pipeline
import torch
from typing import Dict, List, Tuple

class ProductionNERExtractor:
    """
    Production-grade extractor using:
    1. dslim/bert-base-NER - reliable PERSON, ORG, LOC detection
    2. spaCy - validation and supplementary extraction
    3. Layout awareness - section-based extraction
    4. RegEx - PII and patterns
    """
    
    def __init__(self):
        print("🔧 Loading Production NER Extractor...")
        
        # Load BERT NER (primary)
        try:
            device = 0 if torch.cuda.is_available() else -1
            self.bert_ner = pipeline(
                "ner",
                model="dslim/bert-base-NER",
                device=device,
                aggregation_strategy="simple"
            )
            print(f"✅ BERT NER loaded (GPU: {torch.cuda.is_available()})")
        except Exception as e:
            print(f"⚠️  BERT NER failed: {e}")
            self.bert_ner = None
        
        # Load spaCy (validation)
        try:
            self.nlp = spacy.load("en_core_web_sm")
            print("✅ spaCy loaded")
        except OSError:
            print("⚠️  spaCy not found. Run: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # RegEx patterns
        self.regex_patterns = {
            'EMAIL': re.compile(r'\b[A-Za-z][A-Za-z0-9._%+-]*@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'PHONE': re.compile(r'\+\d{10,15}|\d{10}'),
            'LINKEDIN': re.compile(r'linkedin\.com/in/[\w-]+')
        }
    
    def _parse_sections(self, text: str) -> Dict[str, Tuple[int, int]]:
        """Parse resume into sections"""
        sections = {'HEADER': (0, 300)}
        
        patterns = {
            'SKILLS': r'^\s*(?:SKILLS?|TECHNICAL SKILLS?)\s*$',
            'EXPERIENCE': r'^\s*(?:EXPERIENCE|WORK HISTORY)\s*$',
            'EDUCATION': r'^\s*(?:EDUCATION|ACADEMIC)\s*$'
        }
        
        for name, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                start = match.start()
                next_match = re.search(r'^\s*[A-Z]{3,}\s*$', text[start+20:], re.IGNORECASE | re.MULTILINE)
                end = start + 20 + next_match.start() if next_match else len(text)
                sections[name] = (start, min(end, start + 2000))
        
        return sections
    
    def _extract_with_bert(self, text: str) -> List[Dict]:
        """Extract entities using BERT NER"""
        if not self.bert_ner:
            return []
        
        try:
            entities = self.bert_ner(text[:512])  # BERT limit
            return [
                {
                    'label': e['entity_group'],
                    'text': e['word'],
                    'start': e['start'],
                    'end': e['end'],
                    'score': e['score'],
                    'source': 'bert'
                }
                for e in entities
            ]
        except Exception as e:
            print(f"⚠️  BERT extraction failed: {e}")
            return []
    
    def _extract_with_spacy(self, text: str) -> List[Dict]:
        """Extract entities using spaCy"""
        if not self.nlp:
            return []
        
        try:
            doc = self.nlp(text[:500])
            return [
                {
                    'label': ent.label_,
                    'text': ent.text,
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'source': 'spacy'
                }
                for ent in doc.ents
                if ent.label_ in ['PERSON', 'ORG', 'GPE']
            ]
        except Exception as e:
            print(f"⚠️  spaCy extraction failed: {e}")
            return []
    
    def extract(self, text: str) -> Dict:
        """Main extraction method"""
        sections = self._parse_sections(text)
        
        result = {
            "name": "",
            "email": "",
            "phone": "",
            "linkedin": "",
            "skills": [],
            "degrees": [],
            "job_titles": [],
            "companies": [],
            "universities": [],
            "locations": []
        }
        
        # Extract from header
        if 'HEADER' in sections:
            start, end = sections['HEADER']
            header_text = text[start:end]
            
            # PII with RegEx
            email_match = self.regex_patterns['EMAIL'].search(header_text)
            if email_match:
                result['email'] = email_match.group(0)
            
            phone_match = self.regex_patterns['PHONE'].search(header_text)
            if phone_match:
                result['phone'] = phone_match.group(0)
            
            linkedin_match = self.regex_patterns['LINKEDIN'].search(header_text)
            if linkedin_match:
                result['linkedin'] = linkedin_match.group(0)
            
            # Name with BERT - merge consecutive PER entities
            bert_entities = self._extract_with_bert(header_text)
            per_entities = [e for e in bert_entities if e['label'] == 'PER']
            
            if per_entities:
                # Check if consecutive PER entities (subword tokens)
                if len(per_entities) > 1:
                    # Check if they're close together (within 5 chars)
                    first = per_entities[0]
                    last = per_entities[-1]
                    if last['end'] - first['start'] < 20:  # Likely same name
                        # Extract full text from original
                        full_name = header_text[first['start']:last['end']]
                        # Clean subword markers
                        full_name = full_name.replace('##', '').strip()
                        if len(full_name) > 2:
                            result['name'] = full_name
                else:
                    # Single entity
                    name = per_entities[0]['text'].strip()
                    if len(name) > 2:
                        result['name'] = name
            
            # Fallback: RegEx for name (more reliable than spaCy for resumes)
            if not result['name'] and result['email']:
                contact_pos = header_text.find(result['email'])
                search_text = header_text[max(0, contact_pos - 150):contact_pos + 50]
                name_pattern = re.compile(r'\b([A-Z][a-z]+\s[A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\b')
                match = name_pattern.search(search_text)
                if match:
                    result['name'] = match.group(1)
            
            # Last resort: spaCy for name
            if not result['name']:
                spacy_entities = self._extract_with_spacy(header_text)
                for entity in spacy_entities:
                    if entity['label'] == 'PERSON':
                        result['name'] = entity['text']
                        break
            
            # Locations with spaCy
            spacy_entities = self._extract_with_spacy(header_text)
            for entity in spacy_entities:
                if entity['label'] == 'GPE' and entity['text'] not in result['locations']:
                    result['locations'].append(entity['text'])
        
        # Extract skills
        if 'SKILLS' in sections:
            start, end = sections['SKILLS']
            skills_text = text[start:end]
            skills_text = re.sub(r'^.*?(?:SKILLS?)[:\s]*\n', '', skills_text, flags=re.IGNORECASE)
            skills = re.split(r'[,;•\n|]', skills_text)
            for skill in skills:
                skill = re.sub(r'^[:\-•\s]+', '', skill.strip())
                skill = re.sub(r'\s+', ' ', skill)
                if skill and 2 < len(skill) < 50:
                    result['skills'].append(skill)
            result['skills'] = result['skills'][:20]
        
        # Extract education
        if 'EDUCATION' in sections:
            start, end = sections['EDUCATION']
            edu_text = text[start:end]
            degrees = re.findall(
                r'(?:Bachelor|Master|PhD|B\.?S\.?|M\.?S\.?|MBA|B\.?Tech|M\.?Tech|PGDM)[^\n]*',
                edu_text, re.IGNORECASE
            )
            result['degrees'] = [d.strip() for d in degrees][:5]
        
        # Extract experience
        if 'EXPERIENCE' in sections:
            start, end = sections['EXPERIENCE']
            exp_text = text[start:end]
            
            # Use BERT to detect ORG entities
            bert_entities = self._extract_with_bert(exp_text)
            org_entities = [e for e in bert_entities if e['label'] == 'ORG']
            
            # Layout-based: detect company/title pairs
            lines = [l.strip() for l in exp_text.split('\n')]
            seen_companies = set()
            
            for i, line in enumerate(lines):
                if not line or line.startswith('•') or line.startswith('-') or len(line) < 5:
                    continue
                
                # Check if line contains BERT-detected ORG
                is_company = any(org['text'].lower() in line.lower() for org in org_entities)
                
                # Layout heuristic: short line (< 60 chars) with capital words, before bullets
                if not is_company:
                    cap_words = len(re.findall(r'\b[A-Z][a-z]+', line))
                    next_is_bullet = i + 1 < len(lines) and lines[i+1].startswith('•')
                    is_company = cap_words >= 2 and len(line) < 60 and next_is_bullet
                
                if is_company and line not in seen_companies:
                    result['companies'].append(line)
                    seen_companies.add(line)
                    
                    # Next non-bullet line is likely job title
                    for j in range(i+1, min(i+3, len(lines))):
                        next_line = lines[j]
                        if next_line and not next_line.startswith('•') and not next_line.startswith('-'):
                            if len(next_line) < 60 and next_line not in result['job_titles']:
                                result['job_titles'].append(next_line)
                            break
            
            result['companies'] = result['companies'][:5]
            result['job_titles'] = result['job_titles'][:5]
        
        return result
