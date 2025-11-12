"""
LLM-Based Feedback Generator
Generates human-like, actionable feedback using templates and patterns
"""
from typing import List, Dict

class FeedbackGenerator:
    """Generates actionable feedback from analysis results"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """Load feedback templates"""
        return {
            'low_keyword_match': [
                "Add {count} key terms from the job description: {keywords}",
                "Include industry-specific keywords: {keywords}",
                "Strengthen alignment by adding: {keywords}"
            ],
            'missing_quantification': [
                "Quantify achievements with metrics (e.g., 'Increased sales by 25%')",
                "Add numbers to demonstrate impact (percentages, dollar amounts, time saved)",
                "Use data-driven results to strengthen bullet points"
            ],
            'weak_action_verbs': [
                "Replace weak verbs with strong action words: {suggestions}",
                "Start bullets with impactful verbs like: {suggestions}",
                "Use power verbs: {suggestions}"
            ],
            'employment_gaps': [
                "Address {gap_months}-month gap between {dates}",
                "Consider explaining career break from {start} to {end}",
                "Fill employment gap with relevant activities or training"
            ],
            'low_semantic_match': [
                "Expand on relevant experience in {domain}",
                "Highlight transferable skills for this role",
                "Connect your background more explicitly to job requirements"
            ],
            'formatting_issues': [
                "Use consistent formatting throughout (fonts, spacing, bullets)",
                "Ensure ATS-friendly format: {issues}",
                "Improve document structure for better parsing"
            ],
            'missing_skills': [
                "Add these relevant skills if applicable: {skills}",
                "Consider highlighting: {skills}",
                "Include technical proficiencies: {skills}"
            ],
            'readability': [
                "Simplify complex sentences for better clarity",
                "Break long paragraphs into concise bullet points",
                "Use clear, professional language throughout"
            ]
        }
    
    def generate_feedback(self, analysis_results: Dict, parsed_data: Dict, jd_text: str = "") -> List[str]:
        """Generate prioritized feedback based on analysis"""
        feedback = []
        scores = analysis_results.get('breakdown', {})
        
        # Priority 1: Critical issues (score < 50)
        if scores.get('keyword_alignment', 100) < 50:
            feedback.extend(self._generate_keyword_feedback(parsed_data, jd_text))
        
        if scores.get('semantic_fit', 100) < 50:
            feedback.append(self.templates['low_semantic_match'][0].format(domain="target role"))
        
        # Priority 2: Important improvements (score < 70)
        if scores.get('quantified_impact', 100) < 70:
            feedback.append(self.templates['missing_quantification'][0])
        
        if scores.get('professional_language', 100) < 70:
            feedback.append(self.templates['weak_action_verbs'][0].format(
                suggestions="Led, Achieved, Implemented, Optimized"
            ))
        
        # Priority 3: Enhancement opportunities (score < 85)
        if scores.get('file_layout', 100) < 85:
            feedback.append(self.templates['formatting_issues'][0].format(
                issues="consistent fonts, clear sections"
            ))
        
        if scores.get('readability', 100) < 85:
            feedback.append(self.templates['readability'][0])
        
        # Limit to top 5 most impactful items
        return feedback[:5]
    
    def _generate_keyword_feedback(self, parsed_data: Dict, jd_text: str) -> List[str]:
        """Generate keyword-specific feedback"""
        if not jd_text:
            return [self.templates['low_keyword_match'][0].format(
                count=3, keywords="relevant technical terms"
            )]
        
        # Extract missing keywords (simplified)
        jd_words = set(jd_text.lower().split())
        resume_skills = set(s.lower() for s in parsed_data.get('skills', []))
        
        common_tech = {'python', 'java', 'sql', 'aws', 'docker', 'kubernetes', 'react', 'api'}
        missing = (jd_words & common_tech) - resume_skills
        
        if missing:
            return [self.templates['low_keyword_match'][0].format(
                count=len(missing), keywords=", ".join(list(missing)[:5])
            )]
        
        return [self.templates['low_keyword_match'][1].format(keywords="job-specific terms")]
    
    def generate_summary(self, final_score: float, grade: str) -> str:
        """Generate overall summary"""
        if final_score >= 85:
            return f"Excellent resume (Grade {grade}). Strong ATS compatibility with minor refinements possible."
        elif final_score >= 70:
            return f"Good resume (Grade {grade}). Solid foundation with room for targeted improvements."
        elif final_score >= 55:
            return f"Fair resume (Grade {grade}). Needs significant enhancements for better ATS performance."
        else:
            return f"Needs improvement (Grade {grade}). Major revisions required for ATS optimization."
