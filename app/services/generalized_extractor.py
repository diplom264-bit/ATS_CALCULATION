"""
Generalized Resume Extractor
Works on any resume format using multi-strategy approach
"""
import re
from typing import Dict, List, Tuple
from difflib import SequenceMatcher

class GeneralizedExtractor:
    """
    Generalized extractor using:
    1. Multi-strategy section detection
    2. Layout-aware entity extraction
    3. Context-based association
    4. Confidence scoring
    """
    
    def __init__(self):
        # Common section names (for fuzzy matching)
        self.section_patterns = {
            'SUMMARY': ['summary', 'profile', 'objective', 'about'],
            'EXPERIENCE': ['experience', 'work history', 'employment', 'work experience', 'professional experience'],
            'EDUCATION': ['education', 'academic', 'qualification'],
            'SKILLS': ['skills', 'technical skills', 'competencies', 'expertise', 'core competencies'],
            'PROJECTS': ['projects', 'key projects'],
            'CERTIFICATIONS': ['certifications', 'certificates', 'awards'],
        }
        
        # Job title keywords (for context)
        self.job_keywords = [
            'developer', 'engineer', 'analyst', 'manager', 'consultant',
            'specialist', 'architect', 'designer', 'intern', 'lead',
            'senior', 'junior', 'principal', 'staff', 'associate'
        ]
        
        # Common locations (to filter out)
        self.common_locations = {
            'delhi', 'mumbai', 'bangalore', 'hyderabad', 'chennai',
            'pune', 'kolkata', 'jaipur', 'india', 'usa', 'uk'
        }
        
        # Regex patterns
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
        self.linkedin_pattern = re.compile(r'linkedin\.com/in/[\w-]+')
        self.github_pattern = re.compile(r'github\.com/[\w-]+')
        self.date_pattern = re.compile(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|20\d{2})\b', re.IGNORECASE)
    
    def extract(self, preprocessed_data: Dict) -> Dict:
        """Extract entities from preprocessed document"""
        
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
            "locations": [],
            "confidence": {}
        }
        
        if preprocessed_data.get('status') != 'ok':
            return result
        
        clean_text = preprocessed_data['clean_text']
        blocks = preprocessed_data.get('blocks', [])
        
        # Extract header info (first 500 chars)
        header_text = clean_text[:500]
        
        # PII extraction (high confidence)
        email_match = self.email_pattern.search(header_text)
        if email_match:
            result['email'] = email_match.group(0)
            result['confidence']['email'] = 1.0
        
        phone_match = self.phone_pattern.search(header_text)
        if phone_match:
            result['phone'] = phone_match.group(0)
            result['confidence']['phone'] = 0.95
        
        linkedin_match = self.linkedin_pattern.search(header_text)
        if linkedin_match:
            result['linkedin'] = linkedin_match.group(0)
            result['confidence']['linkedin'] = 1.0
        
        github_match = self.github_pattern.search(header_text)
        if github_match:
            result['github'] = github_match.group(0)
            result['confidence']['github'] = 1.0
        
        # Name extraction (multi-strategy)
        result['name'], name_conf = self._extract_name(header_text, blocks)
        result['confidence']['name'] = name_conf
        
        # Detect sections with confidence
        sections = self._detect_sections_fuzzy(clean_text, blocks)
        
        # Extract from sections
        for section_type, section_data in sections.items():
            if section_type == 'SKILLS':
                result['skills'] = self._extract_skills(section_data['text'])
                result['confidence']['skills'] = section_data['confidence']
            
            elif section_type == 'EDUCATION':
                result['degrees'] = self._extract_degrees(section_data['text'])
                result['confidence']['education'] = section_data['confidence']
            
            elif section_type == 'EXPERIENCE':
                companies, titles, exp_conf = self._extract_experience_generalized(section_data['text'])
                result['companies'] = companies
                result['job_titles'] = titles
                result['confidence']['experience'] = exp_conf
        
        return result
    
    def _extract_name(self, header_text: str, blocks: List[Dict]) -> Tuple[str, float]:
        """Extract name using multiple strategies"""
        candidates = []
        
        # Strategy 1: Largest font in header
        if blocks:
            header_blocks = [b for b in blocks[:5] if b['y0'] < 150]
            if header_blocks:
                largest = max(header_blocks, key=lambda b: b['font_size'])
                text = largest['text'].strip()
                words = text.split()
                if 2 <= len(words) <= 3 and all(w[0].isupper() and w.isalpha() for w in words):
                    candidates.append((text, 0.9))
        
        # Strategy 2: First line with 2-3 capitalized words
        lines = header_text.split('\n')
        for line in lines[:5]:
            line = line.strip()
            words = line.split()
            if 2 <= len(words) <= 3:
                if all(w[0].isupper() and w.isalpha() for w in words):
                    if '@' not in line and '|' not in line:
                        candidates.append((line, 0.8))
                        break
        
        # Return best candidate
        if candidates:
            return max(candidates, key=lambda x: x[1])
        return "", 0.0
    
    def _detect_sections_fuzzy(self, text: str, blocks: List[Dict]) -> Dict:
        """Detect sections using fuzzy matching and multiple signals"""
        sections = {}
        lines = text.split('\n')
        
        # Calculate average font size for comparison
        avg_font_size = sum(b['font_size'] for b in blocks) / len(blocks) if blocks else 11
        
        for i, line in enumerate(lines):
            line_clean = line.strip()
            if not line_clean or len(line_clean) > 80:
                continue
            
            # Check if this line matches any section pattern
            best_match = None
            best_score = 0.0
            
            for section_type, patterns in self.section_patterns.items():
                for pattern in patterns:
                    # Fuzzy match
                    similarity = SequenceMatcher(None, line_clean.lower(), pattern.lower()).ratio()
                    if similarity > 0.7 and similarity > best_score:
                        best_match = section_type
                        best_score = similarity
            
            if best_match:
                # Found a section header - extract content
                # Find next section
                section_end = len(lines)
                for j in range(i + 1, len(lines)):
                    next_line = lines[j].strip()
                    if len(next_line) < 80:
                        # Check if this is another section
                        for patterns in self.section_patterns.values():
                            for pattern in patterns:
                                if SequenceMatcher(None, next_line.lower(), pattern.lower()).ratio() > 0.7:
                                    section_end = j
                                    break
                            if section_end != len(lines):
                                break
                    if section_end != len(lines):
                        break
                
                section_text = '\n'.join(lines[i+1:section_end])
                
                # Calculate confidence based on multiple signals
                confidence = best_score  # Base: fuzzy match score
                
                # Boost if line is short (likely a header)
                if len(line_clean) < 30:
                    confidence = min(1.0, confidence + 0.1)
                
                # Boost if all caps or title case
                if line_clean.isupper() or line_clean.istitle():
                    confidence = min(1.0, confidence + 0.1)
                
                sections[best_match] = {
                    'text': section_text.strip(),
                    'confidence': confidence
                }
        
        return sections
    
    def _extract_skills(self, skills_text: str) -> List[str]:
        """Extract skills with flexible parsing"""
        skills = []
        
        # Split by multiple delimiters
        items = re.split(r'[,;•\n|]', skills_text)
        
        for item in items:
            item = item.strip()
            
            # Remove category labels
            item = re.sub(r'^[A-Za-z\s]+:\s*', '', item)
            item = re.sub(r'^[:\-•\s]+', '', item)
            item = re.sub(r'\s+', ' ', item)
            
            # Filter
            if item and 2 < len(item) < 50:
                # Skip if ends with colon (category label)
                if not item.endswith(':'):
                    # Skip common words
                    if item.lower() not in ['other', 'tools', 'languages', 'skills']:
                        skills.append(item)
        
        # Deduplicate while preserving order
        seen = set()
        unique_skills = []
        for skill in skills:
            skill_lower = skill.lower()
            if skill_lower not in seen:
                seen.add(skill_lower)
                unique_skills.append(skill)
        
        return unique_skills[:20]
    
    def _extract_degrees(self, edu_text: str) -> List[str]:
        """Extract degrees with flexible patterns"""
        degree_patterns = [
            r'(?:Bachelor|Master|PhD|Doctorate)[\w\s]*',
            r'B\.?[A-Z]\.?[\w\s]*',
            r'M\.?[A-Z]\.?[\w\s]*',
            r'(?:MBA|PGDM|BBA)[\w\s]*'
        ]
        
        degrees = []
        for pattern in degree_patterns:
            matches = re.findall(pattern, edu_text, re.IGNORECASE)
            for match in matches:
                # Extract full degree line
                lines = edu_text.split('\n')
                for line in lines:
                    if match.lower() in line.lower():
                        degree = line.strip()
                        if degree and len(degree) < 150:
                            degrees.append(degree)
                        break
        
        return list(set(degrees))[:5]
    
    def _extract_experience_generalized(self, exp_text: str) -> Tuple[List[str], List[str], float]:
        """Extract experience using block detection and context"""
        companies = []
        titles = []
        
        lines = [l.strip() for l in exp_text.split('\n') if l.strip()]
        
        # Detect experience blocks (groups of related lines)
        blocks = self._detect_experience_blocks(lines)
        
        for block in blocks:
            # Within each block, identify company and title
            company, title = self._extract_from_experience_block(block)
            if company:
                companies.append(company)
            if title:
                titles.append(title)
        
        confidence = 0.8 if companies else 0.0
        return companies[:5], titles[:5], confidence
    
    def _detect_experience_blocks(self, lines: List[str]) -> List[List[str]]:
        """Group lines into experience blocks"""
        blocks = []
        current_block = []
        
        for line in lines:
            # Start new block if line looks like a company/title
            if self._is_block_start(line):
                if current_block:
                    blocks.append(current_block)
                current_block = [line]
            elif line.startswith('•') or line.startswith('-'):
                # Bullet point - part of current block
                current_block.append(line)
            elif len(line) < 100 and current_block:
                # Short line after block start - might be title/date
                current_block.append(line)
            elif not current_block:
                # First line
                current_block.append(line)
        
        if current_block:
            blocks.append(current_block)
        
        return blocks
    
    def _is_block_start(self, line: str) -> bool:
        """Check if line starts a new experience block"""
        # Has multiple capital words
        cap_words = len(re.findall(r'\b[A-Z][a-z]+', line))
        
        # Not a bullet point
        not_bullet = not line.startswith('•') and not line.startswith('-')
        
        # Not too long
        reasonable_length = len(line) < 100
        
        return cap_words >= 2 and not_bullet and reasonable_length
    
    def _extract_from_experience_block(self, block: List[str]) -> Tuple[str, str]:
        """Extract company and title from experience block"""
        company = ""
        title = ""
        
        # First non-bullet line is likely company or title
        non_bullet_lines = [l for l in block if not l.startswith('•') and not l.startswith('-')]
        
        if not non_bullet_lines:
            return company, title
        
        # Analyze first 2-3 lines
        for i, line in enumerate(non_bullet_lines[:3]):
            has_job_keyword = any(kw in line.lower() for kw in self.job_keywords)
            has_date = bool(self.date_pattern.search(line))
            has_location = any(loc in line.lower() for loc in self.common_locations)
            cap_words = len(re.findall(r'\b[A-Z][a-z]+', line))
            
            # Title: has job keyword
            if has_job_keyword and not title:
                # Clean: remove dates and locations
                title = self.date_pattern.sub('', line)
                for loc in self.common_locations:
                    title = re.sub(rf'\b{loc}\b', '', title, flags=re.IGNORECASE)
                title = re.sub(r'\s+', ' ', title).strip()
            
            # Company: multiple capital words, no job keyword
            elif cap_words >= 2 and not has_job_keyword and not company:
                # Clean: remove dates and locations
                company = self.date_pattern.sub('', line)
                for loc in self.common_locations:
                    company = re.sub(rf'\b{loc}\b', '', company, flags=re.IGNORECASE)
                company = re.sub(r'\s+', ' ', company).strip()
        
        return company, title
