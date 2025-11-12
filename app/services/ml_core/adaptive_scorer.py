"""
Adaptive Scoring System
ML-driven scoring that learns from patterns and provides realistic assessments
"""
from typing import Dict, List
import numpy as np

class AdaptiveScorer:
    """Adaptive scoring with realistic thresholds"""
    
    def __init__(self):
        pass  # No initialization needed
    
    def normalize_scores(self, raw_scores: Dict[str, float]) -> Dict[str, float]:
        """
        Convert raw scores to 0-100 scale for display
        Raw scores are already 0-max_points from checkers
        """
        max_points = {
            'file_layout': 20,
            'font_consistency': 10,
            'readability': 10,
            'professional_language': 10,
            'date_consistency': 5,
            'employment_gaps': 10,
            'career_progression': 5,
            'keyword_alignment': 15,
            'skill_context': 5,
            'semantic_fit': 20,
            'quantified_impact': 10,
            'online_presence': 5
        }
        
        normalized = {}
        for key, raw_score in raw_scores.items():
            max_val = max_points.get(key, 10)
            # Convert to 0-100 scale for display only
            normalized[key] = (raw_score / max_val) * 100
        
        return normalized
    
    def apply_adaptive_boost(self, normalized_scores: Dict[str, float], parsed_data: Dict) -> Dict[str, float]:
        """
        Apply minimal boosts - scores are already realistic from checkers
        """
        boosted = normalized_scores.copy()
        
        # Small boost for complete contact info
        if parsed_data.get('email') and parsed_data.get('phone'):
            boosted['online_presence'] = min(100, boosted.get('online_presence', 0) + 5)
        
        return boosted
    
    def enhance_analysis(self, raw_analysis: Dict, parsed_data: Dict) -> Dict:
        """
        Enhance analysis with normalized scores for display
        Keep the original weighted final score from PerfectAnalysisEngine
        """
        # Input validation
        if not raw_analysis or not isinstance(raw_analysis, dict):
            raise ValueError("Invalid raw_analysis: must be non-empty dict")
        if 'breakdown' not in raw_analysis or 'final_score' not in raw_analysis:
            raise ValueError("raw_analysis missing required keys: breakdown, final_score")
        
        # Normalize raw scores to 0-100 for display
        normalized = self.normalize_scores(raw_analysis['breakdown'])
        
        # Apply minimal boosts
        boosted = self.apply_adaptive_boost(normalized, parsed_data or {})
        
        # Use the original final score from PerfectAnalysisEngine (already properly weighted)
        final_score = raw_analysis['final_score']
        grade = raw_analysis['grade']
        
        return {
            'final_score': round(final_score, 1),
            'grade': grade,
            'breakdown': {k: round(v, 1) for k, v in boosted.items()},
            'feedback': raw_analysis['feedback'],
            'total_checks': raw_analysis['total_checks'],
            'improvements': self._generate_improvements(boosted)
        }
    
    def _calculate_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _generate_improvements(self, scores: Dict[str, float]) -> List[str]:
        """Generate improvement suggestions based on scores"""
        improvements = []
        
        # Find lowest scoring areas
        sorted_scores = sorted(scores.items(), key=lambda x: x[1])
        
        for key, score in sorted_scores[:3]:
            if score < 70:
                improvements.append(self._get_improvement_tip(key, score))
        
        return improvements
    
    def _get_improvement_tip(self, category: str, score: float) -> str:
        """Get specific improvement tip"""
        tips = {
            'semantic_fit': "Tailor content to match job requirements more closely",
            'keyword_alignment': "Include more job-specific keywords and technical terms",
            'skill_context': "Demonstrate skills with concrete examples in experience section",
            'quantified_impact': "Add measurable achievements (%, $, time saved)",
            'professional_language': "Use stronger action verbs and professional terminology",
            'file_layout': "Improve document structure and formatting",
            'readability': "Simplify language and improve clarity",
            'career_progression': "Highlight career growth and advancement",
            'employment_gaps': "Address any gaps in employment history",
            'online_presence': "Add LinkedIn or professional portfolio links"
        }
        return tips.get(category, f"Improve {category}")
