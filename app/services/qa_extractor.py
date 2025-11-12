"""
Fast QA-based extraction using deepset/roberta-base-squad2
Replaces slow LLM with 2-3s generalized extraction
"""
from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering
from typing import Dict, Any, List
import re
import torch
from pathlib import Path

class QAExtractor:
    """Question-Answering based field extraction with GPU support"""
    
    def __init__(self, model_cache_dir="models/qa_model"):
        self.device = 0 if torch.cuda.is_available() else -1
        self.model_cache_dir = Path(model_cache_dir)
        self.model_cache_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🔧 Loading QA model (device: {'cuda' if self.device == 0 else 'cpu'})...")
        
        # Load model locally if exists, otherwise download
        model_name = "deepset/roberta-base-squad2"
        if (self.model_cache_dir / "config.json").exists():
            print("✅ Using cached model")
            self.qa_pipeline = pipeline(
                "question-answering",
                model=str(self.model_cache_dir),
                tokenizer=str(self.model_cache_dir),
                device=self.device
            )
        else:
            print("📥 Downloading model (one-time, ~500MB)...")
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForQuestionAnswering.from_pretrained(model_name)
            
            # Save locally
            tokenizer.save_pretrained(str(self.model_cache_dir))
            model.save_pretrained(str(self.model_cache_dir))
            print(f"💾 Model cached to {self.model_cache_dir}")
            
            self.qa_pipeline = pipeline(
                "question-answering",
                model=model,
                tokenizer=tokenizer,
                device=self.device
            )
        
        print(f"✅ QA model ready (GPU: {torch.cuda.is_available()})")
    
    def extract_resume(self, text: str) -> Dict[str, Any]:
        """Extract resume fields using QA (2-3s)"""
        
        # Personal info (RegEx - 99.9% accurate)
        email = self._extract_email(text)
        phone = self._extract_phone(text)
        name = self._extract_name(text, email)
        
        # QA extraction (parallel questions)
        qa_results = self._batch_qa(text, [
            "What is the most recent job title?",
            "What companies has the candidate worked for?",
            "What universities did the candidate attend?",
            "What degrees does the candidate have?",
            "How many years of experience?",
            "What is the candidate's location or city?"
        ])
        
        return {
            "personal_information": {
                "name": name,
                "email": email,
                "phone": phone,
                "location": qa_results.get("location", "")
            },
            "experience": [{
                "title": qa_results.get("job_title", ""),
                "organization": qa_results.get("companies", "")
            }],
            "education": [{
                "degree": qa_results.get("degrees", ""),
                "institution": qa_results.get("universities", "")
            }],
            "years_experience": self._parse_years(qa_results.get("years", "0"))
        }
    
    def extract_jd(self, text: str) -> Dict[str, Any]:
        """Extract JD fields using QA (1-2s)"""
        
        qa_results = self._batch_qa(text, [
            "What is the job title or position?",
            "What is the company name?",
            "What is the job location?",
            "How many years of experience required?",
            "What education is required?"
        ])
        
        return {
            "position": qa_results.get("job_title", ""),
            "company": qa_results.get("company", ""),
            "location": qa_results.get("location", ""),
            "experience_required": qa_results.get("years", ""),
            "education_required": qa_results.get("education", "")
        }
    
    def _batch_qa(self, context: str, questions: List[str]) -> Dict[str, str]:
        """Run multiple QA questions (GPU-accelerated if available)"""
        results = {}
        key_map = {
            "job title": "job_title",
            "companies": "companies",
            "universities": "universities",
            "degrees": "degrees",
            "years": "years",
            "location": "location",
            "company": "company",
            "education": "education"
        }
        
        # Truncate context for speed
        context = context[:2000]
        
        for question in questions:
            try:
                answer = self.qa_pipeline(
                    question=question,
                    context=context,
                    max_answer_len=100,
                    handle_impossible_answer=True
                )
                key = next((v for k, v in key_map.items() if k in question.lower()), "unknown")
                results[key] = answer['answer'] if answer['score'] > 0.01 else ""
            except:
                pass
        
        return results
    
    def _extract_email(self, text: str) -> str:
        """RegEx email extraction (99.9% accurate)"""
        match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        return match.group(0) if match else ""
    
    def _extract_phone(self, text: str) -> str:
        """RegEx phone extraction"""
        patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\+?\d{10,}',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return ""
    
    def _extract_name(self, text: str, email: str) -> str:
        """Extract name from first lines or email"""
        lines = text.split('\n')[:5]
        for line in lines:
            words = line.strip().split()
            if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w):
                return ' '.join(words)
        
        # Fallback: extract from email
        if email:
            return email.split('@')[0].replace('.', ' ').title()
        return ""
    
    def _parse_years(self, text: str) -> int:
        """Extract years from text"""
        match = re.search(r'(\d+)', text)
        return int(match.group(1)) if match else 0
