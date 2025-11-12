"""
Phase 5: Impact & Advanced Module
Quantified achievements, online presence
"""
import re
import spacy
from spacy.matcher import Matcher
from typing import Dict, List, Tuple

class ImpactChecker:
    """Achievement and impact analysis"""
    
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
            self.matcher = Matcher(self.nlp.vocab)
            self._setup_patterns()
        except:
            self.nlp = None
            self.matcher = None
    
    def _setup_patterns(self):
        """Setup spaCy patterns for quantified metrics"""
        if not self.matcher:
            return
        
        # Pattern: "X%"
        pattern_percent = [{"LIKE_NUM": True}, {"ORTH": "%"}]
        
        # Pattern: "increased by X%"
        pattern_increased = [
            {"LOWER": {"IN": ["increased", "improved", "reduced", "grew"]}},
            {"LOWER": "by", "OP": "?"},
            {"LIKE_NUM": True},
            {"ORTH": "%"}
        ]
        
        # Pattern: "$X" or "$XM" or "$XK"
        pattern_money = [
            {"ORTH": "$"},
            {"LIKE_NUM": True},
            {"LOWER": {"IN": ["k", "m", "b", "million", "billion"]}, "OP": "?"}
        ]
        
        # Pattern: "X users/customers/clients"
        pattern_scale = [
            {"LIKE_NUM": True},
            {"LOWER": {"IN": ["users", "customers", "clients", "employees", "projects"]}}
        ]
        
        self.matcher.add("QuantifiedImpact", [pattern_percent, pattern_increased, pattern_money, pattern_scale])
    
    def check_quantified_achievements(self, experience_text: str) -> Tuple[float, List[str]]:
        """Check 12: Quantified Achievements (10 points)"""
        score = 0.0
        feedback = []
        
        if not experience_text:
            return 0, ["No experience section to analyze"]
        
        # Regex-based detection (fallback)
        metrics_found = 0
        
        # Numbers with %
        percent_matches = re.findall(r'\d+%', experience_text)
        metrics_found += len(percent_matches)
        
        # Dollar amounts
        money_matches = re.findall(r'\$\d+[KMB]?', experience_text, re.IGNORECASE)
        metrics_found += len(money_matches)
        
        # Numbers with scale words
        scale_matches = re.findall(r'\d+\+?\s+(users|customers|clients|employees|projects)', experience_text, re.IGNORECASE)
        metrics_found += len(scale_matches)
        
        # spaCy-based detection (if available)
        if self.nlp and self.matcher:
            try:
                doc = self.nlp(experience_text[:5000])  # Limit for performance
                matches = self.matcher(doc)
                metrics_found += len(matches)
            except:
                pass
        
        # More lenient scoring: Give credit for having experience
        # Not all roles need heavy quantification (e.g., research, creative)
        has_experience = len(experience_text) > 100 and any(word in experience_text.lower() for word in ['developed', 'created', 'implemented', 'managed', 'led', 'designed', 'built', 'worked', 'responsible'])
        
        if metrics_found >= 5:
            score = 10.0  # Excellent quantification
        elif metrics_found >= 3:
            score = 8.0  # Good quantification
        elif metrics_found >= 1:
            score = 6.0  # Some quantification
        elif has_experience:
            score = 5.0  # Has experience but no metrics - still acceptable
        else:
            score = 0.0  # No experience or metrics
        
        if metrics_found == 0:
            feedback.append("Add quantified achievements (%, $, numbers)")
        elif metrics_found < 3:
            feedback.append(f"{metrics_found} metric(s) found - add more for stronger impact")
        else:
            feedback.append(f"Strong quantification: {metrics_found} metrics found")
        
        return score, feedback
    
    def check_online_presence(self, contact_text: str) -> Tuple[float, List[str]]:
        """Check 13: Online Presence (5 points)"""
        score = 0.0
        feedback = []
        
        if not contact_text:
            return 0, []
        
        contact_lower = contact_text.lower()
        
        # LinkedIn
        if re.search(r'linkedin\.com', contact_lower):
            score += 2
            feedback.append("LinkedIn profile included")
        else:
            feedback.append("Add LinkedIn profile URL")
        
        # GitHub/Portfolio
        if re.search(r'github\.com', contact_lower):
            score += 3
            feedback.append("GitHub profile included")
        elif re.search(r'(portfolio|website|blog)', contact_lower):
            score += 2
            feedback.append("Portfolio/website included")
        else:
            feedback.append("Consider adding GitHub or portfolio link")
        
        return score, feedback
