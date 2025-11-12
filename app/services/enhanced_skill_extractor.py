"""Enhanced Skill Extractor - Better skill detection from resume text"""
import re
from typing import List, Set
import numpy as np

class EnhancedSkillExtractor:
    """Extract skills from resume text using embedding-based matching"""
    
    _embedding_model = None
    
    @classmethod
    def _get_model(cls):
        """Lazy load embedding model"""
        if cls._embedding_model is None:
            from sentence_transformers import SentenceTransformer
            cls._embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        return cls._embedding_model
    
    # Comprehensive skill database
    TECH_SKILLS = {
        # Programming Languages
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'php', 'go', 'rust', 'kotlin', 'swift',
        # Web Frameworks
        'django', 'flask', 'fastapi', 'react', 'angular', 'vue', 'next.js', 'node.js', 'express', 'spring',
        # Databases
        'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra', 'dynamodb', 'oracle', 'sqlite',
        # Cloud & DevOps
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform', 'ansible', 'ci/cd',
        # Data Science & ML
        'pandas', 'numpy', 'tensorflow', 'pytorch', 'scikit-learn', 'keras', 'opencv', 'nlp', 'ml', 'ai',
        # Tools & Others
        'git', 'github', 'gitlab', 'jira', 'confluence', 'selenium', 'celery', 'rabbitmq', 'kafka',
        'rest', 'api', 'graphql', 'microservices', 'agile', 'scrum', 'html', 'css', 'sass', 'bootstrap',
        # BI & Analytics
        'power bi', 'tableau', 'dax', 'power query', 'excel', 'sql server', 'ssrs', 'ssis',
        # Additional
        'linux', 'unix', 'bash', 'powershell', 'elasticsearch', 'nginx', 'apache', 'postman'
    }
    
    @classmethod
    def extract_skills(cls, text: str) -> List[str]:
        """Extract skills using embedding-based matching + direct search"""
        text_lower = text.lower()
        found_skills: Set[str] = set()
        
        # Strategy 1: Embedding-based fuzzy matching
        try:
            model = cls._get_model()
            
            # Extract all potential skill phrases (1-3 words)
            words = text.split()
            candidates = set()
            
            for i in range(len(words)):
                # Single words
                word = words[i].strip('.,;:()[]{}"\'')
                if len(word) > 2:
                    candidates.add(word.lower())
                
                # Two-word phrases
                if i < len(words) - 1:
                    phrase = f"{words[i]} {words[i+1]}".strip('.,;:()[]{}"\'')
                    candidates.add(phrase.lower())
                
                # Three-word phrases
                if i < len(words) - 2:
                    phrase = f"{words[i]} {words[i+1]} {words[i+2]}".strip('.,;:()[]{}"\'')
                    candidates.add(phrase.lower())
            
            # Encode candidates and known skills
            skill_list = list(cls.TECH_SKILLS)
            candidate_list = list(candidates)
            
            if candidate_list and skill_list:
                skill_embeddings = model.encode(skill_list, show_progress_bar=False)
                candidate_embeddings = model.encode(candidate_list, show_progress_bar=False)
                
                # Compute similarity
                from sklearn.metrics.pairwise import cosine_similarity
                similarities = cosine_similarity(candidate_embeddings, skill_embeddings)
                
                # Find matches with threshold
                for i, candidate in enumerate(candidate_list):
                    max_sim = similarities[i].max()
                    if max_sim > 0.75:  # High similarity threshold
                        best_match_idx = similarities[i].argmax()
                        found_skills.add(skill_list[best_match_idx].title())
        except:
            pass
        
        # Strategy 2: Direct exact match from skill database
        for skill in cls.TECH_SKILLS:
            if skill in text_lower:
                found_skills.add(skill.title())
        
        # Strategy 3: Extract from "Technical Skills" or "Technologies Used" sections
        skill_patterns = [
            r'technical skills[:\s-]+(.*?)(?:\n\n|languages:|\Z)',
            r'technolog(?:y|ies) used[:\s-]+(.*?)(?:\n\n|\Z)',
            r'skills[:\s-]+(.*?)(?:\n\n|languages:|education|\Z)'
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # Split by common delimiters
                items = re.split(r'[,;•\n]', match)
                for item in items:
                    item = item.strip()
                    if item and len(item) < 30:
                        # Add directly if reasonable length
                        if item and not item.endswith(':'):
                            found_skills.add(item.title())
                        # Also check against known skills
                        item_lower = item.lower()
                        for skill in EnhancedSkillExtractor.TECH_SKILLS:
                            if skill in item_lower:
                                found_skills.add(skill.title())
        
        # Strategy 3: Extract capitalized tech terms
        cap_pattern = r'\b([A-Z][a-z]+(?:\.[a-z]+)?)\b'
        cap_matches = re.findall(cap_pattern, text)
        for match in cap_matches:
            if match.lower() in EnhancedSkillExtractor.TECH_SKILLS:
                found_skills.add(match)
        
        # Strategy 4: Common patterns like "Python Developer", "Django framework"
        context_patterns = [
            r'(\w+)\s+(?:developer|engineer|framework|library|database|platform)',
            r'(?:using|with|in)\s+(\w+)',
            r'experience\s+(?:in|with)\s+(\w+)'
        ]
        for pattern in context_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if match in EnhancedSkillExtractor.TECH_SKILLS:
                    found_skills.add(match.title())
        
        # Remove duplicates and common words
        filtered = [s for s in found_skills if s.lower() not in ['used', 'technology', 'technologies', 'skills']]
        return sorted(list(filtered))
