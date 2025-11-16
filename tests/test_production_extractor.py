"""Test Production Extractor - Final Test"""
import sys
sys.path.insert(0, 'D:/ATSsys/version_4')

from app.services.preprocessing_engine import PreprocessingEngine
from app.services.production_extractor import ProductionExtractor

print("="*80)
print("PRODUCTION EXTRACTOR - FINAL TEST")
print("="*80)

preprocessor = PreprocessingEngine()
extractor = ProductionExtractor()

resumes = [
    (r"C:\Users\Owner\Downloads\RitikSharma_BI Developer.pdf", "Ritik"),
    (r"C:\Users\Owner\Downloads\Nakul_Saraswat_Resume 1 (1).pdf", "Nakul")
]

for resume_path, name in resumes:
    print(f"\n{'='*80}")
    print(f"📄 {name}'s Resume")
    print(f"{'='*80}")
    
    # Preprocess
    preprocessed = preprocessor.process(resume_path)
    print(f"✅ Preprocessed: {preprocessed['metadata']['pages']} page(s), {preprocessed['metadata']['total_blocks']} blocks")
    
    # Extract
    entities = extractor.extract(preprocessed)
    
    # Display results
    print(f"\n👤 PERSONAL INFO:")
    print(f"   Name: {entities['name'] or '❌ NOT FOUND'}")
    print(f"   Email: {entities['email'] or '❌ NOT FOUND'}")
    print(f"   Phone: {entities['phone'] or '❌ NOT FOUND'}")
    print(f"   LinkedIn: {entities['linkedin'] or '-'}")
    print(f"   GitHub: {entities['github'] or '-'}")
    
    print(f"\n🏢 EXPERIENCE:")
    print(f"   Companies: {len(entities['companies'])}")
    for i, c in enumerate(entities['companies'], 1):
        print(f"     {i}. {c}")
    if not entities['companies']:
        print(f"     ❌ NO COMPANIES FOUND")
    
    print(f"\n   Job Titles: {len(entities['job_titles'])}")
    for i, t in enumerate(entities['job_titles'], 1):
        print(f"     {i}. {t}")
    if not entities['job_titles']:
        print(f"     ❌ NO TITLES FOUND")
    
    print(f"\n💼 SKILLS: {len(entities['skills'])}")
    if entities['skills']:
        for i, s in enumerate(entities['skills'][:10], 1):
            print(f"     {i}. {s}")
        if len(entities['skills']) > 10:
            print(f"     ... and {len(entities['skills']) - 10} more")
    else:
        print(f"     ❌ NO SKILLS FOUND")
    
    print(f"\n🎓 EDUCATION:")
    print(f"   Degrees: {len(entities['degrees'])}")
    for i, d in enumerate(entities['degrees'], 1):
        print(f"     {i}. {d}")
    if not entities['degrees']:
        print(f"     ❌ NO DEGREES FOUND")
    
    print(f"\n   Universities: {len(entities['universities'])}")
    for i, u in enumerate(entities['universities'], 1):
        print(f"     {i}. {u}")
    
    print(f"\n📍 Locations: {', '.join(entities['locations'][:3]) if entities['locations'] else '-'}")

print(f"\n{'='*80}")
print("✅ PRODUCTION EXTRACTOR TEST COMPLETE")
print(f"{'='*80}")
