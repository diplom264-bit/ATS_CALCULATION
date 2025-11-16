"""Test Generalized Extractor on multiple resumes"""
import sys
sys.path.insert(0, 'D:/ATSsys/version_4')

from app.services.preprocessing_engine import PreprocessingEngine
from app.services.generalized_extractor import GeneralizedExtractor

print("="*80)
print("GENERALIZED EXTRACTOR TEST")
print("="*80)

preprocessor = PreprocessingEngine()
extractor = GeneralizedExtractor()

resumes = [
    (r"C:\Users\Owner\Downloads\RitikSharma_BI Developer.pdf", "Ritik"),
    (r"C:\Users\Owner\Downloads\Nakul_Saraswat_Resume 1 (1).pdf", "Nakul")
]

for resume_path, name in resumes:
    print(f"\n{'='*80}")
    print(f"{name}'s Resume")
    print(f"{'='*80}")
    
    # Preprocess
    preprocessed = preprocessor.process(resume_path)
    
    # Extract
    entities = extractor.extract(preprocessed)
    
    # Display results
    print(f"\n📋 Basic Info:")
    print(f"   Name: {entities['name']} (conf: {entities['confidence'].get('name', 0):.2f})")
    print(f"   Email: {entities['email']} (conf: {entities['confidence'].get('email', 0):.2f})")
    print(f"   Phone: {entities['phone']} (conf: {entities['confidence'].get('phone', 0):.2f})")
    print(f"   LinkedIn: {entities['linkedin']}")
    print(f"   GitHub: {entities['github']}")
    
    print(f"\n🏢 Experience (conf: {entities['confidence'].get('experience', 0):.2f}):")
    print(f"   Companies ({len(entities['companies'])}):")
    for c in entities['companies']:
        print(f"     - {c}")
    print(f"   Titles ({len(entities['job_titles'])}):")
    for t in entities['job_titles']:
        print(f"     - {t}")
    
    print(f"\n💼 Skills (conf: {entities['confidence'].get('skills', 0):.2f}):")
    print(f"   Total: {len(entities['skills'])}")
    for s in entities['skills'][:10]:
        print(f"     - {s}")
    if len(entities['skills']) > 10:
        print(f"     ... and {len(entities['skills']) - 10} more")
    
    print(f"\n🎓 Education (conf: {entities['confidence'].get('education', 0):.2f}):")
    for d in entities['degrees']:
        print(f"     - {d}")

print(f"\n{'='*80}")
print("✅ Generalized Extractor Test Complete")
print(f"{'='*80}")
