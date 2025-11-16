"""
Test complete ATS analysis integration
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.ats_analyzer import ATSAnalyzer
from app.services.file_parser import FileParser

def test_ats_analysis():
    """Test complete ATS analysis pipeline"""
    
    # Test resume path
    resume_path = Path(r"C:\Users\Owner\Downloads\RitikSharma_BI Developer.pdf")
    
    if not resume_path.exists():
        print(f"❌ Test resume not found: {resume_path}")
        print("\n💡 Update the resume_path variable with your test resume location")
        return
    
    print("=" * 60)
    print("ATS INTEGRATION TEST")
    print("=" * 60)
    
    # Parse resume
    print("\n1️⃣ Parsing resume...")
    parse_result = FileParser.parse(str(resume_path))
    resume_text = parse_result.get('text', '')
    print(f"✅ Extracted {len(resume_text)} characters")
    
    # Initialize analyzer
    print("\n2️⃣ Initializing ATS Analyzer...")
    analyzer = ATSAnalyzer()
    print("✅ Analyzer ready")
    
    # Test without JD
    print("\n3️⃣ Running analysis (no JD)...")
    result = analyzer.analyze_resume(resume_text)
    
    print("\n" + "=" * 60)
    print("ANALYSIS RESULTS")
    print("=" * 60)
    
    print(f"\n📊 SCORE: {result['score']}/100")
    print(f"🎓 GRADE: {result['grade']}")
    
    print("\n📋 EXTRACTED ENTITIES:")
    entities = result['entities']
    print(f"  Name: {entities['name']}")
    print(f"  Email: {entities['email']}")
    print(f"  Phone: {entities['phone']}")
    print(f"  LinkedIn: {entities['linkedin']}")
    print(f"  Skills: {len(entities['skills'])} items")
    print(f"  Companies: {len(entities['companies'])} items")
    print(f"  Job Titles: {len(entities['job_titles'])} items")
    print(f"  Degrees: {len(entities['degrees'])} items")
    print(f"  Locations: {entities['locations']}")
    
    print("\n📈 SCORE BREAKDOWN:")
    for factor, data in result['breakdown'].items():
        print(f"  {factor}: {data['score']*100:.1f}% (weight: {data['weight']*100:.0f}%, contribution: {data['contribution']:.1f})")
    
    print("\n💡 RECOMMENDATIONS:")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"  {i}. [{rec['priority']}] {rec['category']}: {rec['message']}")
    
    # Test with JD
    print("\n" + "=" * 60)
    print("4️⃣ Testing with Job Description...")
    print("=" * 60)
    
    sample_jd = """
    Senior BI Developer
    
    Required Skills:
    - Power BI, Tableau
    - SQL, Python
    - Data Warehousing
    - ETL processes
    - Azure, AWS
    
    Experience:
    - 5+ years in BI development
    - Strong analytical skills
    - Team collaboration
    """
    
    result_with_jd = analyzer.analyze_resume(resume_text, sample_jd)
    
    print(f"\n📊 SCORE (with JD): {result_with_jd['score']}/100")
    print(f"🎓 GRADE: {result_with_jd['grade']}")
    
    print("\n📈 MATCHING SCORES:")
    breakdown = result_with_jd['breakdown']
    print(f"  Keyword Match: {breakdown['keyword_match']['score']*100:.1f}%")
    print(f"  Job Fit (Semantic): {breakdown['job_fit']['score']*100:.1f}%")
    
    print("\n✅ Integration test complete!")

if __name__ == "__main__":
    test_ats_analysis()
