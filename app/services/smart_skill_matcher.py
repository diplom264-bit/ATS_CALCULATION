"""
Smart Skill Matcher with KB-powered semantic matching
"""
from typing import List, Tuple, Set, Optional
from difflib import SequenceMatcher
import sys
from pathlib import Path

# Use KB singleton
try:
    from app.services.knowledge_base_engine import KnowledgeBase
    KB_AVAILABLE = True
except ImportError:
    KB_AVAILABLE = False

class SmartSkillMatcher:
    """Intelligent skill matching with KB semantic search and fuzzy logic"""
    
    # Fallback equivalents (used if KB unavailable)
    EQUIVALENTS = {
        'sql': ['t-sql', 'sql server', 'mysql', 'postgresql', 'plsql'],
        'power bi': ['powerbi', 'power bi desktop', 'power bi service', 'power bi dataflows'],
        'etl': ['etl automation', 'etl tools', 'etl processes', 'data integration'],
        'data modeling': ['data modelling', 'database modeling', 'data model'],
        'data warehousing': ['data warehouse', 'dwh', 'data mart'],
        'python': ['python3', 'python 3', 'py'],
        'javascript': ['js', 'node.js', 'nodejs'],
        'machine learning': ['ml', 'deep learning', 'neural networks'],
        'aws': ['amazon web services', 'ec2', 's3', 'lambda'],
        'azure': ['microsoft azure', 'azure cloud'],
        'docker': ['containerization', 'containers'],
        'kubernetes': ['k8s', 'container orchestration'],
        'tableau': ['tableau desktop', 'tableau server'],
        'excel': ['microsoft excel', 'ms excel', 'spreadsheets'],
        'communication': ['communication skills', 'interpersonal skills'],
        'problem solving': ['problem-solving', 'analytical skills', 'critical thinking']
    }
    
    def __init__(self, fuzzy_threshold: float = 0.8, kb_threshold: float = 0.5):
        """
        Initialize matcher
        
        Args:
            fuzzy_threshold: Minimum similarity score (0-1) for fuzzy matching
            kb_threshold: Minimum KB semantic similarity (0-1)
        """
        self.fuzzy_threshold = fuzzy_threshold
        self.kb_threshold = kb_threshold
        self.kb = None
        
        # Use KB singleton
        if KB_AVAILABLE:
            try:
                from app.services.kb_singleton import get_kb_instance
                self.kb = get_kb_instance()
            except Exception:
                pass
    
    def match_skills(self, resume_skills: List[str], jd_skills: List[str]) -> Tuple[List[str], List[str], float]:
        """
        Match resume skills against JD requirements
        
        Args:
            resume_skills: List of skills from resume
            jd_skills: List of required skills from JD
            
        Returns:
            (matched_skills, missing_skills, match_percentage)
        """
        if not jd_skills:
            return [], [], 100.0
        
        # Normalize skills
        resume_normalized = [self._normalize(s) for s in resume_skills]
        jd_normalized = [self._normalize(s) for s in jd_skills]
        
        matched = set()
        missing = []
        
        for jd_skill in jd_skills:
            jd_norm = self._normalize(jd_skill)
            
            # Check for match
            if self._is_match(jd_norm, resume_normalized):
                matched.add(jd_skill)
            else:
                missing.append(jd_skill)
        
        match_pct = (len(matched) / len(jd_skills)) * 100 if jd_skills else 100.0
        
        return list(matched), missing, match_pct
    
    def _normalize(self, skill: str) -> str:
        """Normalize skill string"""
        return skill.lower().strip()
    
    def _is_match(self, jd_skill: str, resume_skills: List[str]) -> bool:
        """Check if JD skill matches any resume skill"""
        
        # 1. Exact match
        if jd_skill in resume_skills:
            return True
        
        # 2. Substring match (e.g., "power bi" in "power bi desktop")
        for resume_skill in resume_skills:
            if jd_skill in resume_skill or resume_skill in jd_skill:
                return True
        
        # 3. KB semantic matching (if available)
        if self.kb:
            try:
                # Search KB for JD skill
                jd_results = self.kb.search(jd_skill, type_filter='skill', top_k=5)
                if jd_results:
                    # Get top match for JD skill
                    jd_kb_skill = jd_results[0]['label'].lower()
                    
                    # Check if any resume skill matches the same KB skill
                    for resume_skill in resume_skills:
                        resume_results = self.kb.search(resume_skill, type_filter='skill', top_k=1)
                        if resume_results:
                            resume_kb_skill = resume_results[0]['label'].lower()
                            
                            # If both map to same KB skill, they match
                            if jd_kb_skill == resume_kb_skill and resume_results[0]['score'] >= self.kb_threshold:
                                return True
                            
                            # Or if resume skill is semantically similar to JD skill
                            if resume_results[0]['score'] >= self.kb_threshold:
                                # Check if resume skill contains JD skill or vice versa
                                if jd_skill in resume_kb_skill or resume_kb_skill in jd_skill:
                                    return True
            except Exception as e:
                pass  # Fall through to other methods
        
        # 4. Check equivalents (fallback)
        for base_skill, variants in self.EQUIVALENTS.items():
            if jd_skill == base_skill or jd_skill in variants:
                # JD skill is in our equivalents, check if resume has any variant
                for resume_skill in resume_skills:
                    if resume_skill == base_skill or resume_skill in variants:
                        return True
        
        # 5. Fuzzy match (last resort)
        for resume_skill in resume_skills:
            similarity = SequenceMatcher(None, jd_skill, resume_skill).ratio()
            if similarity >= self.fuzzy_threshold:
                return True
        
        return False
    
    def get_match_details(self, resume_skills: List[str], jd_skills: List[str]) -> dict:
        """Get detailed matching information"""
        
        matched, missing, match_pct = self.match_skills(resume_skills, jd_skills)
        
        # Find which resume skills matched which JD skills
        match_map = {}
        for jd_skill in matched:
            jd_norm = self._normalize(jd_skill)
            resume_normalized = [self._normalize(s) for s in resume_skills]
            
            for i, resume_norm in enumerate(resume_normalized):
                if self._is_match(jd_norm, [resume_norm]):
                    match_map[jd_skill] = resume_skills[i]
                    break
        
        return {
            'matched_skills': matched,
            'missing_skills': missing,
            'match_percentage': match_pct,
            'match_map': match_map,
            'total_jd_skills': len(jd_skills),
            'total_resume_skills': len(resume_skills)
        }
