"""Test layout-aware extractor"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.file_parser import FileParser
from app.services.layout_aware_extractor import LayoutAwareExtractor

pdf_path = r"C:\Users\Owner\Downloads\RitikSharma_BI Developer.pdf"
result = FileParser.parse(pdf_path)
text = result['text']

print("="*80)
print("LAYOUT-AWARE EXTRACTOR TEST")
print("="*80)
print(f"\n📄 File: {Path(pdf_path).name}")
print(f"📏 Text length: {len(text)} chars\n")

extractor = LayoutAwareExtractor()
extracted = extractor.extract(text)

print("📋 EXTRACTED ENTITIES:\n")
for key, value in extracted.items():
    if value:
        if isinstance(value, list):
            print(f"  {key:15} : {len(value)} items")
            for item in value[:5]:
                print(f"                    - {item}")
        else:
            print(f"  {key:15} : {value}")

print("\n" + "="*80)
print("✅ Layout-aware extraction complete!")
print("="*80)
