"""Test Preprocessing Engine V2"""
import sys
sys.path.insert(0, 'D:/ATSsys/version_4')

from app.services.preprocessing_engine_v2 import PreprocessingEngineV2

print("="*80)
print("PREPROCESSING ENGINE V2 TEST")
print("="*80)

engine = PreprocessingEngineV2()

resumes = [
    (r"C:\Users\Owner\Downloads\RitikSharma_BI Developer.pdf", "Ritik"),
    (r"C:\Users\Owner\Downloads\Nakul_Saraswat_Resume 1 (1).pdf", "Nakul")
]

for resume_path, name in resumes:
    print(f"\n{'='*80}")
    print(f"📄 {name}'s Resume")
    print(f"{'='*80}")
    
    result = engine.process(resume_path)
    
    if result['status'] != 'ok':
        print(f"❌ Error: {result.get('error')}")
        continue
    
    print(f"\n✅ Preprocessing successful")
    print(f"   Pages: {result['metadata']['pages']}")
    print(f"   Total lines: {result['metadata']['total_lines']}")
    print(f"   Avg font size: {result['metadata']['avg_font_size']:.1f}")
    
    print(f"\n📋 Section Headers Detected:")
    section_headers = [l for l in result['lines'] if l.get('is_section_header')]
    print(f"   Total: {len(section_headers)}")
    for header in section_headers:
        print(f"     - '{header['text']}' (conf: {header['section_confidence']:.2f}, size: {header['font_size']:.1f}, bold: {header['is_bold']})")
    
    print(f"\n📚 Sections Extracted:")
    print(f"   Total: {len(result['sections'])}")
    for name, data in result['sections'].items():
        print(f"     - {name}: {len(data['text'])} chars (conf: {data['confidence']:.2f})")
        print(f"       First 100 chars: {data['text'][:100]}...")
    
    print(f"\n📝 Clean Text Sample (first 300 chars):")
    print(f"   {result['clean_text'][:300]}...")
    
    # Check for specific sections
    print(f"\n✓ Section Check:")
    print(f"   SKILLS: {'✅' if 'SKILLS' in result['sections'] else '❌'}")
    print(f"   EXPERIENCE: {'✅' if 'EXPERIENCE' in result['sections'] else '❌'}")
    print(f"   EDUCATION: {'✅' if 'EDUCATION' in result['sections'] else '❌'}")

print(f"\n{'='*80}")
print("✅ PREPROCESSING ENGINE V2 TEST COMPLETE")
print(f"{'='*80}")
