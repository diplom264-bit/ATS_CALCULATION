"""
Test Perfect Analysis Engine
Complete modular checker system
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.file_parser import FileParser
from app.services.production_ner_extractor import ProductionNERExtractor
from app.services.perfect_analysis_engine import PerfectAnalysisEngine
from app.services.data_adapter import DataAdapter

def test_perfect_analysis():
    """Test complete perfect analysis engine"""
    
    resume_path = Path(r"C:\Users\Owner\Downloads\RitikSharma_BI Developer.pdf")
    
    if not resume_path.exists():
        print(f"❌ Test resume not found: {resume_path}")
        return
    
    print("=" * 80)
    print("PERFECT ANALYSIS ENGINE TEST")
    print("=" * 80)
    
    # Parse resume
    print("\n1️⃣ Parsing resume...")
    parse_result = FileParser.parse(str(resume_path))
    resume_text = parse_result.get('text', '')
    print(f"✅ Extracted {len(resume_text)} characters")
    
    # Extract entities
    print("\n2️⃣ Extracting entities...")
    extractor = ProductionNERExtractor()
    entities = extractor.extract(resume_text)
    print(f"✅ Extracted {len(entities['skills'])} skills, {len(entities['companies'])} companies")
    
    # Adapt data
    print("\n3️⃣ Adapting data...")
    parsed_data = DataAdapter.adapt_ner_to_analysis(entities, resume_text)
    print(f"✅ Prepared {len(parsed_data)} data fields")
    
    # Run analysis
    print("\n4️⃣ Running perfect analysis...")
    engine = PerfectAnalysisEngine()
    
    # Test without JD
    result = engine.analyze(
        str(resume_path),
        resume_text,
        None,
        parsed_data
    )
    
    print("\n" + "=" * 80)
    print("ANALYSIS RESULTS (No JD)")
    print("=" * 80)
    
    print(f"\n📊 FINAL SCORE: {result['final_score']}/100")
    print(f"🎓 GRADE: {result['grade']}")
    print(f"✅ TOTAL CHECKS: {result['total_checks']}")
    
    print("\n📈 DETAILED BREAKDOWN:")
    for check, score in result['breakdown'].items():
        print(f"  {check:25} : {score:5.1f} points")
    
    print("\n💡 FEEDBACK:")
    for i, feedback in enumerate(result['feedback'], 1):
        print(f"  {i}. {feedback}")
    
    # Test with JD
    print("\n" + "=" * 80)
    print("5️⃣ Testing with Job Description...")
    print("=" * 80)
    
    sample_jd = """
    Senior BI Developer
    
    We are seeking an experienced BI Developer with strong skills in:
    - Power BI and Tableau for data visualization
    - SQL and Python for data analysis
    - Data warehousing and ETL processes
    - Cloud platforms (Azure, AWS)
    
    Requirements:
    - 5+ years of experience in BI development
    - Strong analytical and problem-solving skills
    - Proven track record of delivering data-driven insights
    - Experience with large-scale data projects
    
    Responsibilities:
    - Design and develop BI dashboards
    - Optimize data pipelines and ETL processes
    - Collaborate with stakeholders to understand requirements
    - Mentor junior team members
    """
    
    result_with_jd = engine.analyze(
        str(resume_path),
        resume_text,
        sample_jd,
        parsed_data
    )
    
    print(f"\n📊 FINAL SCORE (with JD): {result_with_jd['final_score']}/100")
    print(f"🎓 GRADE: {result_with_jd['grade']}")
    
    print("\n📈 KEY SCORES:")
    print(f"  Keyword Alignment  : {result_with_jd['breakdown']['keyword_alignment']:.1f}/15")
    print(f"  Semantic Fit       : {result_with_jd['breakdown']['semantic_fit']:.1f}/20")
    print(f"  Skill Context      : {result_with_jd['breakdown']['skill_context']:.1f}/5")
    
    print("\n💡 JD-SPECIFIC FEEDBACK:")
    jd_feedback = [f for f in result_with_jd['feedback'] if any(kw in f.lower() for kw in ['keyword', 'match', 'semantic', 'skill'])]
    for i, feedback in enumerate(jd_feedback, 1):
        print(f"  {i}. {feedback}")
    
    print("\n✅ Perfect Analysis Engine test complete!")
    print("=" * 80)

if __name__ == "__main__":
    test_perfect_analysis()
