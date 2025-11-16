"""Test spaCy-based extractor"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.file_parser import FileParser
from app.services.spacy_extractor import SpacyExtractor

pdf_path = r"C:\Users\Owner\Downloads\RitikSharma_BI Developer.pdf"
result = FileParser.parse(pdf_path)
text = result['text']

print("="*80)
print("SPACY EXTRACTOR TEST")
print("="*80)
print(f"\n📄 File: {Path(pdf_path).name}")
print(f"📏 Text length: {len(text)} chars\n")

extractor = SpacyExtractor()
extracted = extractor.extract(text)

print("\n📋 EXTRACTED ENTITIES:\n")
for key, value in extracted.items():
    if value:
        print(f"  {key:15} : {value}")

print("\n" + "="*80)
