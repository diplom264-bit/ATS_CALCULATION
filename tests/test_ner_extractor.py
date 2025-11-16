"""Test NER-Based Extractor"""
import sys
sys.path.insert(0, 'D:/ATSsys/version_4')

from app.services.preprocessing_engine import PreprocessingEngine
from app.services.ner_based_extractor import NERBasedExtractor

print("="*80)
print("NER-BASED EXTRACTOR TEST")
print("="*80)

preprocessor = PreprocessingEngine()
extractor = NERBasedExtractor()

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
    print(f"   Name: {entities['name']}")
    print(f"   Email: {entities['email']}")
    print(f"   Phone: {entities['phone']}")
    print(f"   LinkedIn: {entities['linkedin']}")
    print(f"   GitHub: {entities['github']}")
    
    print(f"\n🏢 Experience:")
    print(f"   Companies ({len(entities['companies'])}):")
    for c in entities['companies']:
        print(f"     - {c}")
    print(f"   Titles ({len(entities['job_titles'])}):")
    for t in entities['job_titles']:
        print(f"     - {t}")
    
    print(f"\n💼 Skills:")
    print(f"   Total: {len(entities['skills'])}")
    for s in entities['skills'][:10]:
        print(f"     - {s}")
    if len(entities['skills']) > 10:
        print(f"     ... and {len(entities['skills']) - 10} more")
    
    print(f"\n🎓 Education:")
    print(f"   Degrees ({len(entities['degrees'])}):")
    for d in entities['degrees']:
        print(f"     - {d}")
    print(f"   Universities ({len(entities['universities'])}):")
    for u in entities['universities']:
        print(f"     - {u}")
    
    print(f"\n📍 Locations ({len(entities['locations'])}):")
    for loc in entities['locations'][:5]:
        print(f"     - {loc}")

print(f"\n{'='*80}")
print("✅ NER-Based Extractor Test Complete")
print(f"{'='*80}")
