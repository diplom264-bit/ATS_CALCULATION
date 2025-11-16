"""Test real JD + Resume files with fixed KB"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'app'))

from services.smart_skill_matcher import SmartSkillMatcher
from services.final_resume_parser import FinalResumeParser

def extract_jd_skills(jd_text):
    """Extract skills from JD text"""
    common_skills = [
        '.NET', 'Angular', 'C#', 'ASP.NET', 'SQL Server', 'SQL', 'JavaScript', 
        'TypeScript', 'HTML', 'CSS', 'REST API', 'Web API', 'Entity Framework', 
        'LINQ', 'Azure', 'Git', 'Agile', 'Scrum', 'MVC', 'MVVM', 'Bootstrap',
        'jQuery', 'JSON', 'XML', 'Visual Studio', 'TFS', 'CI/CD', 'Microservices'
    ]
    found_skills = []
    jd_lower = jd_text.lower()
    for skill in common_skills:
        if skill.lower() in jd_lower:
            found_skills.append(skill)
    return found_skills

def test_real_files():
    jd_path = r"C:\Users\Owner\Downloads\ATL .Net + Angular 6-8 yrs.docx"
    resume_path = r"C:\Users\Owner\Downloads\Anurag Kumar Srivastav_2.8 Years_ .Net Angular (1).pdf"
    
    print("="*70)
    print("TESTING REAL JD + RESUME MATCHING WITH FIXED KB")
    print("="*70)
    
    # Parse JD
    print("\n📄 Parsing Job Description...")
    try:
        from docx import Document
        doc = Document(jd_path)
        jd_text = '\n'.join([p.text for p in doc.paragraphs])
        print(f"✓ JD loaded ({len(jd_text)} chars)")
    except Exception as e:
        print(f"✗ Error loading JD: {e}")
        return
    
    jd_skills = extract_jd_skills(jd_text)
    print(f"\n🎯 JD Skills Extracted ({len(jd_skills)}):")
    for skill in jd_skills:
        print(f"  - {skill}")
    
    # Parse Resume
    print(f"\n📄 Parsing Resume...")
    parser = FinalResumeParser()
    
    try:
        resume_data = parser.parse(resume_path)
        print(f"✓ Resume parsed")
    except Exception as e:
        print(f"✗ Error parsing resume: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Extract skills
    skills_data = resume_data.get('skills', {})
    if isinstance(skills_data, dict):
        resume_skills = skills_data.get('technical', []) + skills_data.get('soft', [])
    else:
        resume_skills = skills_data if isinstance(skills_data, list) else []
    
    print(f"\n💼 Resume Skills Extracted ({len(resume_skills)}):")
    for skill in resume_skills[:20]:
        print(f"  - {skill}")
    if len(resume_skills) > 20:
        print(f"  ... and {len(resume_skills) - 20} more")
    
    # Match with KB
    print(f"\n{'='*70}")
    print("SKILL MATCHING WITH FIXED KB")
    print("="*70)
    
    matcher = SmartSkillMatcher(fuzzy_threshold=0.75, kb_threshold=0.55)
    details = matcher.get_match_details(resume_skills, jd_skills)
    
    print(f"\n📊 SKILL ALIGNMENT METRICS:")
    print(f"  Match Score: {details['match_percentage']:.1f}%")
    print(f"  Matched: {len(details['matched_skills'])}/{details['total_jd_skills']} JD requirements")
    print(f"  Total Resume Skills: {details['total_resume_skills']}")
    
    print(f"\n✅ Matched Skills ({len(details['matched_skills'])}):")
    for jd_skill in details['matched_skills']:
        resume_skill = details['match_map'].get(jd_skill, '?')
        print(f"  ✓ {jd_skill} ← {resume_skill}")
    
    print(f"\n❌ Unmatched JD Requirements ({len(details['missing_skills'])}):")
    for skill in details['missing_skills']:
        print(f"  ✗ {skill}")
    
    # Summary
    print(f"\n{'='*70}")
    print("MATCH SUMMARY")
    print("="*70)
    print(f"\nSkill Match Score: {details['match_percentage']:.1f}%")
    print(f"Coverage: {len(details['matched_skills'])}/{details['total_jd_skills']} required skills")
    print(f"\nNote: This is an objective skill alignment measurement.")
    print(f"Hiring decisions should consider experience, culture fit, and other factors.")

if __name__ == "__main__":
    test_real_files()
