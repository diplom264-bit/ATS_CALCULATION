"""Quick extraction test"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.file_parser import FileParser
from app.services.production_ner_extractor import ProductionNERExtractor

resume_path = r"C:\Users\Owner\Downloads\RitikSharma_BI Developer.pdf"

result = FileParser.parse(resume_path)
text = result.get('text', '')

print("Extracting...")
extractor = ProductionNERExtractor()
entities = extractor.extract(text)

print(f"\nCompanies ({len(entities['companies'])}):")
for c in entities['companies']:
    print(f"  - {c}")

print(f"\nJob Titles ({len(entities['job_titles'])}):")
for t in entities['job_titles']:
    print(f"  - {t}")
