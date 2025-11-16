"""Test pyresparser library for comparison"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("="*80)
print("PYRESPARSER TEST")
print("="*80)

# Install if needed
try:
    from pyresparser import ResumeParser
    print("✅ pyresparser installed")
except ImportError:
    print("⚠️  pyresparser not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyresparser"])
    from pyresparser import ResumeParser
    print("✅ pyresparser installed")

pdf_path = r"C:\Users\Owner\Downloads\RitikSharma_BI Developer.pdf"

print(f"\n📄 File: {Path(pdf_path).name}")
print("\n🔧 Running pyresparser...")

try:
    data = ResumeParser(pdf_path).get_extracted_data()
    
    print("\n📋 EXTRACTED DATA:\n")
    
    for key, value in data.items():
        if value:
            if isinstance(value, list):
                print(f"  {key:20} : {len(value)} items")
                for item in value[:5]:
                    print(f"                         - {item}")
            else:
                print(f"  {key:20} : {value}")
    
    print("\n" + "="*80)
    print("✅ pyresparser extraction complete")
    print("="*80)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nNote: pyresparser may have dependency issues.")
    print("It requires: spacy, nltk, pdfminer, docx2txt, etc.")
