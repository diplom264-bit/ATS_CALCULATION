"""
Layout-Aware Entity Extractor
Uses preprocessed document structure for accurate extraction
"""
import re
from typing import Dict, List, Tuple

class LayoutAwareExtractor:
    """Extract entities using layout information from preprocessing engine"""
    
    def __init__(self):
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
        self.linkedin_pattern = re.compile(r'linkedin\.com/in/[\w-]+')
        self.github_pattern = re.compile(r'github\.com/[\w-]+')
    
    def extract(self, preprocessed_data: Dict) -> Dict:
        """
        Extract entities from preprocessed document
        
        Args:
            preprocessed_data: Output from PreprocessingEngine
        
        Returns:
            Extracted entities
        """
        result = {
            "name": "",
            "email": "",
            "phone": "",
            "linkedin": "",
            "github": "",
            "skills": [],
            "degrees": [],
            "job_titles": [],
            "companies": [],
            "universities": [],
            "locations": []
        }
        
        if preprocessed_data.get('status') != 'ok':
            return result
        
        clean_text = preprocessed_data['clean_text']
        blocks = preprocessed_data.get('blocks', [])
        sections = preprocessed_data.get('sections', [])
        
        # Extract from header (first 3 blocks or first 300 chars)
        header_text = clean_text[:300]
        
        # PII extraction
        email_match = self.email_pattern.search(header_text)
        if email_match:
            result['email'] = email_match.group(0)
        
        phone_match = self.phone_pattern.search(header_text)
        if phone_match:
            result['phone'] = phone_match.group(0)
        
        linkedin_match = self.linkedin_pattern.search(header_text)
        if linkedin_match:
            result['linkedin'] = linkedin_match.group(0)
        
        github_match = self.github_pattern.search(header_text)
        if github_match:
            result['github'] = github_match.group(0)
        
        # Name extraction: first line with 2-3 capitalized words, no special chars
        header_lines = header_text.split('\n')
        for line in header_lines[:5]:
            line = line.strip()
            words = line.split()
            if 2 <= len(words) <= 3:
                # Check if looks like a name
                if all(w[0].isupper() and w.isalpha() for w in words):
                    # Not email, phone, or URL
                    if '@' not in line and 'http' not in line.lower() and '|' not in line:
                        result['name'] = line
                        break
        
        # Extract from sections
        for section in sections:
            section_name = section['name'].upper()
            section_text = section['text']
            
            if 'SKILL' in section_name:
                result['skills'] = self._extract_skills(section_text)
            
            elif 'EDUCATION' in section_name:
                result['degrees'] = self._extract_degrees(section_text)
            
            elif 'EXPERIENCE' in section_name or 'EMPLOYMENT' in section_name:
                companies, titles = self._extract_experience(section_text)
                result['companies'] = companies
                result['job_titles'] = titles
        
        return result
    
    def _extract_skills(self, skills_text: str) -> List[str]:
        """Extract skills from skills section"""
        skills = []
        
        # Split by common delimiters
        items = re.split(r'[,;•\n|]', skills_text)
        
        for item in items:
            item = item.strip()
            # Remove leading labels like "Tools:", "Languages:"
            item = re.sub(r'^[A-Za-z\s]+:\s*', '', item)
            # Remove leading symbols
            item = re.sub(r'^[:\-•\s]+', '', item)
            # Clean whitespace
            item = re.sub(r'\s+', ' ', item)
            
            if item and 2 < len(item) < 50:
                # Skip if it's a category label
                if not item.endswith(':') and not item.lower().startswith('other'):
                    skills.append(item)
        
        return skills[:20]
    
    def _extract_degrees(self, edu_text: str) -> List[str]:
        """Extract degrees from education section"""
        degree_pattern = r'(?:Bachelor|Master|PhD|Doctorate|B\.?S\.?|M\.?S\.?|MBA|B\.?Tech|M\.?Tech|PGDM|B\.?E\.?|M\.?E\.?|B\.?A\.?|M\.?A\.?)[^\n]*'
        degrees = re.findall(degree_pattern, edu_text, re.IGNORECASE)
        return [d.strip() for d in degrees][:5]
    
    def _extract_experience(self, exp_text: str) -> Tuple[List[str], List[str]]:
        """Extract companies and job titles from experience section"""
        companies = []
        titles = []
        
        lines = [l.strip() for l in exp_text.split('\n')]
        
        # Common single-word locations to skip
        locations = {'Delhi', 'Mumbai', 'Bangalore', 'Hyderabad', 'Chennai', 'Pune', 'Kolkata', 'Jaipur', 'India'}
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Skip empty lines and bullets
            if not line or line.startswith('•') or line.startswith('-'):
                i += 1
                continue
            
            # Skip if too long (likely description)
            if len(line) > 120:
                i += 1
                continue
            
            # Skip single-word locations
            if line in locations:
                i += 1
                continue
            
            # Check if line looks like a company
            # Company indicators: multiple capital words, no dates at start, not a single location
            has_caps = len(re.findall(r'\b[A-Z][a-z]+', line)) >= 2
            starts_with_date = bool(re.match(r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|20\d{2})', line))
            is_single_location = line.strip() in locations
            
            if has_caps and not starts_with_date and not is_single_location:
                # Check if next line has title keywords (strong indicator this is a company)
                has_title_in_next = False
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    has_title_in_next = bool(re.search(
                        r'\b(Developer|Engineer|Analyst|Manager|Consultant|Specialist|Architect|Designer|Intern|Lead|Senior|Junior)\b',
                        next_line, re.IGNORECASE
                    ))
                
                # Extract company name (remove trailing dates/locations)
                company = re.sub(r'\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).*$', '', line, flags=re.IGNORECASE)
                company = re.sub(r'\s+20\d{2}.*$', '', company)
                company = re.sub(r'\s+(Delhi|Mumbai|Bangalore|Hyderabad|Chennai|Pune|Kolkata|Jaipur|India).*$', '', company, flags=re.IGNORECASE)
                company = company.strip()
                
                # Only add if it looks like a real company (not just a location)
                if company and len(company) > 5 and (has_title_in_next or '(' in company or 'Ltd' in company or 'Inc' in company):
                    companies.append(company)
                    
                    # Look for title in next 2 lines
                    for j in range(i + 1, min(i + 3, len(lines))):
                        next_line = lines[j].strip()
                        
                        if not next_line or next_line.startswith('•'):
                            continue
                        
                        # Title indicators: job keywords
                        has_title_keyword = bool(re.search(
                            r'\b(Developer|Engineer|Analyst|Manager|Consultant|Specialist|Architect|Designer|Intern|Lead|Senior|Junior)\b',
                            next_line, re.IGNORECASE
                        ))
                        
                        if has_title_keyword:
                            # Clean title (remove dates/locations at end)
                            title = re.sub(r'\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).*$', '', next_line, flags=re.IGNORECASE)
                            title = re.sub(r'\s+20\d{2}.*$', '', title)
                            title = re.sub(r'\s+(Delhi|Mumbai|Bangalore|Jaipur|India).*$', '', title, flags=re.IGNORECASE)
                            title = title.strip()
                            
                            if title and len(title) > 3:
                                titles.append(title)
                            break
            
            i += 1
        
        return companies[:5], titles[:5]
