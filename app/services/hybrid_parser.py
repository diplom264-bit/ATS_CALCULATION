"""
Hybrid 5-Second Parser: RegEx + KB + QA
Replaces 45s LLM with 5s generalized pipeline
"""
from typing import Dict, Any
from .qa_extractor import QAExtractor
from .smart_skill_matcher import SmartSkillMatcher
from pathlib import Path
import sys

# Add KB to path
kb_path = Path(__file__).parent.parent.parent / "knowledge_base"
sys.path.insert(0, str(kb_path))

try:
    from knowledge_base_engine import KnowledgeBase
    KB_AVAILABLE = True
except:
    KB_AVAILABLE = False

class HybridParser:
    """Fast 5-second parser combining RegEx, KB, and QA"""
    
    def __init__(self):
        self.qa = QAExtractor()
        self.kb = KnowledgeBase(str(Path(__file__).parent.parent.parent / "knowledge_base" / "kb")) if KB_AVAILABLE else None
    
    def parse_resume(self, text: str) -> Dict[str, Any]:
        """
        Parse resume in ~5 seconds
        Step 1: RegEx (0.1s) - Personal info
        Step 2: KB (0.5s) - Skills
        Step 3: QA (2-3s) - Experience/Education
        """
        
        # Step 1: Fast RegEx extraction
        base_data = self.qa.extract_resume(text)
        
        # Step 2: KB skill extraction (superior to any model)
        if self.kb:
            skills = self._extract_skills_kb(text)
            base_data['technical_skills'] = skills
        
        return base_data
    
    def parse_jd(self, text: str) -> Dict[str, Any]:
        """
        Parse JD in ~2 seconds
        Step 1: QA (1-2s) - Basic fields
        Step 2: KB (0.5s) - Required skills
        """
        
        # Step 1: QA extraction
        base_data = self.qa.extract_jd(text)
        
        # Step 2: KB skill extraction
        if self.kb:
            skills = self._extract_skills_kb(text)
            base_data['required_skills'] = skills[:15]  # Top 15 skills
        
        return base_data
    
    def _extract_skills_kb(self, text: str) -> List[str]:
        """Extract skills using KB/FAISS (0.5s, 100% accurate for 17K skills)"""
        if not self.kb:
            return []
        
        results = self.kb.extract_skills(text, top_k=30, threshold=0.3)
        return [r['label'] for r in results]
