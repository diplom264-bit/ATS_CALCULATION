"""
Phase 4: JD Alignment Module
Keyword matching, skill context, semantic job-fit with KB enhancement
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import torch
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# KB path - from checkers -> services -> app -> version_4 -> ATSsys -> knowledge_base
kb_path = Path(__file__).parent.parent.parent.parent.parent / "knowledge_base"

class JDAlignmentChecker:
    """Job description alignment analysis with KB enhancement"""
    
    def __init__(self, use_kb: bool = True):
        # Use KB singleton
        self.use_kb = use_kb
        if use_kb:
            from app.services.kb_singleton import get_kb_instance
            self.kb = get_kb_instance()
        else:
            self.kb = None
        
        # Fallback: Load S-BERT directly
        if not self.kb:
            from sentence_transformers import SentenceTransformer
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2', device=device)
        else:
            self.semantic_model = self.kb.model
    
    def check_keyword_alignment(self, resume_text: str, jd_text: str) -> Tuple[float, List[str], Dict]:
        """Check 9: Keyword Alignment (15 points)"""
        score = 0.0
        feedback = []
        skill_details = {'matched': [], 'missing': [], 'matched_technical': [], 'matched_soft': [], 'missing_technical': [], 'missing_soft': []}
        
        if not jd_text or not resume_text:
            return 15.0, [], skill_details
        
        try:
            # Extract actual technical terms using TF-IDF (bypass KB's generic descriptions)
            vectorizer = TfidfVectorizer(
                stop_words='english',
                max_features=100,
                ngram_range=(1, 3),
                token_pattern=r'\b[A-Za-z][A-Za-z0-9+#.\-/]*\b',
                min_df=1
            )
            tfidf_matrix = vectorizer.fit_transform([jd_text, resume_text])
            feature_names = vectorizer.get_feature_names_out()
            
            jd_vector = tfidf_matrix[0].toarray()[0]
            jd_terms = [feature_names[i] for i in jd_vector.argsort()[-100:][::-1] if jd_vector[i] > 0]
            
            resume_lower = resume_text.lower()
            matched = [t for t in jd_terms if t.lower() in resume_lower]
            missing = [t for t in jd_terms if t.lower() not in resume_lower]
                
                # Filter out generic ESCO descriptions (keep only tech terms)
            # Filter terms
            GENERIC = {'using', 'experience', 'knowledge', 'ability', 'working', 'understanding', 'strong', 'good', 'excellent', 'proficient', 'familiar', 'expertise', 'background', 'years', 'work', 'team', 'teams', 'business', 'performance', 'support', 'applications', 'services', 'quality', 'technical', 'skills', 'required', 'preferred', 'must', 'should', 'will', 'can', 'able', 'including', 'related', 'relevant', 'various', 'multiple', 'several', 'different', 'new', 'current', 'existing', 'future', 'based', 'driven', 'focused', 'oriented', 'data', 'tools', 'technologies', 'systems', 'solutions', 'processes', 'projects', 'development', 'design', 'implementation', 'integration', 'testing', 'deployment', 'maintenance', 'documentation', 'requirements', 'analysis', 'reporting', 'monitoring'}
            SOFT_SKILLS = {'leadership', 'communication', 'teamwork', 'collaboration', 'mentoring', 'management', 'planning', 'organization', 'problem solving', 'critical thinking', 'adaptability', 'creativity', 'presentation', 'negotiation', 'decision making', 'strategic thinking', 'analytical thinking', 'interpersonal', 'emotional intelligence'}
            
            def is_soft_skill(term):
                return any(soft in term.lower() for soft in SOFT_SKILLS)
            
            def is_valid_tech(term):
                if len(term) < 2 or term.lower() in GENERIC or is_soft_skill(term):
                    return False
                # Keep if contains tech indicators or is capitalized tech term
                tech_patterns = {'sql', 'python', 'java', 'javascript', 'react', 'angular', 'node', 'aws', 'azure', 'docker', 'kubernetes', 'api', 'server', 'cloud', '.net', 'c#', 'typescript', 'html', 'css', 'rest', 'graphql', 'mongodb', 'postgresql', 'redis', 'kafka', 'spark', 'hadoop', 'tableau', 'power bi', 'powerbi', 'excel', 'git', 'jenkins', 'terraform', 'ansible', 'framework', 'library', 'devops', 'ml', 'ai', 'etl', 'warehouse', 'pipeline', 'mvc', 'orm', 'wcf', 'nunit', 'entity', 'linq', 'razor', 'blazor', 'xamarin', 'ssas', 'ssis', 'ssrs', 'olap', 'oltp', 'dax', 'mdx', 'cube', 'qlikview', 'looker', 'microstrategy', 'cognos', 'sap', 'oracle', 'mysql', 'nosql', 'snowflake', 'redshift', 'bigquery', 'databricks', 'airflow', 'talend', 'informatica', 'pentaho', 'alteryx', 'knime', 'rapidminer', 'spss', 'sas', 'stata', 'matlab', 'scala', 'golang', 'ruby', 'php', 'swift', 'kotlin', 'rust', 'vue', 'svelte', 'django', 'flask', 'spring', 'express', 'fastapi', 'graphql', 'grpc', 'rabbitmq', 'elasticsearch', 'solr', 'neo4j', 'cassandra', 'dynamodb', 'firebase', 'supabase', 'vercel', 'netlify', 'heroku', 'digitalocean', 'gcp', 'ibm', 'salesforce', 'servicenow', 'jira', 'confluence', 'slack', 'teams', 'zoom', 'webex', 'miro', 'figma', 'sketch', 'adobe', 'photoshop', 'illustrator', 'xd', 'invision', 'zeplin', 'abstract', 'framer', 'principle', 'origami', 'flinto', 'proto', 'marvel', 'balsamiq', 'axure', 'justinmind', 'mockplus', 'uxpin', 'craft', 'avocode', 'sympli', 'measure'}
                return any(pat in term.lower() for pat in tech_patterns) or (term[0].isupper() and len(term) > 2 and not term.lower() in {'the', 'and', 'for', 'with', 'from', 'this', 'that', 'have', 'has', 'had', 'will', 'would', 'could', 'should'})
            
            matched_tech = [t for t in matched if is_valid_tech(t)][:15]
            matched_soft = [t for t in matched if is_soft_skill(t)][:10]
            missing_tech = [t for t in missing if is_valid_tech(t)][:10]
            missing_soft = [t for t in missing if is_soft_skill(t)][:5]
            
            skill_details = {
                'matched': matched[:15],
                'missing': missing[:10],
                'matched_technical': matched_tech,
                'matched_soft': matched_soft,
                'missing_technical': missing_tech,
                'missing_soft': missing_soft
            }
            
            match_rate = len(matched) / len(jd_terms) if jd_terms else 0
            total_tech = len(matched_tech) + len(missing_tech)
            tech_match_rate = len(matched_tech) / total_tech if total_tech > 0 else 1.0
            
            # Strict penalty for role mismatch
            if total_tech >= 3 and tech_match_rate < 0.4:
                score = match_rate * 15 * 0.2  # Severe penalty - wrong role
                feedback.append(f"CRITICAL MISMATCH: Only {len(matched_tech)}/{total_tech} technical skills matched")
            elif total_tech >= 3 and tech_match_rate < 0.6:
                score = match_rate * 15 * 0.4  # Heavy penalty
                feedback.append(f"Major gap: Missing {len(missing_tech)} key technical skills")
            elif tech_match_rate < 0.8:
                score = match_rate * 15 * 0.7  # Moderate penalty
                feedback.append(f"Missing {len(missing_tech)} technical skills")
            else:
                score = match_rate * 15
                if match_rate >= 0.8:
                    feedback.append(f"Excellent match: {len(matched_tech)} technical skills")
        except Exception as e:
            import logging
            logging.error(f"Keyword alignment error: {e}")
            score = 7.5
        
        return score, feedback, skill_details
    
    def check_skill_context(self, skills: List[str], experience_text: str) -> Tuple[float, List[str]]:
        """Check 10: Skill Context (5 points)"""
        score = 0.0
        feedback = []
        
        if not skills:
            return 0, ["No skills listed"]
        
        # More lenient matching - check for partial matches and word boundaries
        experience_lower = experience_text.lower()
        contextual_skills = []
        
        for skill in skills:
            skill_lower = skill.lower()
            # Check exact match or as part of compound terms
            if skill_lower in experience_lower or any(word in experience_lower for word in skill_lower.split()):
                contextual_skills.append(skill)
        
        context_rate = len(contextual_skills) / len(skills)
        # More lenient: Give credit for having skills listed
        if context_rate >= 0.7:
            score = 5.0  # Excellent - most skills demonstrated
        elif context_rate >= 0.5:
            score = 4.0  # Good - half skills demonstrated
        elif context_rate >= 0.3:
            score = 3.5  # Acceptable - some skills demonstrated
        else:
            score = 2.5  # Has skills listed - give base credit
        
        if context_rate < 0.3:
            feedback.append(f"Only {len(contextual_skills)}/{len(skills)} skills demonstrated in experience")
        elif context_rate < 0.6:
            feedback.append(f"Fair skill context: {len(contextual_skills)}/{len(skills)} skills shown")
        else:
            feedback.append(f"Strong skill context: {len(contextual_skills)}/{len(skills)} skills demonstrated")
        
        return score, feedback
    
    def check_semantic_fit(self, resume_text: str, jd_text: str) -> Tuple[float, List[str]]:
        """Check 11: Semantic Job-Fit (20 points) - The AI Score with KB Enhancement"""
        # Input validation
        if not resume_text or not isinstance(resume_text, str):
            return 0.0, ["Invalid resume text"]
        if not jd_text or not isinstance(jd_text, str):
            return 20.0, []  # Full score if no JD
        
        score = 0.0
        feedback = []
        
        try:
            if self.kb:
                # KB-enhanced semantic matching
                score, feedback = self._kb_enhanced_semantic_fit(resume_text, jd_text)
            else:
                # Fallback: Direct S-BERT similarity
                score, feedback = self._direct_semantic_fit(resume_text, jd_text)
        except Exception as e:
            import logging
            logging.warning(f"Semantic fit error: {e}")
            score = 5.0  # Low score on error to avoid false positives
            feedback = ["Semantic analysis failed"]
        
        return score, feedback
    
    def _kb_enhanced_semantic_fit(self, resume_text: str, jd_text: str) -> Tuple[float, List[str]]:
        """KB-enhanced semantic matching with role-specific validation"""
        MAX_TEXT_LENGTH = 2000  # Truncate long texts for performance
        feedback = []
        critical_match_rate = 0.5  # Default if TF-IDF fails
        
        # Step 1: Check for critical role-specific keywords
        resume_lower = resume_text.lower()
        jd_lower = jd_text.lower()
        
        # Extract critical technical terms from JD (TF-IDF top terms)
        try:
            vectorizer = TfidfVectorizer(stop_words='english', max_features=10, ngram_range=(1, 2))
            tfidf_matrix = vectorizer.fit_transform([jd_text])
            feature_names = vectorizer.get_feature_names_out()
            jd_vector = tfidf_matrix[0].toarray()[0]
            critical_terms = [feature_names[i] for i in jd_vector.argsort()[-10:][::-1]]
            
            # Check how many critical terms are in resume
            found_critical = sum(1 for term in critical_terms if term.lower() in resume_lower)
            critical_match_rate = found_critical / len(critical_terms) if critical_terms else 0.5
            
            # Heavy penalty only for severe mismatches (< 25% match)
            if critical_match_rate < 0.25:
                missing_terms = [t for t in critical_terms[:5] if t.lower() not in resume_lower]
                feedback.append(f"Critical mismatch - missing: {', '.join(missing_terms)}")
                return 0.0 + (critical_match_rate * 10), feedback  # Max 2.5 points if <25% match
        except Exception as e:
            import logging
            logging.warning(f"TF-IDF extraction failed: {e}")
            critical_match_rate = 0.5  # Neutral default
        
        # Step 2: Semantic similarity (only if critical terms present)
        try:
            resume_embedding = self.semantic_model.encode(resume_text[:MAX_TEXT_LENGTH], convert_to_tensor=False)
            jd_embedding = self.semantic_model.encode(jd_text[:MAX_TEXT_LENGTH], convert_to_tensor=False)
            
            from sklearn.metrics.pairwise import cosine_similarity
            similarity = cosine_similarity([resume_embedding], [jd_embedding])[0][0]
            
            # Apply critical term boost/penalty to semantic score
            if critical_match_rate >= 0.6:
                # Boost for strong keyword match (60%+ keywords present)
                score = float(similarity) * 20 * min(1.2, 0.8 + critical_match_rate * 0.4)
            elif critical_match_rate >= 0.35:
                # Standard scoring for moderate match (35-60% keywords)
                score = float(similarity) * 20 * max(0.7, critical_match_rate + 0.3)
            else:
                # Penalty for weak match (25-35% keywords)
                score = float(similarity) * 20 * 0.5
            
            if similarity >= 0.65 and critical_match_rate >= 0.5:
                feedback.append(f"Strong match ({similarity*100:.0f}% semantic, {critical_match_rate*100:.0f}% keywords)")
            elif similarity >= 0.5 and critical_match_rate >= 0.35:
                feedback.append(f"Good match ({similarity*100:.0f}% semantic, {critical_match_rate*100:.0f}% keywords)")
            elif critical_match_rate < 0.3:
                feedback.append(f"Weak match ({similarity*100:.0f}%) - wrong role fit")
            else:
                feedback.append(f"Moderate match ({similarity*100:.0f}% semantic, {critical_match_rate*100:.0f}% keywords)")
            
            return score, feedback
        except Exception as e:
            import logging
            logging.warning(f"Semantic embedding failed: {e}")
        
        # Fallback: return low score if semantic analysis failed
        return 5.0, ["Semantic analysis failed"]
    
    def _direct_semantic_fit(self, resume_text: str, jd_text: str) -> Tuple[float, List[str]]:
        """Direct S-BERT similarity (fallback when KB unavailable)"""
        feedback = []
        
        # Truncate for performance
        resume_chunk = resume_text[:2000]
        jd_chunk = jd_text[:2000]
        
        resume_embedding = self.semantic_model.encode(resume_chunk, convert_to_tensor=False)
        jd_embedding = self.semantic_model.encode(jd_chunk, convert_to_tensor=False)
        
        similarity = cosine_similarity([resume_embedding], [jd_embedding])[0][0]
        score = float(similarity) * 20
        
        if similarity >= 0.7:
            feedback.append(f"Strong semantic match ({similarity*100:.0f}%)")
        elif similarity < 0.5:
            feedback.append(f"Low job-fit ({similarity*100:.0f}%) - tailor resume to JD")
        
        return score, feedback
