"""
Phase 2: Readability & Quality Module
Grammar, readability, professional language checks
"""
import re
import textstat
from collections import Counter
from typing import Dict, List, Tuple

class ReadabilityChecker:
    """Rule-based text quality analysis"""
    
    ACTION_VERBS = {
        'led', 'managed', 'developed', 'created', 'implemented', 'designed',
        'built', 'launched', 'increased', 'improved', 'reduced', 'achieved',
        'delivered', 'executed', 'established', 'optimized', 'streamlined',
        'coordinated', 'directed', 'spearheaded', 'initiated', 'drove'
    }
    
    BUZZWORDS = {
        'team player', 'hardworking', 'go-getter', 'synergy', 'leverage',
        'think outside the box', 'results-driven', 'detail-oriented',
        'self-starter', 'motivated', 'passionate', 'dynamic'
    }
    
    def check_readability(self, text: str) -> Tuple[float, List[str]]:
        """Check 4: Readability & Clarity (10 points)"""
        score = 7.0  # Start with base score
        feedback = []
        
        try:
            flesch_score = textstat.flesch_reading_ease(text)
            
            if 60 <= flesch_score <= 80:
                score = 10.0  # Optimal range - full points
            elif flesch_score < 60:
                score = 6.0  # Slightly complex - still acceptable
                feedback.append("Consider simplifying complex sentences")
            elif flesch_score > 80:
                score = 8.0  # Simple - good for ATS
        except:
            score = 7.0  # Neutral if can't calculate
        
        return score, feedback
    
    def check_professional_language(self, text: str, experience_bullets: List[str]) -> Tuple[float, List[str]]:
        """Check 5: Professional Language (10 points)"""
        score = 6.0  # Start with base score
        feedback = []
        
        # Action verbs check (give credit, not penalty)
        if experience_bullets:
            action_verb_count = 0
            for bullet in experience_bullets:
                first_word = bullet.strip().split()[0].lower() if bullet.strip() else ''
                if first_word in self.ACTION_VERBS:
                    action_verb_count += 1
            
            action_verb_pct = action_verb_count / len(experience_bullets) if experience_bullets else 0
            if action_verb_pct >= 0.8:
                score = 10.0  # Excellent
            elif action_verb_pct >= 0.5:
                score = 8.0  # Good
            elif action_verb_pct >= 0.3:
                score = 7.0  # Acceptable
            else:
                score = 6.0  # Needs improvement
                feedback.append(f"Use more action verbs (currently {action_verb_pct*100:.0f}%)")
        else:
            score = 7.0  # No bullets to check - give benefit of doubt
        
        # Buzzwords check (minor penalty only)
        text_lower = text.lower()
        found_buzzwords = [bw for bw in self.BUZZWORDS if bw in text_lower]
        if len(found_buzzwords) > 3:
            score -= 1
            feedback.append(f"Reduce buzzwords: {', '.join(found_buzzwords[:2])}")
        
        return max(0, score), feedback
