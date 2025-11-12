"""
Production-Grade Entity Extractor using spaCy
Architecture: RegEx for PII + spaCy for NER
"""
import re
import spacy
from typing import Dict, List

class SpacyExtractor:
    """
    Hybrid extractor using:
    - RegEx for reliable PII (email, phone)
    - spaCy for NER (names, organizations, skills)
    """
    
    def __init__(self):
        print("🔧 Loading spaCy NER model...")
        try:
            self.nlp = spacy.load("en_core_web_sm")
            print("✅ spaCy model loaded")
        except OSError:
            print("⚠️  spaCy model not found. Run: python -m spacy download en_core_web_sm")
            self.nlp = None

        # Compiled RegEx patterns
        self.regex_patterns = {
            'EMAIL': re.compile(r'\b[A-Za-z][A-Za-z0-9._%+-]*@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'PHONE': re.compile(r'\+\d{10,15}|\d{10}'),
            'LINKEDIN_URL': re.compile(r'linkedin\.com/in/[\w-]+')
        }

    def _extract_with_regex(self, text: str) -> List[Dict]:
        """Extract PII with RegEx"""
        entities = []
        
        for label, pattern in self.regex_patterns.items():
            for match in pattern.finditer(text):
                entities.append({
                    "label": label,
                    "text": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "source": "regex"
                })
        
        # Extract Skills section
        skills_match = re.search(r'(?:SKILLS?|TECHNICAL SKILLS?)[:\s]*\n(.*?)(?:\n\n|\n[A-Z]{3,})', 
                                text, re.IGNORECASE | re.DOTALL)
        if skills_match:
            skills_text = skills_match.group(1)
            skills = re.split(r'[,;•\n|]', skills_text)
            for skill in skills:
                skill = skill.strip()
                if skill and len(skill) > 2:
                    entities.append({
                        "label": "SKILL",
                        "text": skill,
                        "start": text.find(skill),
                        "end": text.find(skill) + len(skill),
                        "source": "regex"
                    })
        
        # Extract Education
        edu_match = re.search(r'(?:EDUCATION|ACADEMIC)[:\s]*\n(.*?)(?:\n\n|\n[A-Z]{3,}|$)', 
                             text, re.IGNORECASE | re.DOTALL)
        if edu_match:
            edu_text = edu_match.group(1)
            degrees = re.findall(r'(?:Bachelor|Master|PhD|B\.?S\.?|M\.?S\.?|MBA|B\.?Tech|M\.?Tech|PGDM)[^\n]*', 
                               edu_text, re.IGNORECASE)
            for degree in degrees:
                degree = degree.strip()
                entities.append({
                    "label": "DEGREE",
                    "text": degree,
                    "start": text.find(degree),
                    "end": text.find(degree) + len(degree),
                    "source": "regex"
                })
        
        # Extract companies from EXPERIENCE section only
        exp_match = re.search(r'(?:EXPERIENCE|WORK HISTORY)[:\s]*\n(.*?)(?:\n\n[A-Z]{3,}|$)', 
                             text, re.IGNORECASE | re.DOTALL)
        if exp_match:
            exp_text = exp_match.group(1)[:1000]
            companies = re.findall(r'\b([A-Z][A-Za-z\s&]+?(?:Pvt|Ltd|Inc|Corp|LLC|Limited)\.?)\b', exp_text)
            for company in companies:
                company = company.strip()
                if 3 < len(company) < 50:
                    entities.append({
                        "label": "COMPANY",
                        "text": company,
                        "start": text.find(company),
                        "end": text.find(company) + len(company),
                        "source": "regex"
                    })
                
        return entities

    def _extract_with_spacy(self, text: str) -> List[Dict]:
        """Extract entities with spaCy NER (PERSON and GPE only)"""
        if not self.nlp:
            return []
            
        try:
            doc = self.nlp(text[:500])
            entities = []
            
            for ent in doc.ents:
                if ent.label_ in ['PERSON', 'GPE']:
                    entities.append({
                        "label": ent.label_,
                        "text": ent.text,
                        "start": ent.start_char,
                        "end": ent.end_char,
                        "source": "spacy"
                    })
            
            return entities
        except Exception as e:
            print(f"⚠️  spaCy extraction failed: {e}")
            return []

    def extract(self, text: str) -> Dict:
        """Main extraction method"""
        # 1. RegEx extraction (primary for PII)
        regex_entities = self._extract_with_regex(text)
        
        # 2. spaCy extraction (supplement for NER)
        spacy_entities = self._extract_with_spacy(text)
        
        # 3. Structure output
        result = {
            "name": "",
            "email": "",
            "phone": "",
            "skills": [],
            "degrees": [],
            "job_titles": [],
            "companies": [],
            "universities": [],
            "locations": []
        }
        
        # Extract from RegEx
        for entity in regex_entities:
            label = entity['label']
            ent_text = entity['text']
            
            if label == 'EMAIL' and not result['email']:
                result['email'] = ent_text
            elif label == 'PHONE' and not result['phone']:
                result['phone'] = ent_text
            elif label == 'SKILL' and ent_text not in result['skills']:
                result['skills'].append(ent_text)
            elif label == 'DEGREE' and ent_text not in result['degrees']:
                result['degrees'].append(ent_text)
            elif label == 'COMPANY' and ent_text not in result['companies']:
                result['companies'].append(ent_text)
        
        # Extract name from spaCy (PERSON in first 300 chars near contact)
        email_pos = text.find(result['email']) if result['email'] else -1
        phone_pos = text.find(result['phone']) if result['phone'] else -1
        contact_pos = min(p for p in [email_pos, phone_pos] if p >= 0) if (email_pos >= 0 or phone_pos >= 0) else 0
        
        for entity in spacy_entities:
            if entity['label'] == 'PERSON' and not result['name']:
                if entity['start'] < 300 and abs(entity['start'] - contact_pos) < 200:
                    result['name'] = entity['text']
                    break
        
        # Fallback: If spaCy didn't find name, use RegEx near contact info
        if not result['name'] and contact_pos > 0:
            search_start = max(0, contact_pos - 150)
            search_end = contact_pos + 50
            search_text = text[search_start:search_end]
            
            name_pattern = re.compile(r'\b([A-Z][a-z]+\s[A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\b')
            for match in name_pattern.finditer(search_text):
                candidate = match.group(1)
                result['name'] = candidate
                break
        
        # Extract locations from spaCy
        for entity in spacy_entities:
            if entity['label'] == 'GPE' and entity['text'] not in result['locations']:
                result['locations'].append(entity['text'])
        
        return result
