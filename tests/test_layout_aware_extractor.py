"""Test Layout-Aware Extractor"""
import sys
sys.path.insert(0, 'D:/ATSsys/version_4')

from app.services.preprocessing_engine import PreprocessingEngine
from app.services.layout_aware_extractor import LayoutAwareExtractor

print("="*80)
print("LAYOUT-AWARE EXTRACTOR TEST")
print("="*80)

preprocessor = PreprocessingEngine()
extractor = LayoutAwareExtractor()

# Test Ritik's resume
print("\n1. Ritik's Resume:")
preprocessed1 = preprocessor.process(r"C:\Users\Owner\Downloads\RitikSharma_BI Developer.pdf")
entities1 = extractor.extract(preprocessed1)

print(f"   Name: {entities1['name']}")
print(f"   Email: {entities1['email']}")
print(f"   Phone: {entities1['phone']}")
print(f"   LinkedIn: {entities1['linkedin']}")
print(f"   GitHub: {entities1['github']}")

print(f"\n   Companies ({len(entities1['companies'])}):")
for c in entities1['companies']:
    print(f"     - {c}")

print(f"\n   Job Titles ({len(entities1['job_titles'])}):")
for t in entities1['job_titles']:
    print(f"     - {t}")

print(f"\n   Skills ({len(entities1['skills'])}):")
for s in entities1['skills'][:10]:
    print(f"     - {s}")

print(f"\n   Degrees ({len(entities1['degrees'])}):")
for d in entities1['degrees']:
    print(f"     - {d}")

# Test Nakul's resume
print("\n" + "="*80)
print("\n2. Nakul's Resume:")
preprocessed2 = preprocessor.process(r"C:\Users\Owner\Downloads\Nakul_Saraswat_Resume 1 (1).pdf")
entities2 = extractor.extract(preprocessed2)

print(f"   Name: {entities2['name']}")
print(f"   Email: {entities2['email']}")
print(f"   Phone: {entities2['phone']}")
print(f"   LinkedIn: {entities2['linkedin']}")
print(f"   GitHub: {entities2['github']}")

print(f"\n   Companies ({len(entities2['companies'])}):")
for c in entities2['companies']:
    print(f"     - {c}")

print(f"\n   Job Titles ({len(entities2['job_titles'])}):")
for t in entities2['job_titles']:
    print(f"     - {t}")

print(f"\n   Skills ({len(entities2['skills'])}):")
for s in entities2['skills'][:10]:
    print(f"     - {s}")

print(f"\n   Degrees ({len(entities2['degrees'])}):")
for d in entities2['degrees']:
    print(f"     - {d}")

print("\n" + "="*80)
print("✅ Layout-Aware Extractor Test Complete")
