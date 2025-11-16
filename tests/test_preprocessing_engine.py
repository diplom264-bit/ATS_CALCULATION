"""Test Preprocessing Engine"""
import sys
sys.path.insert(0, 'D:/ATSsys/version_4')

from app.services.preprocessing_engine import PreprocessingEngine

print("="*80)
print("PREPROCESSING ENGINE TEST")
print("="*80)

engine = PreprocessingEngine()

# Test Ritik's resume
print("\n1. Ritik's Resume:")
result1 = engine.process(r"C:\Users\Owner\Downloads\RitikSharma_BI Developer.pdf")

if result1['status'] == 'ok':
    print(f"   Status: ✅ {result1['status']}")
    print(f"   Pages: {result1['metadata']['pages']}")
    print(f"   Total blocks: {result1['metadata']['total_blocks']}")
    print(f"   Clean text length: {len(result1['clean_text'])} chars")
    print(f"   Sections detected: {len(result1['sections'])}")
    
    print(f"\n   Sections:")
    for sec in result1['sections']:
        print(f"     - {sec['name']} (confidence: {sec['confidence']:.2f}, bold: {sec['is_bold']}, size: {sec['font_size']:.1f})")
    
    print(f"\n   First 300 chars of clean text:")
    print(f"   {result1['clean_text'][:300]}")
    
    print(f"\n   Sample blocks (first 3):")
    for i, block in enumerate(result1['blocks'][:3]):
        print(f"     Block {i}: '{block['text'][:50]}...' (size: {block['font_size']:.1f}, bold: {block['is_bold']})")
else:
    print(f"   Status: ❌ {result1.get('error')}")

# Test Nakul's resume
print("\n" + "="*80)
print("\n2. Nakul's Resume:")
result2 = engine.process(r"C:\Users\Owner\Downloads\Nakul_Saraswat_Resume 1 (1).pdf")

if result2['status'] == 'ok':
    print(f"   Status: ✅ {result2['status']}")
    print(f"   Pages: {result2['metadata']['pages']}")
    print(f"   Total blocks: {result2['metadata']['total_blocks']}")
    print(f"   Clean text length: {len(result2['clean_text'])} chars")
    print(f"   Sections detected: {len(result2['sections'])}")
    
    print(f"\n   Sections:")
    for sec in result2['sections']:
        print(f"     - {sec['name']} (confidence: {sec['confidence']:.2f}, bold: {sec['is_bold']}, size: {sec['font_size']:.1f})")
    
    print(f"\n   First 300 chars of clean text:")
    print(f"   {result2['clean_text'][:300]}")
    
    print(f"\n   Sample blocks (first 3):")
    for i, block in enumerate(result2['blocks'][:3]):
        print(f"     Block {i}: '{block['text'][:50]}...' (size: {block['font_size']:.1f}, bold: {block['is_bold']})")
    
    # Check spacing
    print(f"\n   Spacing check:")
    print(f"     Has 'Power BI': {'Power BI' in result2['clean_text']}")
    print(f"     Has 'Technical Skills': {'Technical Skills' in result2['clean_text']}")
else:
    print(f"   Status: ❌ {result2.get('error')}")

print("\n" + "="*80)
print("✅ Preprocessing Engine Test Complete")
