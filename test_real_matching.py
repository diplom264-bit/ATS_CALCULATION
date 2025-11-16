"""Test real JD + Resume matching with fixed KB"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'app'))

from services.smart_skill_matcher import SmartSkillMatcher

# Real Data Analyst JD
JD_TEXT = """
Data Analyst Position

Required Skills:
- SQL and database querying
- Python for data analysis
- Excel and data visualization
- Statistical analysis
- Power BI or Tableau
- ETL processes
- Data modeling
- Communication skills

Preferred:
- Machine learning basics
- R programming
- AWS or Azure cloud
"""

# Real Resume Example 1: Strong match
RESUME_1 = """
Skills:
- SQL (MySQL, PostgreSQL)
- Python (pandas, numpy, matplotlib)
- Microsoft Excel (pivot tables, vlookup)
- Statistics and probability
- Tableau dashboards
- Data warehousing
- Database design
- Strong communication
"""

# Real Resume Example 2: Partial match
RESUME_2 = """
Skills:
- Basic SQL
- Excel spreadsheets
- Data entry
- Microsoft Office
- Customer service
- Team collaboration
"""

# Real Resume Example 3: Different domain (Software Engineer)
RESUME_3 = """
Skills:
- Python (Django, Flask)
- JavaScript (React, Node.js)
- Docker and Kubernetes
- Git version control
- RESTful APIs
- Agile methodology
"""

def extract_skills(text):
    """Extract skills from text (simple line-based extraction)"""
    skills = []
    for line in text.split('\n'):
        line = line.strip()
        if line.startswith('-'):
            skill = line[1:].strip()
            # Remove parenthetical details
            if '(' in skill:
                skill = skill.split('(')[0].strip()
            skills.append(skill)
    return skills

def test_matching():
    matcher = SmartSkillMatcher(fuzzy_threshold=0.75, kb_threshold=0.55)
    
    jd_skills = extract_skills(JD_TEXT)
    
    print("="*70)
    print("JOB DESCRIPTION SKILLS")
    print("="*70)
    for skill in jd_skills:
        print(f"  - {skill}")
    
    resumes = [
        ("Strong Match (Data Analyst)", RESUME_1),
        ("Weak Match (Entry Level)", RESUME_2),
        ("Wrong Domain (Software Engineer)", RESUME_3)
    ]
    
    for name, resume_text in resumes:
        resume_skills = extract_skills(resume_text)
        
        print(f"\n{'='*70}")
        print(f"RESUME: {name}")
        print("="*70)
        print("Resume Skills:")
        for skill in resume_skills:
            print(f"  - {skill}")
        
        # Match
        details = matcher.get_match_details(resume_skills, jd_skills)
        
        print(f"\n📊 MATCH RESULTS:")
        print(f"  Match Score: {details['match_percentage']:.1f}%")
        print(f"  Matched: {len(details['matched_skills'])}/{details['total_jd_skills']}")
        
        print(f"\n✅ Matched Skills ({len(details['matched_skills'])}):")
        for jd_skill in details['matched_skills']:
            resume_skill = details['match_map'].get(jd_skill, '?')
            print(f"  ✓ {jd_skill} ← {resume_skill}")
        
        print(f"\n❌ Missing Skills ({len(details['missing_skills'])}):")
        for skill in details['missing_skills'][:5]:
            print(f"  ✗ {skill}")
        if len(details['missing_skills']) > 5:
            print(f"  ... and {len(details['missing_skills']) - 5} more")

if __name__ == "__main__":
    test_matching()
