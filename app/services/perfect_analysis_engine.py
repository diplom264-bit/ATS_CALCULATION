"""
Perfect Analysis Engine
Orchestrates all checker modules for comprehensive resume analysis
"""
from typing import Dict, List, Optional
from .checkers.formatting_checker import FormattingChecker
from .checkers.readability_checker import ReadabilityChecker
from .checkers.experience_checker import ExperienceChecker
from .checkers.jd_alignment_checker import JDAlignmentChecker
from .checkers.impact_checker import ImpactChecker
from .ml_core.experience_parser import enhance_impact_score

class PerfectAnalysisEngine:
    """
    Modular analysis engine combining all checkers
    Implements the complete phased roadmap
    """
    
    def __init__(self):
        self.formatting_checker = FormattingChecker()
        self.readability_checker = ReadabilityChecker()
        self.experience_checker = ExperienceChecker()
        self.jd_checker = JDAlignmentChecker()
        self.impact_checker = ImpactChecker()
    
    def analyze(
        self,
        resume_file_path: str,
        resume_text: str,
        jd_text: Optional[str],
        parsed_data: Dict
    ) -> Dict:
        """
        Complete analysis using all checker modules
        
        Args:
            resume_file_path: Path to resume file (for layout analysis)
            resume_text: Extracted resume text
            jd_text: Job description text (optional)
            parsed_data: Structured data from NER extractor
                {
                    'skills': [...],
                    'work_history': [{title, company, start_date, end_date}, ...],
                    'experience_text': "...",
                    'contact_text': "...",
                    'experience_bullets': [...]
                }
        
        Returns:
            {
                'final_score': 85.5,
                'breakdown': {...},
                'feedback': [...],
                'grade': 'B'
            }
        """
        
        scores = {}
        all_feedback = []
        
        # Phase 1: Formatting & ATS-Compliance
        layout_score, layout_feedback = self.formatting_checker.check_file_layout(resume_file_path)
        scores['file_layout'] = layout_score
        all_feedback.extend(layout_feedback)
        
        font_score, font_feedback = self.formatting_checker.check_font_consistency(resume_file_path)
        scores['font_consistency'] = font_score
        all_feedback.extend(font_feedback)
        
        # Phase 2: Readability & Quality
        readability_score, readability_feedback = self.readability_checker.check_readability(resume_text)
        scores['readability'] = readability_score
        all_feedback.extend(readability_feedback)
        
        language_score, language_feedback = self.readability_checker.check_professional_language(
            resume_text,
            parsed_data.get('experience_bullets', [])
        )
        scores['professional_language'] = language_score
        all_feedback.extend(language_feedback)
        
        # Phase 3: Experience & Chronology
        date_score, date_feedback = self.experience_checker.check_date_consistency(
            parsed_data.get('work_history', [])
        )
        scores['date_consistency'] = date_score
        all_feedback.extend(date_feedback)
        
        gaps_score, gaps_feedback = self.experience_checker.check_employment_gaps(
            parsed_data.get('work_history', [])
        )
        scores['employment_gaps'] = gaps_score
        all_feedback.extend(gaps_feedback)
        
        progression_score, progression_feedback = self.experience_checker.check_career_progression(
            parsed_data.get('work_history', [])
        )
        scores['career_progression'] = progression_score
        all_feedback.extend(progression_feedback)
        
        # Phase 4: JD Alignment
        keyword_score, keyword_feedback, skill_details = self.jd_checker.check_keyword_alignment(
            resume_text,
            jd_text or ""
        )
        scores['keyword_alignment'] = keyword_score
        all_feedback.extend(keyword_feedback)
        
        context_score, context_feedback = self.jd_checker.check_skill_context(
            parsed_data.get('skills', []),
            parsed_data.get('experience_text', '')
        )
        scores['skill_context'] = context_score
        all_feedback.extend(context_feedback)
        
        semantic_score, semantic_feedback = self.jd_checker.check_semantic_fit(
            resume_text,
            jd_text or ""
        )
        scores['semantic_fit'] = semantic_score
        all_feedback.extend(semantic_feedback)
        
        # Phase 5: Impact & Advanced (Enhanced with ML parser)
        impact_score, impact_feedback = self.impact_checker.check_quantified_achievements(
            parsed_data.get('experience_text', '')
        )
        
        # Enhance with ML-based detection
        enhanced_scores = enhance_impact_score(
            parsed_data.get('experience_text', ''),
            parsed_data.get('work_history', [])
        )
        
        # Use max of rule-based and ML-based scores
        scores['quantified_impact'] = max(impact_score, enhanced_scores['quantified_impact'] / 10)  # Normalize to 0-10
        scores['career_progression'] = max(progression_score, enhanced_scores['career_progression'] / 20)  # Normalize to 0-5
        
        all_feedback.extend(impact_feedback)
        
        presence_score, presence_feedback = self.impact_checker.check_online_presence(
            parsed_data.get('contact_text', '')
        )
        scores['online_presence'] = presence_score
        all_feedback.extend(presence_feedback)
        
        # Calculate final score with weights
        final_score = self._calculate_weighted_score(scores)
        
        # Apply global mismatch penalty if semantic fit is critically low
        if jd_text and scores.get('semantic_fit', 0) < 4.0:  # <20% of 20 points
            # Critical mismatch - wrong role entirely (e.g., .NET dev vs BI analyst)
            final_score = min(final_score, 30.0)  # Cap at 30 (Grade F)
            all_feedback.insert(0, "⚠️ CRITICAL: Resume does not match job role requirements")
        elif jd_text and scores.get('semantic_fit', 0) < 7.0:  # <35% of 20 points
            # Significant mismatch
            final_score = min(final_score, 50.0)  # Cap at 50 (Grade F)
            all_feedback.insert(0, "⚠️ WARNING: Weak job-role alignment detected")
        
        grade = self._calculate_grade(final_score)
        
        return {
            'final_score': round(final_score, 1),
            'grade': grade,
            'breakdown': scores,
            'feedback': all_feedback,
            'total_checks': len(scores),
            'skill_match_details': skill_details if jd_text else {}
        }
    
    def _calculate_weighted_score(self, scores: Dict[str, float]) -> float:
        """
        Calculate weighted final score
        Normalize each score to 0-100 first, then apply weights
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
        
        weights = {
            'file_layout': 0.10,
            'font_consistency': 0.05,
            'readability': 0.05,
            'professional_language': 0.05,
            'date_consistency': 0.025,
            'employment_gaps': 0.05,
            'career_progression': 0.025,
            'keyword_alignment': 0.15,
            'skill_context': 0.05,
            'semantic_fit': 0.25,
            'quantified_impact': 0.15,
            'online_presence': 0.05
        }
        
        # Normalize to 0-100, then apply weights
        final_score = 0
        for key, raw_score in scores.items():
            max_val = max_points.get(key, 10)
            normalized = (raw_score / max_val) * 100
            final_score += normalized * weights.get(key, 0)
        
        return min(100, max(0, final_score))
    
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
