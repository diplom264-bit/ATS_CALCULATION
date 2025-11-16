"""Test HybridExtractor with real resume"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.file_parser import FileParser
from app.services.hybrid_extractor import HybridExtractor

# Parse real resume
pdf_path = r"C:\Users\Owner\Downloads\RitikSharma_BI Developer.pdf"
result = FileParser.parse(pdf_path)
text = result['text']

print("="*80)
print("HYBRID EXTRACTOR TEST - REAL RESUME")
print("="*80)
print(f"\n📄 File: {Path(pdf_path).name}")
print(f"📏 Text length: {len(text)} chars\n")

# Extract with hybrid approach
extractor = HybridExtractor()
extracted = extractor.extract(text)

print("\n📋 EXTRACTED ENTITIES:\n")
for key, value in extracted.items():
    if value:
        print(f"  {key:15} : {value}")

print("\n" + "="*80)
print("✅ Hybrid extraction complete!")
print("="*80)
