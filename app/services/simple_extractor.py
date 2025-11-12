"""
Simple Rule-Based Extractor
Minimal, reliable extraction using regex and layout patterns
"""
import re
from typing import Dict, List, Tuple

class SimpleExtractor:
    """Minimal rule-based extractor - no ML dependencies"""
    
    def __init__(self):
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
        self.linkedin_pattern = re.compile(r'linkedin\.com/in/[\w-]+')
    
    def extract(self, text: str) -> Dict:
        """Extract entities from resume text"""
        
        result = {
            "name": "",
            "email": "",
            "phone": "",
            "linkedin": "",
            "skills": [],
            "degrees": [],
            "job_titles": [],
            "companies": [],
            "universities": [],
            "locations": []
        }
        
        lines = text.split('\n')
        
        # Extract PII from first 10 lines
        header = '\n'.join(lines[:10])
        
        email_match = self.email_pattern.search(header)
        if email_match:
            result['email'] = email_match.group(0)
        
        phone_match = self.phone_pattern.search(header)
        if phone_match:
            result['phone'] = phone_match.group(0)
        
        linkedin_match = self.linkedin_pattern.search(header)
        if linkedin_match:
            result['linkedin'] = linkedin_match.group(0)
        
        # Name: First line with 2-3 capital words
        for line in lines[:5]:
            line = line.strip()
            words = line.split()
            if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w):
                result['name'] = line
                break
        
        # Find sections
        sections = self._find_sections(text)
        
        # Extract skills
        if 'SKILLS' in sections:
            result['skills'] = self._extract_skills(sections['SKILLS'])
        
        # Extract education
        if 'EDUCATION' in sections:
            result['degrees'] = self._extract_degrees(sections['EDUCATION'])
        
        # Extract experience
        if 'EXPERIENCE' in sections:
            companies, titles = self._extract_experience(sections['EXPERIENCE'])
            result['companies'] = companies
            result['job_titles'] = titles
        
        return result
    
    def _find_sections(self, text: str) -> Dict[str, str]:
        """Find major sections in resume"""
        sections = {}
        
        patterns = {
            'SKILLS': r'(?i)(?:^|\n)((?:TECHNICAL\s*)?SKILLS?)[:\s]*\n',
            'EXPERIENCE': r'(?i)(?:^|\n)((?:WORK\s*)?EXPERIENCE|EMPLOYMENT)[:\s]*\n',
            'EDUCATION': r'(?i)(?:^|\n)(EDUCATION|ACADEMIC)[:\s]*\n'
        }
        
        for name, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                start = match.end()
                # Find next section
                next_section = re.search(r'\n[A-Z][A-Za-z\s]{3,}[:\s]*\n', text[start:])
                end = start + next_section.start() if next_section else len(text)
                sections[name] = text[start:end].strip()
        
        return sections
    
    def _extract_skills(self, skills_text: str) -> List[str]:
        """Extract skills from skills section"""
        skills = []
        
        # Split by common delimiters
        items = re.split(r'[,;•\n|]', skills_text)
        
        for item in items:
            item = item.strip()
            # Remove leading symbols
            item = re.sub(r'^[:\-•\s]+', '', item)
            # Clean whitespace
            item = re.sub(r'\s+', ' ', item)
            
            if item and 2 < len(item) < 50:
                skills.append(item)
        
        return skills[:20]
    
    def _extract_degrees(self, edu_text: str) -> List[str]:
        """Extract degrees from education section"""
        degree_pattern = r'(?:Bachelor|Master|PhD|B\.?S\.?|M\.?S\.?|MBA|B\.?Tech|M\.?Tech|PGDM|B\.?E\.?|M\.?E\.?)[^\n]*'
        degrees = re.findall(degree_pattern, edu_text, re.IGNORECASE)
        return [d.strip() for d in degrees][:5]
    
    def _extract_experience(self, exp_text: str) -> Tuple[List[str], List[str]]:
        """Extract companies and job titles from experience section"""
        companies = []
        titles = []
        
        lines = [l.strip() for l in exp_text.split('\n')]
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Skip empty lines and bullets
            if not line or line.startswith('•') or line.startswith('-'):
                i += 1
                continue
            
            # Skip if too long (likely description)
            if len(line) > 100:
                i += 1
                continue
            
            # Check if line looks like a company (has capital words, no dates)
            has_caps = len(re.findall(r'\b[A-Z][a-z]+', line)) >= 2
            has_date = bool(re.search(r'\b(20\d{2}|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b', line))
            
            if has_caps and not has_date:
                # This might be a company
                companies.append(line)
                
                # Next line might be title
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not next_line.startswith('•') and len(next_line) < 80:
                        # Check if it has title keywords or dates
                        has_title_keyword = bool(re.search(
                            r'\b(Developer|Engineer|Analyst|Manager|Consultant|Specialist|Architect|Designer|Intern)\b',
                            next_line, re.IGNORECASE
                        ))
                        if has_title_keyword or has_date:
                            titles.append(next_line)
                            i += 1  # Skip next line since we processed it
            
            i += 1
        
        return companies[:5], titles[:5]
