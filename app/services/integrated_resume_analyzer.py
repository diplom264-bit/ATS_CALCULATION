"""
Integrated Resume Analyzer
Combines parsing + analysis in single pipeline
"""
from typing import Dict
from .final_resume_parser import FinalResumeParser
from .data_adapter import DataAdapter
from .perfect_analysis_engine import PerfectAnalysisEngine

class IntegratedResumeAnalyzer:
    """Complete resume analysis pipeline"""
    
    def __init__(self):
        self.parser = FinalResumeParser()
        self.analyzer = PerfectAnalysisEngine()
    
    def analyze(self, resume_path: str, job_description: str = None) -> Dict:
        """
        Complete analysis: parse + analyze
        
        Returns:
            {
                'extraction': {...},  # Parsed entities
                'analysis': {...},    # Analysis results
                'status': 'ok'
            }
        """
        # Parse resume
        parsed = self.parser.parse(resume_path)
        
        if parsed['status'] != 'ok':
            return parsed
        
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
        
        # If JD provided, run analysis
        if job_description:
            # Get preprocessed data
            preprocessed = self.parser.preprocessor.process(resume_path)
            resume_text = preprocessed.get('clean_text', '')
            
            # Adapt data for analysis engine
            analysis_data = DataAdapter.adapt_ner_to_analysis(parsed, resume_text)
            
            # Run analysis
            analysis = self.analyzer.analyze(
                resume_file_path=resume_path,
                resume_text=resume_text,
                jd_text=job_description,
                parsed_data=analysis_data
            )
            result['analysis'] = analysis
        
        return result
