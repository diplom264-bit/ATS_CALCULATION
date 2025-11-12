"""
Phase 3: Experience & Chronology Module
Date consistency, employment gaps, career progression
"""
import re
from datetime import datetime
from dateutil import parser
from typing import Dict, List, Tuple

class ExperienceChecker:
    """Date and career progression analysis"""
    
    DATE_PATTERNS = [
        r'^\d{2}/\d{4}$',  # 01/2020
        r'^\w{3} \d{4}$',  # Jan 2020
        r'^\w+ \d{4}$',    # January 2020
        r'^\d{4}$'         # 2020
    ]
    
    def check_date_consistency(self, work_history: List[Dict]) -> Tuple[float, List[str]]:
        """Check 6: Date Consistency (5 points)"""
        score = 5.0
        feedback = []
        
        if not work_history:
            return score, feedback
        
        date_strings = []
        for job in work_history:
            if job.get('start_date'):
                date_strings.append(str(job['start_date']))
            if job.get('end_date'):
                date_strings.append(str(job['end_date']))
        
        if not date_strings:
            return score, feedback
        
        # Find first matching pattern
        first_pattern = None
        for pattern in self.DATE_PATTERNS:
            if re.match(pattern, date_strings[0]):
                first_pattern = pattern
                break
        
        if first_pattern:
            inconsistent = [d for d in date_strings[1:] if not re.match(first_pattern, d)]
            if inconsistent:
                score -= 3
                feedback.append("Inconsistent date formatting - use same format throughout")
        
        return max(0, score), feedback
    
    def check_employment_gaps(self, work_history: List[Dict]) -> Tuple[float, List[str]]:
        """Check 7: Employment Gaps (10 points)"""
        score = 10.0
        feedback = []
        
        if len(work_history) < 2:
            return score, feedback
        
        # Sort by start date
        sorted_history = sorted(work_history, key=lambda x: self._parse_date(x.get('start_date', '')))
        
        gaps = []
        for i in range(len(sorted_history) - 1):
            end_date = self._parse_date(sorted_history[i].get('end_date', ''))
            next_start = self._parse_date(sorted_history[i+1].get('start_date', ''))
            
            if end_date and next_start:
                gap_months = (next_start.year - end_date.year) * 12 + (next_start.month - end_date.month)
                if gap_months > 6:
                    gaps.append(gap_months)
        
        if gaps:
            score -= min(10, len(gaps) * 3)
            feedback.append(f"{len(gaps)} employment gap(s) > 6 months detected")
        
        return max(0, score), feedback
    
    def check_career_progression(self, work_history: List[Dict]) -> Tuple[float, List[str]]:
        """Check 8: Career Progression (5 points)"""
        score = 5.0
        feedback = []
        
        if not work_history:
            score = 0
            feedback.append("No work experience listed")
            return score, feedback
        
        # Total years
        total_years = self._calculate_total_years(work_history)
        if total_years < 2:
            score -= 2
            feedback.append(f"Limited experience ({total_years:.1f} years)")
        
        # Check for promotions (same company, different titles)
        companies = {}
        for job in work_history:
            company = job.get('company', '')
            title = job.get('title', '')
            if company:
                if company not in companies:
                    companies[company] = []
                companies[company].append(title)
        
        promotions = sum(1 for titles in companies.values() if len(titles) > 1)
        if promotions > 0:
            score += 2  # Bonus for promotions
            feedback.append(f"Career progression: {promotions} promotion(s) detected")
        
        # Check seniority progression
        seniority_keywords = ['junior', 'senior', 'lead', 'principal', 'manager', 'director']
        titles = [job.get('title', '').lower() for job in work_history]
        has_progression = any(any(kw in t for kw in seniority_keywords) for t in titles)
        
        if not has_progression and len(work_history) > 2:
            score -= 1
            feedback.append("No clear seniority progression in titles")
        
        return min(10, max(0, score)), feedback
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime"""
        if not date_str or date_str.lower() == 'present':
            return datetime.now()
        try:
            return parser.parse(date_str, fuzzy=True)
        except:
            return None
    
    def _calculate_total_years(self, work_history: List[Dict]) -> float:
        """Calculate total years of experience"""
        total_months = 0
        for job in work_history:
            start = self._parse_date(job.get('start_date', ''))
            end = self._parse_date(job.get('end_date', ''))
            if start and end:
                months = (end.year - start.year) * 12 + (end.month - start.month)
                total_months += max(0, months)
        return total_months / 12.0
