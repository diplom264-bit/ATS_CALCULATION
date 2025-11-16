"""Test NER extraction on real resume PDF"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.ner_extractor import NERExtractor
from app.services.file_parser import FileParser

# Parse PDF
pdf_path = r"C:\Users\Owner\Downloads\RitikSharma_BI Developer.pdf"
parser = FileParser()
result = parser.parse(pdf_path)
text = result['text']

print("="*80)
print("REAL RESUME NER TEST")
print("="*80)
print(f"\n📄 File: {Path(pdf_path).name}")
print(f"📏 Text length: {len(text)} chars\n")

# Extract entities
ner = NERExtractor()
result = ner.extract(text)

print("📋 EXTRACTED ENTITIES:\n")
for key, value in result.items():
    if value:
        print(f"  {key:15} : {value}")

print("\n" + "="*80)
