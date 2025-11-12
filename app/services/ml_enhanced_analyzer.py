"""
ML-Enhanced Resume Analyzer
Integrates embedding engine, feature fusion, and intelligent feedback
"""
from typing import Dict
from .final_resume_parser import FinalResumeParser
from .data_adapter import DataAdapter
from .perfect_analysis_engine import PerfectAnalysisEngine
from .ml_core.embedding_engine import EmbeddingEngine
from .ml_core.feature_fusion import FeatureFusion
from .ml_core.feedback_generator import FeedbackGenerator
from .ml_core.adaptive_scorer import AdaptiveScorer
from .ml_core.ml_scorer import get_ml_scorer

class MLEnhancedAnalyzer:
    """Production-ready analyzer with ML enhancements"""
    
    def __init__(self):
        self.parser = FinalResumeParser()
        self.analyzer = PerfectAnalysisEngine()
        self.embedding_engine = EmbeddingEngine()
        self.feature_fusion = FeatureFusion()
        self.feedback_gen = FeedbackGenerator()
        self.adaptive_scorer = AdaptiveScorer()
        self.ml_scorer = get_ml_scorer()  # Layer 5: ML scoring
    
    def analyze(self, resume_path: str, job_description: str = None) -> Dict:
        """
        Complete ML-enhanced analysis
        
        Returns:
            {
                'extraction': {...},
                'analysis': {...},
                'ml_features': {...},
                'semantic_score': float,
                'enhanced_feedback': [...],
                'status': 'ok'
            }
        """
        # Parse resume
        parsed = self.parser.parse(resume_path)
        if parsed['status'] != 'ok':
            return parsed
        
        # Get preprocessed data
        preprocessed = self.parser.preprocessor.process(resume_path)
        resume_text = preprocessed.get('clean_text', '')
        
        result = {
            'extraction': {
                'name': parsed['name'],
                'email': parsed['email'],
                'phone': parsed['phone'],
                'linkedin': parsed['linkedin'],
                'skills': parsed['skills'],
                'companies': parsed['companies'],
                'job_titles': parsed['job_titles'],
                'degrees': parsed['degrees'],
                'confidence': parsed.get('confidence', {})
            },
            'status': 'ok'
        }
        
        # ML Feature extraction
        analysis_data = DataAdapter.adapt_ner_to_analysis(parsed, resume_text)
        ml_features = self.feature_fusion.extract_all_features(
            resume_text, 
            analysis_data, 
            self.embedding_engine
        )
        result['ml_features'] = {
            'embedding_dim': ml_features['embedding_dim'],
            'rule_features_dim': ml_features['rule_dim'],
            'total_features': ml_features['total_dim']
        }
        
        # Run analysis if JD provided
        if job_description:
            # Traditional analysis
            raw_analysis = self.analyzer.analyze(
                resume_file_path=resume_path,
                resume_text=resume_text,
                jd_text=job_description,
                parsed_data=analysis_data
            )
            
            # Apply adaptive scoring
            enhanced_analysis = self.adaptive_scorer.enhance_analysis(
                raw_analysis,
                analysis_data
            )
            
            # Preserve skill_match_details from raw analysis
            if 'skill_match_details' in raw_analysis:
                enhanced_analysis['skill_match_details'] = raw_analysis['skill_match_details']
            
            # ML-enhanced semantic scoring (Layer 5)
            try:
                ml_score, ml_explanation = self.ml_scorer.ml_score(
                    resume_text,
                    job_description,
                    raw_analysis['breakdown']
                )
                result['ml_score'] = ml_score
                result['ml_explanation'] = ml_explanation
                
                # Fusion: 50% rule-based + 50% ML (balanced)
                rule_score = enhanced_analysis['final_score']
                fused_score = 0.5 * rule_score + 0.5 * ml_score
                
                # Prevent over-penalization from formatting issues
                formatting_penalty = max(0, (100 - raw_analysis['breakdown'].get('file_layout', 50)) / 10)
                fused_score = max(fused_score - min(0.1 * formatting_penalty, 10), 0)
                
                enhanced_analysis['final_score'] = round(fused_score, 1)
                enhanced_analysis['grade'] = self.adaptive_scorer._calculate_grade(fused_score)
            except Exception as e:
                import logging
                logging.warning(f"ML scoring failed, using rule-based only: {e}")
                result['ml_score'] = None
                result['ml_explanation'] = "ML scoring unavailable"
            
            # Fallback semantic scoring
            semantic_score = self.embedding_engine.compute_similarity(
                resume_text, 
                job_description
            )
            result['semantic_score'] = round(semantic_score * 100, 1)
            
            # Enhanced feedback generation
            enhanced_feedback = self.feedback_gen.generate_feedback(
                enhanced_analysis, 
                analysis_data, 
                job_description
            )
            summary = self.feedback_gen.generate_summary(
                enhanced_analysis['final_score'], 
                enhanced_analysis['grade']
            )
            
            result['analysis'] = enhanced_analysis
            result['enhanced_feedback'] = enhanced_feedback
            result['summary'] = summary
        
        return result
