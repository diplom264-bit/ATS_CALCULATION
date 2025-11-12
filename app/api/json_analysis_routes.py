"""
JSON Analysis Engine API - Standalone dashboard for JSON-only input
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scoring_engine" / "src"))

from kb_enhanced_scorer import KBEnhancedScorer

sys.path.insert(0, str(Path(__file__).parent.parent))
from services.smart_skill_matcher import SmartSkillMatcher

router = APIRouter(prefix="/api/v1/json-analysis", tags=["JSON Analysis"])

scorer = KBEnhancedScorer()
skill_matcher = SmartSkillMatcher()

@router.post("/analyze")
async def analyze_json(jd_file: UploadFile = File(...), resume_file: UploadFile = File(...)):
    """Analyze resume against JD using JSON files"""
    try:
        jd_content = await jd_file.read()
        jd_data = json.loads(jd_content.decode('utf-8'))
        
        resume_content = await resume_file.read()
        resume_data = json.loads(resume_content.decode('utf-8'))
        
        # Extract skills for smart matching
        resume_skills = []
        if 'technical_skills' in resume_data:
            for skills_list in resume_data['technical_skills'].values():
                resume_skills.extend(skills_list)
        
        jd_skills = jd_data.get('required_skills', [])
        
        # Smart skill matching with KB
        matched, missing, match_pct = skill_matcher.match_skills(resume_skills, jd_skills)
        
        # Store original matched/missing before transformation
        smart_matched = matched.copy()
        smart_missing = missing.copy()
        
        # Transform resume data to scorer format
        resume_data = transform_resume_format(resume_data)
        jd_data = transform_jd_format(jd_data)
        
        # Override skill match results with smart matching
        resume_data['_matched_skills'] = matched
        resume_data['_missing_skills'] = missing
        resume_data['_skill_match_pct'] = match_pct
        
        layout_data = {'ats_compatible': True, 'date_format_consistency': 1.0, 'formatting_issues': []}
        
        result = scorer.score(resume_data, jd_data, layout_data)
        
        # Use smart matching results (don't override with scorer's evidence)
        matched = smart_matched
        missing = smart_missing
        
        # Generate recommendations
        recs = []
        scores = result['factor_scores']
        
        if scores.get('skill_match', 0) < 70:
            recs.append(f"Add {len(missing)} missing skills: {', '.join(missing[:3])}...")
        if scores.get('experience', 0) < 70:
            recs.append("Highlight more years of relevant experience")
        if scores.get('keywords', 0) < 60:
            recs.append("Include more keywords from job description")
        if scores.get('title', 0) < 60:
            recs.append("Align job title with position requirements")
        if scores.get('education', 0) < 80:
            recs.append("Add or emphasize educational qualifications")
        
        if not recs:
            recs.append(f"Excellent match! {len(matched)} skills matched with no critical gaps.")
        
        return {
            "status": "ok",
            "analysis": {
                "final_score": result['total_score'],
                "grade": result['grade'],
                "scores": result['factor_scores'],
                "evidence": {
                    "matched_skills": matched,
                    "missing_skills": missing,
                    "matched_count": len(matched),
                    "missing_count": len(missing)
                },
                "breakdown": result['breakdown'],
                "recommendations": recs
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def transform_resume_format(data: dict) -> dict:
    """Transform resume JSON to scorer format"""
    # Flatten skills from both 'skills' and 'technical_skills'
    skills = []
    
    # Check 'technical_skills' first (new format)
    if 'technical_skills' in data:
        if isinstance(data['technical_skills'], dict):
            for category, skill_list in data['technical_skills'].items():
                if isinstance(skill_list, list):
                    skills.extend(skill_list)
        elif isinstance(data['technical_skills'], list):
            skills = data['technical_skills']
    
    # Also check 'skills' (old format)
    if 'skills' in data:
        if isinstance(data['skills'], dict):
            for category, skill_list in data['skills'].items():
                if isinstance(skill_list, list):
                    skills.extend(skill_list)
        elif isinstance(data['skills'], list):
            skills.extend(data['skills'])
    
    # Calculate total experience
    years_exp = 0
    if 'experience' in data:
        for exp in data['experience']:
            years_exp += exp.get('years', 0)
    
    # Get title from first experience
    title = ''
    if 'experience' in data and data['experience']:
        title = data['experience'][0].get('title', '')
    
    return {
        'name': data.get('name', ''),
        'skills': skills,
        'years_experience': years_exp,
        'experience': data.get('experience', []),
        'education': [e.get('degree', '') for e in data.get('education', [])],
        'title': title,
        'text': json.dumps(data)
    }

def transform_jd_format(data: dict) -> dict:
    """Transform JD JSON to scorer format"""
    # Handle both list and dict formats for skills
    required = data.get('required_skills', [])
    preferred = data.get('preferred_skills', [])
    
    must_have = [{'label': s} for s in (required if isinstance(required, list) else [])]
    nice_to_have = [{'label': s} for s in (preferred if isinstance(preferred, list) else [])]
    
    # Extract min experience
    min_exp = 0
    for qual in data.get('qualifications', []):
        match = re.search(r'(\d+)\+?\s*years?', str(qual), re.IGNORECASE)
        if match:
            min_exp = int(match.group(1))
            break
    
    return {
        'title': data.get('title', ''),
        'must_have': must_have,
        'nice_to_have': nice_to_have,
        'min_experience_years': min_exp,
        'text': json.dumps(data)
    }

@router.get("/health")
async def health():
    return {"status": "ok"}
