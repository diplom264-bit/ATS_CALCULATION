"""
Hybrid Entity Extractor: RegEx Primary + NER Supplement
Architecture: High-reliability RegEx for PII, NER for contextual entities
"""
import re
import torch
from transformers import pipeline
from typing import Dict, List

class HybridExtractor:
    """
    Implements the "RegEx as Primary, NER as Supplement" architecture.
    
    1. Runs a high-reliability RegEx pass to find PII.
    2. Runs a NER pass to find complex, contextual entities.
    3. Merges the results, prioritizing RegEx, to build the feature_store.
    """
    
    def __init__(self, model_cache_dir="models/ner_model"):
        print("🔧 Loading Hybrid Extractor...")
        
        # Load NER model
        try:
            device = 0 if torch.cuda.is_available() else -1
            self.ner_pipeline = pipeline(
                "token-classification",
                model=model_cache_dir,
                device=device,
                aggregation_strategy="average"
            )
            print(f"✅ NER model loaded (GPU: {torch.cuda.is_available()})")
        except Exception as e:
            print(f"⚠️  NER model failed to load: {e}. Using RegEx only.")
            self.ner_pipeline = None

        # Compiled RegEx patterns for high-speed, reliable PII extraction
        self.regex_patterns = {
            'EMAIL': re.compile(r'\b[A-Za-z][A-Za-z0-9._%+-]*@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'PHONE': re.compile(r'\+\d{10,15}|\d{10}'),
            'LINKEDIN_URL': re.compile(r'linkedin\.com/in/[\w-]+')
        }

    def _extract_with_regex(self, text: str) -> List[Dict]:
        """Primary pass: Use high-reliability RegEx for PII"""
        entities = []
        
        # 1. Extract PII (Email, Phone, LinkedIn)
        for label, pattern in self.regex_patterns.items():
            for match in pattern.finditer(text):
                entities.append({
                    "label": label,
                    "text": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "source": "regex"
                })
        
        # 2. Extract Name: Find pattern near email/phone (names typically appear with contact info)
        # Look for 2-3 capitalized words within 100 chars before email or phone
        contact_positions = []
        for entity in entities:
            if entity['label'] in ['EMAIL', 'PHONE']:
                contact_positions.append(entity['start'])
        
        if contact_positions:
            search_start = max(0, min(contact_positions) - 100)
            search_end = min(contact_positions) + 50
            search_text = text[search_start:search_end]
            
            name_pattern = re.compile(r'\b([A-Z][a-z]+\s[A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\b')
            for match in name_pattern.finditer(search_text):
                candidate = match.group(1)
                entities.append({
                    "label": "NAME",
                    "text": candidate,
                    "start": search_start + match.start(1),
                    "end": search_start + match.end(1),
                    "source": "regex"
                })
                break
        
        # 3. Extract Skills section
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
        
        # 4. Extract Education
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
                
        return entities

    def _extract_with_ner(self, text: str) -> List[Dict]:
        """Supplemental pass: Use NER model for complex, contextual entities"""
        if not self.ner_pipeline:
            return []
            
        try:
            ner_results = self.ner_pipeline(text[:2000])
            
            entities = []
            for result in ner_results:
                # Clean tokenizer artifacts
                word = result['word'].replace(' ', '').replace('##', '')
                if word and len(word) > 1:
                    entities.append({
                        "label": result['entity_group'].upper(),
                        "text": word,
                        "start": result['start'],
                        "end": result['end'],
                        "source": "ner"
                    })
            return entities
        except Exception as e:
            print(f"⚠️  NER extraction failed: {e}")
            return []

    def extract(self, text: str) -> Dict:
        """
        Main extraction method.
        Returns structured data compatible with existing pipeline.
        """
        # 1. Run Primary Extractor (RegEx)
        regex_entities = self._extract_with_regex(text)
        
        # 2. Run Supplemental Extractor (NER)
        ner_entities = self._extract_with_ner(text)
        
        # 3. Combine and De-duplicate (prioritize RegEx)
        final_entities = list(regex_entities)
        regex_labels = {e['label'] for e in regex_entities}
        
        for ner_entity in ner_entities:
            if ner_entity['label'] not in regex_labels:
                final_entities.append(ner_entity)
        
        # 4. Convert to structured format for compatibility
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
        
        for entity in final_entities:
            label = entity['label']
            text = entity['text']
            
            if label == 'NAME' and not result['name']:
                result['name'] = text
            elif label == 'EMAIL' and not result['email']:
                result['email'] = text
            elif label == 'PHONE' and not result['phone']:
                result['phone'] = text
            elif label == 'SKILL' and text not in result['skills']:
                result['skills'].append(text)
            elif label == 'DEGREE' and text not in result['degrees']:
                result['degrees'].append(text)
            elif label in ['DESIGNATION', 'JOB_TITLE'] and text not in result['job_titles']:
                result['job_titles'].append(text)
        
        return result
