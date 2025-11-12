"""
ATS Resume Analyzer - Production Service
Integrates ML-enhanced analysis with full pipeline
"""
from typing import Dict, Optional
from .ml_enhanced_analyzer import MLEnhancedAnalyzer

class ATSAnalyzer:
    """Complete ATS analysis pipeline with ML"""
    
    def __init__(self):
        self.analyzer = MLEnhancedAnalyzer()
        self.extractor = self.analyzer.parser  # For backward compatibility
    
    def analyze_resume(self, resume_file_path: str, resume_text: str, job_description: Optional[str] = None) -> Dict:
        """
        Complete ML-enhanced resume analysis
        
        Args:
            resume_file_path: Path to resume file
            resume_text: Extracted resume text
            job_description: Optional JD text for matching
            
        Returns:
            Complete analysis with ML scores and recommendations
        """
        # Run ML-enhanced analysis
        result = self.analyzer.analyze(resume_file_path, job_description)
        
        if result['status'] != 'ok':
            return {"error": "Analysis failed", "status": result['status']}
        
        entities = result['extraction']
        analysis = result.get('analysis', {})
        
        # Format response
        return {
            "score": analysis.get('final_score', 0),
            "grade": analysis.get('grade', 'F'),
            "breakdown": analysis.get('breakdown', {}),
            "feedback": analysis.get('feedback', []),
            "ml_score": result.get('ml_score'),
            "ml_explanation": result.get('ml_explanation'),
            "semantic_score": result.get('semantic_score'),
            "entities": entities,
            "analysis": {
                "has_contact_info": bool(entities['email'] or entities['phone']),
                "has_skills": len(entities['skills']) > 0,
                "has_experience": len(entities['companies']) > 0,
                "has_education": len(entities['degrees']) > 0,
                "skill_count": len(entities['skills']),
                "experience_count": len(entities['companies']),
                "education_count": len(entities['degrees']),
                "total_checks": analysis.get('total_checks', 0)
            }
        }
    

