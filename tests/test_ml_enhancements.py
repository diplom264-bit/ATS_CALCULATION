"""
Test ML Enhancements
Validates embedding engine, feature fusion, and feedback generation
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.ml_enhanced_analyzer import MLEnhancedAnalyzer

def test_ml_analyzer():
    """Test complete ML-enhanced pipeline"""
    
    print("=" * 80)
    print("ML-ENHANCED ANALYZER TEST (KB Pre-loaded)")
    print("=" * 80)
    
    analyzer = MLEnhancedAnalyzer()
    
    # Test resume (use actual path from test_harness)
    resume_path = r"C:\Users\Owner\Downloads\RitikSharma_BI Developer.pdf"
    
    # Test JD
    jd_text = """
    Power BI Developer
    
    Required Skills:
    - Power BI, DAX, Power Query
    - SQL Server, Azure
    - Data visualization and dashboard development
    - ETL processes
    - Python for data analysis
    
    Experience:
    - 2+ years in BI development
    - Strong analytical skills
    - Experience with cloud platforms
    """
    
    print("\n1. Running ML-Enhanced Analysis...")
    result = analyzer.analyze(resume_path, jd_text)
    
    if result['status'] != 'ok':
        print(f"❌ Analysis failed: {result.get('error')}")
        return
    
    print("✅ Analysis completed successfully")
    
    # Display results
    print("\n" + "=" * 80)
    print("EXTRACTION RESULTS")
    print("=" * 80)
    extraction = result['extraction']
    print(f"Name: {extraction['name']}")
    print(f"Email: {extraction['email']}")
    print(f"Phone: {extraction['phone']}")
    print(f"Skills: {len(extraction['skills'])} found")
    print(f"Companies: {len(extraction['companies'])} found")
    print(f"Degrees: {len(extraction['degrees'])} found")
    
    # ML Features
    print("\n" + "=" * 80)
    print("ML FEATURES")
    print("=" * 80)
    ml_features = result['ml_features']
    print(f"Embedding Dimension: {ml_features['embedding_dim']}")
    print(f"Rule Features: {ml_features['rule_features_dim']}")
    print(f"Total Features: {ml_features['total_features']}")
    
    # Analysis scores
    if 'analysis' in result:
        print("\n" + "=" * 80)
        print("ANALYSIS SCORES")
        print("=" * 80)
        analysis = result['analysis']
        print(f"Final Score: {analysis['final_score']}/100")
        print(f"Grade: {analysis['grade']}")
        print(f"Semantic Similarity: {result['semantic_score']}/100")
        print(f"Total Checks: {analysis['total_checks']}")
        
        print("\nScore Breakdown:")
        for check, score in analysis['breakdown'].items():
            print(f"  {check}: {score:.1f}")
    
    # Enhanced feedback
    if 'enhanced_feedback' in result:
        print("\n" + "=" * 80)
        print("ENHANCED FEEDBACK")
        print("=" * 80)
        print(f"\n{result['summary']}\n")
        print("Top Recommendations:")
        for i, feedback in enumerate(result['enhanced_feedback'], 1):
            print(f"{i}. {feedback}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    # Preload KB once
    from app.startup import initialize_app
    initialize_app()
    
    test_ml_analyzer()
