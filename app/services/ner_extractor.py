"""
Specialist NER Model for Resume Parsing
Model: yashpwr/resume-ner-bert-v2 (91% accuracy, 25 entity types)
"""
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
import torch
from pathlib import Path
from typing import Dict, List

class NERExtractor:
    """Specialist NER for resume entity extraction"""
    
    def __init__(self, model_cache_dir="models/ner_model"):
        self.device = 0 if torch.cuda.is_available() else -1
        self.model_cache_dir = Path(model_cache_dir)
        self.model_cache_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🔧 Loading NER model (device: {'cuda' if self.device == 0 else 'cpu'})...")
        
        model_name = "yashpwr/resume-ner-bert-v2"
        if (self.model_cache_dir / "config.json").exists():
            print("✅ Using cached NER model")
            self.tokenizer = AutoTokenizer.from_pretrained(str(self.model_cache_dir))
            self.model = AutoModelForTokenClassification.from_pretrained(str(self.model_cache_dir))
            self.ner = pipeline("ner", model=self.model, tokenizer=self.tokenizer, device=self.device, aggregation_strategy="average")
        else:
            print("📥 Downloading NER model (~400MB)...")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForTokenClassification.from_pretrained(model_name)
            
            self.tokenizer.save_pretrained(str(self.model_cache_dir))
            self.model.save_pretrained(str(self.model_cache_dir))
            print(f"💾 NER model cached to {self.model_cache_dir}")
            
            self.ner = pipeline("ner", model=self.model, tokenizer=self.tokenizer, device=self.device, aggregation_strategy="average")
        
        print(f"✅ NER model ready (GPU: {torch.cuda.is_available()})")
    
    def extract(self, text: str) -> Dict:
        """Extract entities - regex primary, NER supplement"""
        if not text or not text.strip():
            return self._empty_result()
        
        # Use regex as primary (more reliable for real resumes)
        result = self._regex_fallback(text)
        
        # Try NER to supplement missing fields
        try:
            entities = self.ner(text[:2000])
            
            # Clean and extract from NER
            for entity in entities:
                entity_type = entity.get('entity_group', '')
                word = entity.get('word', '').replace(' ', '').replace('##', '')
                
                # Only use NER if regex missed it
                if entity_type in ['Name', 'PERSON'] and not result['name'] and len(word) > 3:
                    result['name'] = word
                elif entity_type in ['Skills', 'SKILL'] and word not in result['skills'] and len(word) > 2:
                    result['skills'].append(word)
                elif entity_type in ['Degree', 'DEGREE'] and word not in result['degrees'] and len(word) > 3:
                    result['degrees'].append(word)
        except Exception as e:
            print(f"⚠️  NER supplement failed: {e}")
        
        return result
    
    def _empty_result(self) -> Dict:
        """Return empty structured result"""
        return {
            "name": "",
            "job_titles": [],
            "companies": [],
            "universities": [],
            "degrees": [],
            "skills": [],
            "locations": [],
            "email": "",
            "phone": ""
        }
    
    def _structure_entities(self, entities: List) -> Dict:
        """Convert NER output to structured format"""
        structured = {
            "name": [],
            "job_titles": [],
            "companies": [],
            "universities": [],
            "degrees": [],
            "skills": [],
            "locations": [],
            "emails": [],
            "phones": []
        }
        
        entity_map = {
            # Standard labels
            "PER": "name", "PERSON": "name", "Name": "name",
            "TITLE": "job_titles", "Designation": "job_titles",
            "ORG": "companies", "ORGANIZATION": "companies", "Companies worked at": "companies",
            "UNIVERSITY": "universities", "College Name": "universities",
            "DEGREE": "degrees", "Degree": "degrees", "Graduation Year": "degrees",
            "SKILL": "skills", "Skills": "skills",
            "LOC": "locations", "LOCATION": "locations", "Location": "locations",
            "EMAIL": "emails", "Email Address": "emails",
            "PHONE": "phones", "Phone": "phones"
        }
        
        for entity in entities:
            entity_type = entity.get("entity_group", "")
            text = entity.get("word", "").strip()
            
            if entity_type in entity_map and text:
                key = entity_map[entity_type]
                if text not in structured[key]:
                    structured[key].append(text)
        
        # Return first name, all others as lists
        return {
            "name": structured["name"][0] if structured["name"] else "",
            "job_titles": structured["job_titles"],
            "companies": structured["companies"],
            "universities": structured["universities"],
            "degrees": structured["degrees"],
            "skills": structured["skills"],
            "locations": structured["locations"],
            "email": structured["emails"][0] if structured["emails"] else "",
            "phone": structured["phones"][0] if structured["phones"] else ""
        }
    
    def _apply_fallbacks(self, structured: Dict, text: str) -> Dict:
        """Apply regex fallbacks for missed critical fields"""
        import re
        
        # Fallback: Email
        if not structured["email"]:
            email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
            if email_match:
                structured["email"] = email_match.group(0)
        
        # Fallback: Phone
        if not structured["phone"]:
            phone_patterns = [
                r'\+?\d{1,3}[-\s]?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}',
                r'\+?\d{10,}'
            ]
            for pattern in phone_patterns:
                phone_match = re.search(pattern, text)
                if phone_match:
                    structured["phone"] = phone_match.group(0)
                    break
        
        # Fallback: Name (from first line if not found)
        if not structured["name"]:
            lines = text.strip().split('\n')
            for line in lines[:5]:
                words = line.strip().split()
                if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w):
                    structured["name"] = ' '.join(words)
                    break
        
        return structured
    
    def _regex_fallback(self, text: str) -> Dict:
        """Complete regex-based extraction"""
        import re
        
        result = self._empty_result()
        
        # Extract email (handle various formats)
        email_match = re.search(r'\b[A-Za-z][A-Za-z0-9._%+-]*@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if email_match:
            result["email"] = email_match.group(0)
        
        # Extract phone (international and local)
        phone_patterns = [
            r'\+\d{10,15}',  # International: +918109617693
            r'\+?\d{1,3}[-\s.]?\(?\d{3}\)?[-\s.]?\d{3}[-\s.]?\d{4}',  # Formatted
            r'\d{10}'  # Plain 10 digits
        ]
        for pattern in phone_patterns:
            phone_match = re.search(pattern, text)
            if phone_match:
                result["phone"] = phone_match.group(0)
                break
        
        # Extract name - look for capitalized words near start
        lines = [l.strip() for l in text.split('\n') if l.strip()][:10]
        for line in lines:
            # Skip lines with dates, emails, phones, URLs
            if re.search(r'\d{4}|@|http|www|\+\d{10}', line):
                continue
            
            words = line.split()
            # Name: 2-4 capitalized words
            if 2 <= len(words) <= 4:
                if all(w[0].isupper() and w.isalpha() for w in words):
                    result["name"] = line
                    break
        
        # Extract skills
        skills_match = re.search(r'(?:SKILLS?|TECHNICAL SKILLS?|CORE COMPETENCIES)[:\s]*\n(.*?)(?:\n\n|\n[A-Z]{3,})', 
                                text, re.IGNORECASE | re.DOTALL)
        if skills_match:
            skills_text = skills_match.group(1)
            skills = re.split(r'[,;•\n|]', skills_text)
            result["skills"] = [s.strip() for s in skills if s.strip() and len(s.strip()) > 2][:20]
        
        # Extract education
        edu_match = re.search(r'(?:EDUCATION|ACADEMIC BACKGROUND)[:\s]*\n(.*?)(?:\n\n|\n[A-Z]{3,}|$)', 
                             text, re.IGNORECASE | re.DOTALL)
        if edu_match:
            edu_text = edu_match.group(1)
            degrees = re.findall(r'(?:Bachelor|Master|PhD|B\.?S\.?|M\.?S\.?|MBA|B\.?Tech|M\.?Tech)[^\n]*', edu_text, re.IGNORECASE)
            result["degrees"] = [d.strip() for d in degrees][:5]
        
        # Extract job titles from experience section
        exp_match = re.search(r'(?:EXPERIENCE|WORK HISTORY|EMPLOYMENT)[:\s]*\n(.*?)(?:\n\n[A-Z]{3,}|$)', 
                             text, re.IGNORECASE | re.DOTALL)
        if exp_match:
            exp_text = exp_match.group(1)[:500]
            titles = re.findall(r'(?:Senior|Junior|Lead|Principal)?\s*(?:Developer|Engineer|Analyst|Manager|Designer|Architect)[^\n]*', exp_text, re.IGNORECASE)
            result["job_titles"] = [t.strip() for t in titles][:5]
        
        return result
