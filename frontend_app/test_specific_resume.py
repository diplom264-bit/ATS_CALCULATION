"""Test specific resume and JD"""
import sys
sys.path.insert(0, 'd:/ATSsys/version_4')

from app.services.ml_enhanced_analyzer import MLEnhancedAnalyzer
from app.startup import initialize_app
import fitz

# Initialize
initialize_app()

# Paths
resume_path = r"C:\Users\Owner\Downloads\Naukri_NikharJain[4y_6m] 1  python cv.pdf"
jd_path = r"C:\Users\Owner\Downloads\Python Developer - 3 to 6 years.docx"

# Extract JD text
print("Extracting JD text...")
doc = fitz.open(jd_path)
jd_text = "\n".join(page.get_text() for page in doc)
doc.close()
print(f"JD length: {len(jd_text)} chars\n")

# Analyze
print("Analyzing resume...")
analyzer = MLEnhancedAnalyzer()
result = analyzer.analyze(resume_path, jd_text)

if result['status'] == 'ok':
    print("\n" + "="*80)
    print("EXTRACTION RESULTS")
    print("="*80)
    ext = result['extraction']
    print(f"Name: {ext['name']}")
    print(f"Email: {ext['email']}")
    print(f"Phone: {ext['phone']}")
    print(f"Skills: {len(ext['skills'])} - {', '.join(ext['skills'][:10])}")
    print(f"Companies: {len(ext['companies'])} - {', '.join(ext['companies'][:5])}")
    print(f"Titles: {len(ext['job_titles'])}")
    print(f"Degrees: {len(ext['degrees'])}")
    
    print("\n" + "="*80)
    print("ANALYSIS SCORES")
    print("="*80)
    analysis = result['analysis']
    print(f"Final Score: {analysis['final_score']}/100")
    print(f"Grade: {analysis['grade']}")
    print(f"Semantic Match: {result['semantic_score']}/100")
    
    print("\nBreakdown:")
    for key, value in analysis['breakdown'].items():
        status = "✓" if value >= 70 else "⚠" if value >= 50 else "✗"
        print(f"  {status} {key}: {value:.1f}")
    
    print("\nTop Recommendations:")
    for i, rec in enumerate(result['enhanced_feedback'][:5], 1):
        print(f"  {i}. {rec}")
else:
    print(f"Error: {result.get('error')}")
