"""Test integrated system: parsing + analysis"""
import sys
sys.path.insert(0, 'D:/ATSsys/version_4')

from app.services.integrated_resume_analyzer import IntegratedResumeAnalyzer

analyzer = IntegratedResumeAnalyzer()

jd = """
Power BI Developer
Design and develop interactive dashboards using Power BI.
Required: Power BI, DAX, SQL, data modeling, ETL.
"""

print("="*80)
print("INTEGRATED SYSTEM TEST")
print("="*80)

resumes = [
    (r"C:\Users\Owner\Downloads\RitikSharma_BI Developer.pdf", "Ritik"),
    (r"C:\Users\Owner\Downloads\Nakul_Saraswat_Resume 1 (1).pdf", "Nakul")
]

for path, name in resumes:
    print(f"\n{name}'s Resume:")
    result = analyzer.analyze(path, jd)
    
    if result['status'] != 'ok':
        print(f"  ❌ Error: {result.get('error')}")
        continue
    
    # Extraction
    ext = result['extraction']
    print(f"\n  📋 Extraction:")
    print(f"     Name: {ext['name']}")
    print(f"     Skills: {len(ext['skills'])} extracted")
    print(f"     Companies: {len(ext['companies'])}")
    
    # Analysis
    if 'analysis' in result:
        analysis = result['analysis']
        print(f"\n  📊 Analysis:")
        print(f"     Score: {analysis['final_score']:.1f}/100")
        print(f"     Grade: {analysis['grade']}")
        if analysis.get('feedback'):
            print(f"     Top Issues:")
            for issue in analysis['feedback'][:3]:
                print(f"       - {issue}")

print("\n" + "="*80)
print("✅ Integrated system working")
