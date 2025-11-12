"""
SOTA Specialist Pipeline
Orchestrates all 5 specialist components for 1.4s analysis
"""
from .ner_extractor import NERExtractor
from .semantic_matcher import SemanticMatcher
from .rule_engine import RuleEngine
from .sota_scorer import SOTAScorer
from .feedback_generator import FeedbackGenerator
from typing import Dict
import time

class SOTAPipeline:
    """Complete SOTA pipeline orchestrator"""
    
    def __init__(self):
        print("\n" + "="*80)
        print("INITIALIZING SOTA SPECIALIST PIPELINE")
        print("="*80)
        
        self.ner = NERExtractor()
        self.semantic = SemanticMatcher()
        self.rules = RuleEngine()
        self.scorer = SOTAScorer()
        self.feedback = FeedbackGenerator()
        
        print("\n✅ SOTA Pipeline Ready")
        print("="*80 + "\n")
    
    def analyze(self, resume_text: str, jd_text: str, jd_skills: list = None) -> Dict:
        """
        Complete SOTA analysis in ~1.4s
        
        Returns:
            {
                "final_score": 78.5,
                "grade": "C+",
                "breakdown": {...},
                "feedback": ["tip1", "tip2", "tip3"],
                "timing": {...}
            }
        """
        timing = {}
        
        # Step 1: NER Extraction (0.2s)
        start = time.time()
        structured = self.ner.extract(resume_text)
        timing["ner_extraction"] = time.time() - start
        
        # Step 2: Semantic Matching (0.1s)
        start = time.time()
        job_fit = self.semantic.calculate_job_fit(resume_text, jd_text)
        timing["semantic_matching"] = time.time() - start
        
        # Step 3: Rule Engine (0.1s)
        start = time.time()
        ats_score = self.rules.score_ats_format(resume_text)
        readability_score = self.rules.score_readability(resume_text)
        completeness_score = self.rules.score_completeness(structured)
        timing["rule_engine"] = time.time() - start
        
        # Step 4: Calculate Factor Scores (0.01s)
        start = time.time()
        
        # Keyword match
        resume_skills = structured.get("skills", [])
        keyword_score = self.scorer.calculate_keyword_match(resume_skills, jd_skills or [])
        
        # Experience score
        experience_score = self.scorer.calculate_experience_score(
            structured.get("job_titles", []),
            structured.get("companies", [])
        )
        
        # Quality score
        quality_score = self.scorer.calculate_quality_score(
            structured.get("universities", []),
            structured.get("degrees", [])
        )
        
        # Fairness (default 1.0 for MVP)
        fairness_score = 1.0
        
        # Aggregate scores
        factor_scores = {
            "ats_format": ats_score,
            "job_fit": job_fit,
            "keyword_match": keyword_score,
            "experience": experience_score,
            "readability": readability_score,
            "quality": quality_score,
            "fairness": fairness_score
        }
        
        result = self.scorer.calculate_final_score(factor_scores)
        timing["scoring"] = time.time() - start
        
        # Step 5: Generate Feedback (1.0s)
        start = time.time()
        
        # Identify weak factors
        weak_factors = [k for k, v in factor_scores.items() if v < 0.6]
        
        # Missing skills
        if jd_skills:
            jd_set = set(s.lower() for s in jd_skills)
            resume_set = set(s.lower() for s in resume_skills)
            missing_skills = list(jd_set - resume_set)
        else:
            missing_skills = []
        
        feedback = self.feedback.generate_feedback({
            "final_score": result["final_score"],
            "missing_skills": missing_skills,
            "weak_factors": weak_factors
        })
        timing["feedback_generation"] = time.time() - start
        
        # Compile final result
        result.update({
            "feedback": feedback,
            "structured_data": structured,
            "missing_skills": missing_skills,
            "timing": timing,
            "total_time": sum(timing.values())
        })
        
        return result
