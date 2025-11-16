"""Test scoring generalization"""
import sys
from pathlib import Path

# Ensure we're in version_4 directory
sys.path.insert(0, str(Path(__file__).parent))

from app.services.ml_enhanced_analyzer import MLEnhancedAnalyzer
from app.services.kb_singleton import preload_kb
import os

print("Initializing KB...")
preload_kb()
print("KB loaded.\n")
analyzer = MLEnhancedAnalyzer()

# Test JDs
jd_good_fit = "Python Developer with 5+ years experience in Django, REST APIs, PostgreSQL, Docker, AWS. Must have strong OOP skills, data structures, algorithms."
jd_bad_fit = "Senior Mechanical Engineer with 10+ years in automotive design, CAD, SolidWorks, manufacturing processes, quality control."

# Find test resumes
test_data_path = Path(__file__).parent.parent / 'test_data'
test_files = [f for f in os.listdir(test_data_path) if f.endswith('.pdf')][:2]

print("="*80)
print("SCORING DIAGNOSIS")
print("="*80)

for i, file in enumerate(test_files, 1):
    path = str(test_data_path / file)
    print(f"\n{'='*80}")
    print(f"RESUME {i}: {file}")
    print('='*80)
    
    # Test with good fit JD
    result_good = analyzer.analyze(path, jd_good_fit)
    if result_good['status'] == 'ok' and 'analysis' in result_good:
        analysis = result_good['analysis']
        print(f"\nGOOD FIT JD (Python Dev):")
        print(f"  Final Score: {analysis['final_score']}/100")
        print(f"  Grade: {analysis['grade']}")
        print(f"  Semantic Score: {result_good.get('semantic_score', 0)}/100")
        print(f"\n  Breakdown:")
        for key, val in sorted(analysis['breakdown'].items(), key=lambda x: x[1]):
            print(f"    {key:25s}: {val:5.1f}/100")
    
    # Test with bad fit JD
    result_bad = analyzer.analyze(path, jd_bad_fit)
    if result_bad['status'] == 'ok' and 'analysis' in result_bad:
        analysis = result_bad['analysis']
        print(f"\nBAD FIT JD (Mechanical Eng):")
        print(f"  Final Score: {analysis['final_score']}/100")
        print(f"  Grade: {analysis['grade']}")
        print(f"  Semantic Score: {result_bad.get('semantic_score', 0)}/100")
        print(f"\n  Breakdown:")
        for key, val in sorted(analysis['breakdown'].items(), key=lambda x: x[1]):
            print(f"    {key:25s}: {val:5.1f}/100")
    
    print(f"\n  Skills Extracted: {result_good['extraction']['skills'][:5]}")

print("\n" + "="*80)
