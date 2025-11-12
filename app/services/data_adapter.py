"""
Data Adapter
Converts ProductionNERExtractor output to PerfectAnalysisEngine format
"""
from typing import Dict, List

class DataAdapter:
    """Adapts NER extractor output for analysis engine"""
    
    @staticmethod
    def adapt_ner_to_analysis(entities: Dict, resume_text: str) -> Dict:
        """
        Convert NER extractor output to analysis engine format
        
        Args:
            entities: Output from ProductionNERExtractor
            resume_text: Full resume text
        
        Returns:
            Structured data for PerfectAnalysisEngine
        """
        
        # Build work history from extracted data
        work_history = []
        if entities.get('companies') and entities.get('job_titles'):
            for i, company in enumerate(entities['companies']):
                work_history.append({
                    'company': company,
                    'title': entities['job_titles'][i] if i < len(entities['job_titles']) else '',
                    'start_date': '',  # TODO: Extract dates
                    'end_date': ''
                })
        
        # Extract experience section text
        experience_text = DataAdapter._extract_section(resume_text, 'EXPERIENCE')
        
        # Extract experience bullets
        experience_bullets = []
        if experience_text:
            lines = experience_text.split('\n')
            experience_bullets = [
                line.strip() for line in lines 
                if line.strip() and (line.strip().startswith('•') or line.strip().startswith('-'))
            ]
        
        # Extract contact section
        contact_text = resume_text[:300]  # Header typically in first 300 chars
        
        return {
            'skills': entities.get('skills', []),
            'work_history': work_history,
            'experience_text': experience_text,
            'contact_text': contact_text,
            'experience_bullets': experience_bullets,
            'name': entities.get('name', ''),
            'email': entities.get('email', ''),
            'phone': entities.get('phone', ''),
            'linkedin': entities.get('linkedin', '')
        }
    
    @staticmethod
    def _extract_section(text: str, section_name: str) -> str:
        """Extract specific section from resume text"""
        import re
        
        # Try multiple patterns
        patterns = [
            rf'(?i)(?:^|\n)({section_name}[:\s]*\n)(.*?)(?=\n[A-Z]{{3,}}|\Z)',
            rf'(?i)({section_name}.*?\n)(.*?)(?=\n(?:[A-Z][A-Z]+|EDUCATION|SKILLS|PROJECTS)|\Z)',
            rf'(?i)(WORK {section_name}|PROFESSIONAL {section_name})(.*?)(?=\n[A-Z]{{3,}}|\Z)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                section_text = match.group(2).strip()
                if len(section_text) > 50:  # Valid section should have content
                    return section_text
        
        # Fallback: if no section found, use full text (better than empty)
        return text
