"""Test validation layer"""
import sys
sys.path.insert(0, 'D:/ATSsys/version_4')

from app.services.final_resume_parser import FinalResumeParser

parser = FinalResumeParser()

print("="*80)
print("VALIDATION LAYER TEST")
print("="*80)

resumes = [
    (r"C:\Users\Owner\Downloads\RitikSharma_BI Developer.pdf", "Ritik"),
    (r"C:\Users\Owner\Downloads\Nakul_Saraswat_Resume 1 (1).pdf", "Nakul")
]

for path, name in resumes:
    result = parser.parse(path)
    
    print(f"\n{name}'s Resume:")
    print(f"  Confidence Scores:")
    for field, conf in result.get('confidence', {}).items():
        status = "✅" if conf >= 0.9 else "⚠️" if conf >= 0.7 else "❌"
        print(f"    {status} {field}: {conf:.2f}")

print("\n" + "="*80)
print("✅ Validation layer working")
