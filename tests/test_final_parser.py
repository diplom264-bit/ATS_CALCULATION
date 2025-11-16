"""Test Final Resume Parser"""
import sys
sys.path.insert(0, 'D:/ATSsys/version_4')

from app.services.final_resume_parser import FinalResumeParser

print("="*80)
print("FINAL RESUME PARSER TEST")
print("="*80)

parser = FinalResumeParser()

resumes = [
    (r"C:\Users\Owner\Downloads\RitikSharma_BI Developer.pdf", "Ritik"),
    (r"C:\Users\Owner\Downloads\Nakul_Saraswat_Resume 1 (1).pdf", "Nakul")
]

for resume_path, name in resumes:
    print(f"\n{'='*80}")
    print(f"📄 {name}'s Resume")
    print(f"{'='*80}")
    
    result = parser.parse(resume_path)
    
    if result['status'] != 'ok':
        print(f"❌ Error: {result.get('error')}")
        continue
    
    print(f"\n👤 PERSONAL INFO:")
    print(f"   Name: {result['name'] or '❌ NOT FOUND'}")
    print(f"   Email: {result['email'] or '❌ NOT FOUND'}")
    print(f"   Phone: {result['phone'] or '❌ NOT FOUND'}")
    print(f"   LinkedIn: {result['linkedin'] or '-'}")
    print(f"   GitHub: {result['github'] or '-'}")
    
    print(f"\n🏢 EXPERIENCE:")
    print(f"   Companies: {len(result['companies'])}")
    for i, c in enumerate(result['companies'], 1):
        print(f"     {i}. {c}")
    
    print(f"\n   Job Titles: {len(result['job_titles'])}")
    for i, t in enumerate(result['job_titles'], 1):
        print(f"     {i}. {t}")
    
    print(f"\n💼 SKILLS: {len(result['skills'])}")
    for i, s in enumerate(result['skills'][:10], 1):
        print(f"     {i}. {s}")
    if len(result['skills']) > 10:
        print(f"     ... and {len(result['skills']) - 10} more")
    
    print(f"\n🎓 EDUCATION:")
    print(f"   Degrees: {len(result['degrees'])}")
    for i, d in enumerate(result['degrees'], 1):
        print(f"     {i}. {d}")
    
    print(f"\n   Universities: {len(result['universities'])}")
    for i, u in enumerate(result['universities'], 1):
        print(f"     {i}. {u}")
    
    print(f"\n📍 Locations: {', '.join(result['locations'][:3]) if result['locations'] else '-'}")
    
    # Summary
    print(f"\n📊 EXTRACTION SUMMARY:")
    total_fields = 6  # name, email, phone, skills, companies, degrees
    extracted = sum([
        bool(result['name']),
        bool(result['email']),
        bool(result['phone']),
        bool(result['skills']),
        bool(result['companies']),
        bool(result['degrees'])
    ])
    print(f"   Extracted: {extracted}/{total_fields} core fields")
    print(f"   Status: {'✅ GOOD' if extracted >= 5 else '⚠️ NEEDS IMPROVEMENT' if extracted >= 3 else '❌ POOR'}")

print(f"\n{'='*80}")
print("✅ FINAL RESUME PARSER TEST COMPLETE")
print(f"{'='*80}")
