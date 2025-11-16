import sys
sys.path.insert(0, 'D:/ATSsys/version_4')

from app.services.file_parser import FileParser
from app.services.production_ner_extractor import ProductionNERExtractor

result = FileParser.parse(r"C:\Users\Owner\Downloads\RitikSharma_BI Developer.pdf")
text = result.get('text', '')

extractor = ProductionNERExtractor()
entities = extractor.extract(text)

print(f"\nName: {entities['name']}")
print(f"Email: {entities['email']}")
print(f"Phone: {entities['phone']}")
print(f"LinkedIn: {entities['linkedin']}")

print(f"\nCompanies ({len(entities['companies'])}):")
for c in entities['companies']:
    print(f"  - {c}")

print(f"\nJob Titles ({len(entities['job_titles'])}):")
for t in entities['job_titles']:
    print(f"  - {t}")

print(f"\nSkills ({len(entities['skills'])}):")
for s in entities['skills'][:10]:
    print(f"  - {s}")

print(f"\nDegrees ({len(entities['degrees'])}):")
for d in entities['degrees']:
    print(f"  - {d}")

print(f"\nLocations ({len(entities['locations'])}):")
for l in entities['locations']:
    print(f"  - {l}")
