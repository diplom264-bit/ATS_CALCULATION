"""
SOTA Weighted Scoring Engine
Combines all specialist models with transparent weights
"""
from typing import Dict

class SOTAScorer:
    """Transparent weighted scoring following SOTA blueprint"""
    
    # Weights from SOTA architecture
    WEIGHTS = {
        "ats_format": 0.20,      # ATS/Parsing friendliness
        "job_fit": 0.20,         # Semantic job-fit (S-BERT)
        "keyword_match": 0.25,   # Keyword alignment
        "experience": 0.15,      # Experience & impact
        "readability": 0.10,     # Readability & formatting
        "quality": 0.05,         # Signals of quality
        "fairness": 0.05         # Fairness metrics
    }
    
    def calculate_final_score(self, factor_scores: Dict[str, float]) -> Dict:
        """
        Calculate weighted final score
        
        Args:
            factor_scores: Dict with keys matching WEIGHTS
            
        Returns:
            {
                "final_score": 78.5,
                "grade": "C+",
                "breakdown": {...},
                "factors": {...}
            }
        """
        # Calculate weighted sum
        final_score = 0.0
        breakdown = {}
        
        for factor, weight in self.WEIGHTS.items():
            score = factor_scores.get(factor, 0.0)
            contribution = score * weight * 100  # Convert to 0-100 scale
            final_score += contribution
            breakdown[factor] = {
                "score": score,
                "weight": weight,
                "contribution": contribution
            }
        
        # Determine grade
        grade = self._calculate_grade(final_score)
        
        return {
            "final_score": round(final_score, 1),
            "grade": grade,
            "breakdown": breakdown,
            "factors": factor_scores
        }
    
    def _calculate_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def calculate_keyword_match(self, resume_skills: list, jd_skills: list) -> float:
        """Calculate keyword match percentage"""
        if not jd_skills:
            return 1.0
        
        resume_set = set(s.lower() for s in resume_skills)
        jd_set = set(s.lower() for s in jd_skills)
        
        matched = len(resume_set & jd_set)
        total = len(jd_set)
        
        return matched / total if total > 0 else 0.0
    
    def calculate_experience_score(self, job_titles: list, companies: list) -> float:
        """Score experience quality"""
        score = 0.0
        
        # Has job titles
        if job_titles:
            score += 0.5
        
        # Has companies
        if companies:
            score += 0.3
        
        # Multiple experiences
        if len(job_titles) > 1:
            score += 0.2
        
        return min(score, 1.0)
    
    def calculate_quality_score(self, universities: list, degrees: list) -> float:
        """Score quality signals (education)"""
        score = 0.0
        
        if universities:
            score += 0.5
        if degrees:
            score += 0.5
        
        return min(score, 1.0)
