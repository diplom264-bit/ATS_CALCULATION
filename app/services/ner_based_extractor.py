"""
NER-Based Extractor
Uses spaCy NER as foundation, then aggregates with rules
"""
import re
import spacy
from typing import Dict, List, Tuple
from collections import Counter

class NERBasedExtractor:
    """
    Extract entities using:
    1. spaCy NER for PERSON, ORG, GPE, DATE
    2. Regex for PII (email, phone, links)
    3. Section-aware aggregation
    4. Confidence scoring
    """
    
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("⚠️ spaCy model not found. Run: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Regex patterns
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
        self.linkedin_pattern = re.compile(r'linkedin\.com/in/[\w-]+')
        self.github_pattern = re.compile(r'github\.com/[\w-]+')
        
        # Job title keywords
        self.job_keywords = [
            'developer', 'engineer', 'analyst', 'manager', 'consultant',
            'specialist', 'architect', 'designer', 'intern', 'lead',
            'senior', 'junior', 'principal'
        ]
    
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
            "locations": []
        }
        
        if preprocessed_data.get('status') != 'ok':
            return result
        
        clean_text = preprocessed_data['clean_text']
        sections = preprocessed_data.get('sections', [])
        
        # Extract PII from header (first 500 chars)
        header_text = clean_text[:500]
        
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
        
        if not self.nlp:
            return result
        
        # Run NER on full text
        doc = self.nlp(clean_text[:10000])  # Limit to 10k chars for performance
        
        # Extract entities by type
        persons = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']
        orgs = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
        gpes = [ent.text for ent in doc.ents if ent.label_ == 'GPE']
        
        # Name: Most common PERSON in header, or first PERSON
        header_doc = self.nlp(header_text)
        header_persons = [ent.text for ent in header_doc.ents if ent.label_ == 'PERSON']
        if header_persons:
            result['name'] = header_persons[0]
        elif persons:
            # Use most common person name
            person_counts = Counter(persons)
            result['name'] = person_counts.most_common(1)[0][0]
        
        # Locations: GPE entities
        result['locations'] = list(set(gpes))[:5]
        
        # Process sections
        for section in sections:
            section_name = section['name'].upper()
            section_text = section['text']
            
            if 'SKILL' in section_name:
                result['skills'] = self._extract_skills(section_text)
            
            elif 'EDUCATION' in section_name:
                result['degrees'] = self._extract_degrees(section_text)
                # Extract universities from ORG entities in education section
                edu_doc = self.nlp(section_text[:2000])
                edu_orgs = [ent.text for ent in edu_doc.ents if ent.label_ == 'ORG']
                result['universities'] = edu_orgs[:3]
            
            elif 'EXPERIENCE' in section_name:
                # Use NER to find ORG entities (companies)
                exp_doc = self.nlp(section_text[:5000])
                exp_orgs = [ent.text for ent in exp_doc.ents if ent.label_ == 'ORG']
                
                # Filter and clean companies
                companies, titles = self._extract_experience_with_ner(
                    section_text, exp_orgs
                )
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
            # Remove category labels
            item = re.sub(r'^[A-Za-z\s]+:\s*', '', item)
            item = re.sub(r'^[:\-•\s]+', '', item)
            item = re.sub(r'\s+', ' ', item)
            
            if item and 2 < len(item) < 50:
                if not item.endswith(':') and item.lower() not in ['other', 'tools', 'languages']:
                    skills.append(item)
        
        # Deduplicate
        seen = set()
        unique_skills = []
        for skill in skills:
            if skill.lower() not in seen:
                seen.add(skill.lower())
                unique_skills.append(skill)
        
        return unique_skills[:20]
    
    def _extract_degrees(self, edu_text: str) -> List[str]:
        """Extract degrees from education section"""
        degree_pattern = r'(?:Bachelor|Master|PhD|Doctorate|B\.?S\.?|M\.?S\.?|MBA|B\.?Tech|M\.?Tech|PGDM|B\.?E\.?|M\.?E\.?)[^\n]*'
        degrees = re.findall(degree_pattern, edu_text, re.IGNORECASE)
        
        # Clean and deduplicate
        cleaned = []
        for deg in degrees:
            deg = deg.strip()
            if deg and len(deg) < 150:
                cleaned.append(deg)
        
        return list(set(cleaned))[:5]
    
    def _extract_experience_with_ner(self, exp_text: str, org_entities: List[str]) -> Tuple[List[str], List[str]]:
        """Extract companies and titles using NER + rules"""
        companies = []
        titles = []
        
        lines = [l.strip() for l in exp_text.split('\n') if l.strip()]
        
        # Filter ORG entities to get real companies
        for org in org_entities:
            # Skip if too short or common words
            if len(org) < 3:
                continue
            
            # Skip if it's a skill/tool name
            if org.lower() in ['power bi', 'sql', 'excel', 'python', 'java']:
                continue
            
            # Add to companies
            if org not in companies:
                companies.append(org)
        
        # Extract job titles using keywords
        for line in lines:
            # Skip bullets
            if line.startswith('•') or line.startswith('-'):
                continue
            
            # Skip if too long
            if len(line) > 100:
                continue
            
            # Check if line contains job keywords
            has_job_keyword = any(kw in line.lower() for kw in self.job_keywords)
            
            if has_job_keyword:
                # Clean the title
                title = line
                
                # Remove dates
                title = re.sub(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b.*$', '', title, flags=re.IGNORECASE)
                title = re.sub(r'\b20\d{2}\b.*$', '', title)
                
                # Remove locations
                title = re.sub(r'\b(Delhi|Mumbai|Bangalore|Hyderabad|Chennai|Pune|Jaipur|India)\b.*$', '', title, flags=re.IGNORECASE)
                
                # Clean whitespace
                title = re.sub(r'\s+', ' ', title).strip()
                
                if title and len(title) > 3 and title not in titles:
                    titles.append(title)
        
        return companies[:5], titles[:5]
