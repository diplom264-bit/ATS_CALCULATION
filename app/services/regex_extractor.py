"""Robust regex-based entity extraction for resumes"""
import re
from typing import Dict, List

class RegexExtractor:
    """Fast, reliable regex-based extraction"""
    
    @staticmethod
    def extract(text: str) -> Dict:
        """Extract entities using regex patterns"""
        return {
            "name": RegexExtractor._extract_name(text),
            "email": RegexExtractor._extract_email(text),
            "phone": RegexExtractor._extract_phone(text),
            "skills": RegexExtractor._extract_skills(text),
            "education": RegexExtractor._extract_education(text),
            "experience": RegexExtractor._extract_experience(text)
        }
    
    @staticmethod
    def _extract_name(text: str) -> str:
        """Extract name from first few lines"""
        lines = [l.strip() for l in text.split('\n') if l.strip()][:5]
        for line in lines:
            words = line.split()
            if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w):
                if not re.search(r'@|http|www|\d{3}', line):
                    return line
        return ""
    
    @staticmethod
    def _extract_email(text: str) -> str:
        """Extract email address"""
        match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        return match.group(0) if match else ""
    
    @staticmethod
    def _extract_phone(text: str) -> str:
        """Extract phone number"""
        patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\d{10,}'
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return ""
    
    @staticmethod
    def _extract_skills(text: str) -> List[str]:
        """Extract skills section"""
        skills_match = re.search(r'(?:SKILLS?|TECHNICAL SKILLS?|CORE COMPETENCIES)[:\s]*\n(.*?)(?:\n\n|\n[A-Z]{2,})', 
                                text, re.IGNORECASE | re.DOTALL)
        if skills_match:
            skills_text = skills_match.group(1)
            skills = re.split(r'[,;•\n]', skills_text)
            return [s.strip() for s in skills if s.strip() and len(s.strip()) > 2]
        return []
    
    @staticmethod
    def _extract_education(text: str) -> List[str]:
        """Extract education entries"""
        edu_match = re.search(r'(?:EDUCATION|ACADEMIC)[:\s]*\n(.*?)(?:\n\n|\n[A-Z]{2,}|$)', 
                             text, re.IGNORECASE | re.DOTALL)
        if edu_match:
            edu_text = edu_match.group(1)
            degrees = re.findall(r'(?:Bachelor|Master|PhD|B\.?S\.?|M\.?S\.?|MBA)[^\n]*', edu_text, re.IGNORECASE)
            return [d.strip() for d in degrees]
        return []
    
    @staticmethod
    def _extract_experience(text: str) -> List[Dict]:
        """Extract work experience entries"""
        exp_match = re.search(r'(?:EXPERIENCE|WORK HISTORY|EMPLOYMENT)[:\s]*\n(.*?)(?:\n\n[A-Z]{2,}|$)', 
                             text, re.IGNORECASE | re.DOTALL)
        if exp_match:
            exp_text = exp_match.group(1)
            entries = re.split(r'\n(?=[A-Z][a-z]+ \d{4}|\d{4}[-–])', exp_text)
            return [{"text": e.strip()} for e in entries if e.strip()]
        return []
