"""
Experience Parser - Extract quantified impact and career progression
"""
import re
from typing import Dict, List

def quantify_impact(text: str) -> float:
    """
    Detect quantified achievements in text
    Returns: 0-100 score
    """
    if not text:
        return 0.0
    
    patterns = [
        r'\b\d+%',  # Percentages
        r'\$\d+[KMB]?',  # Dollar amounts
        r'\b\d+\s*(increase|reduction|growth|improvement|saved|generated)',  # Quantified improvements
        r'\b\d+\s*(users|customers|clients|projects)',  # Scale indicators
        r'\b\d+x\b',  # Multipliers
    ]
    
    matches = 0
    for pattern in patterns:
        matches += len(re.findall(pattern, text, re.IGNORECASE))
    
    # Score based on number of quantifications
    if matches >= 5:
        return 100.0
    elif matches >= 3:
        return 75.0
    elif matches >= 1:
        return 50.0
    else:
        return 0.0

def detect_progression(experience_blocks: List[Dict]) -> float:
    """
    Detect career progression from experience
    Returns: 0-100 score
    """
    if not experience_blocks or len(experience_blocks) < 2:
        return 0.0
    
    # Keywords indicating seniority levels
    junior_keywords = ['junior', 'associate', 'intern', 'trainee', 'entry']
    mid_keywords = ['developer', 'engineer', 'analyst', 'consultant']
    senior_keywords = ['senior', 'lead', 'principal', 'architect', 'manager', 'director', 'head']
    
    levels = []
    for exp in experience_blocks:
        title = exp.get('title', '').lower()
        if any(k in title for k in senior_keywords):
            levels.append(3)
        elif any(k in title for k in mid_keywords):
            levels.append(2)
        elif any(k in title for k in junior_keywords):
            levels.append(1)
        else:
            levels.append(2)  # Default to mid-level
    
    # Check if progression is upward
    if len(levels) >= 2:
        if levels[-1] > levels[0]:  # Latest > earliest
            return 80.0
        elif levels[-1] == levels[0] and max(levels) > levels[0]:  # Had progression
            return 60.0
        elif all(l == levels[0] for l in levels):  # Consistent level
            return 40.0
        else:  # Downward or unclear
            return 20.0
    
    return 0.0

def enhance_impact_score(text: str, experience_blocks: List[Dict]) -> Dict[str, float]:
    """
    Compute both quantification and progression scores
    Returns: {'quantified_impact': float, 'career_progression': float}
    """
    return {
        'quantified_impact': quantify_impact(text),
        'career_progression': detect_progression(experience_blocks)
    }
