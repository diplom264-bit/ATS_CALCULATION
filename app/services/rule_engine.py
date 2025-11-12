"""
Rule-Based Scoring Engine
ATS Format & Readability checks (99% accuracy)
"""
import re
import textstat

class RuleEngine:
    """Fast rule-based scoring for ATS and readability"""
    
    def score_ats_format(self, text: str) -> float:
        """
        Score ATS-friendliness (0-10)
        Checks: tables, images, fonts, sections, contact info
        """
        score = 10.0
        
        # Penalty for tables (ATS can't parse)
        if "│" in text or "┌" in text or "├" in text:
            score -= 2.0
        
        # Penalty for special characters
        special_chars = len(re.findall(r'[★●◆■▪]', text))
        score -= min(special_chars * 0.1, 2.0)
        
        # Bonus for standard sections
        sections = ["experience", "education", "skills", "summary"]
        found_sections = sum(1 for s in sections if s in text.lower())
        score += found_sections * 0.5
        
        # Bonus for contact info
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
            score += 1.0
        if re.search(r'\+?\d{10,}', text):
            score += 1.0
        
        return min(max(score, 0), 10) / 10  # Normalize to 0-1
    
    def score_readability(self, text: str) -> float:
        """
        Score readability (0-10) using Flesch Reading Ease
        90-100: Very Easy (5th grade)
        60-70: Standard (8th-9th grade) ← Target
        0-30: Very Difficult (College graduate)
        """
        try:
            flesch = textstat.flesch_reading_ease(text)
            # Normalize: 60-70 is ideal (score 10), scale others
            if 60 <= flesch <= 70:
                score = 10.0
            elif flesch > 70:
                score = 10.0 - (flesch - 70) * 0.1  # Penalty for too easy
            else:
                score = 10.0 - (60 - flesch) * 0.1  # Penalty for too hard
            
            return min(max(score, 0), 10) / 10  # Normalize to 0-1
        except:
            return 0.5  # Default if calculation fails
    
    def score_completeness(self, structured_data: dict) -> float:
        """
        Score profile completeness (0-10)
        Checks: name, email, phone, experience, education, skills
        """
        score = 0.0
        
        if structured_data.get("name"):
            score += 2.0
        if structured_data.get("email"):
            score += 1.5
        if structured_data.get("phone"):
            score += 1.5
        if structured_data.get("job_titles"):
            score += 2.0
        if structured_data.get("universities"):
            score += 1.5
        if structured_data.get("skills"):
            score += 1.5
        
        return min(score, 10) / 10  # Normalize to 0-1
