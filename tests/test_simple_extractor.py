"""Test Simple Extractor"""
import sys
sys.path.insert(0, 'D:/ATSsys/version_4')

from app.services.file_parser import FileParser
from app.services.simple_extractor import SimpleExtractor

print("="*80)
print("SIMPLE EXTRACTOR TEST")
print("="*80)

extractor = SimpleExtractor()

# Test Ritik
print("\n1. Ritik's Resume:")
result1 = FileParser.parse(r"C:\Users\Owner\Downloads\RitikSharma_BI Developer.pdf")
entities1 = extractor.extract(result1['text'])

print(f"   Name: {entities1['name']}")
print(f"   Email: {entities1['email']}")
print(f"   Phone: {entities1['phone']}")
print(f"   LinkedIn: {entities1['linkedin']}")
print(f"   Companies ({len(entities1['companies'])}):")
for c in entities1['companies']:
    print(f"     - {c}")
print(f"   Titles ({len(entities1['job_titles'])}):")
for t in entities1['job_titles']:
    print(f"     - {t}")
print(f"   Skills: {len(entities1['skills'])}")
print(f"   Degrees: {len(entities1['degrees'])}")

# Test Nakul
print("\n2. Nakul's Resume:")
result2 = FileParser.parse(r"C:\Users\Owner\Downloads\Nakul_Saraswat_Resume 1 (1).pdf")
entities2 = extractor.extract(result2['text'])

print(f"   Name: {entities2['name']}")
print(f"   Email: {entities2['email']}")
print(f"   Phone: {entities2['phone']}")
print(f"   LinkedIn: {entities2['linkedin']}")
print(f"   Companies ({len(entities2['companies'])}):")
for c in entities2['companies']:
    print(f"     - {c}")
print(f"   Titles ({len(entities2['job_titles'])}):")
for t in entities2['job_titles']:
    print(f"     - {t}")
print(f"   Skills: {len(entities2['skills'])}")
print(f"   Degrees: {len(entities2['degrees'])}")

print("\n✅ Test Complete")
