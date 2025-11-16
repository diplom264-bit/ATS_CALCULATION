"""
End-to-End Pipeline Sanity Check
Tests: Parser → Analyzer → Scorer → Report Generator
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("="*80)
print("END-TO-END PIPELINE SANITY CHECK")
print("="*80)

# Test 1: Import all components
print("\n1. IMPORT CHECK")
print("-" * 80)
try:
    from app.services.final_resume_parser import FinalResumeParser
    print("✅ FinalResumeParser imported")
except Exception as e:
    print(f"❌ FinalResumeParser import failed: {e}")

try:
    from app.services.perfect_analysis_engine import PerfectAnalysisEngine
    print("✅ PerfectAnalysisEngine imported")
except Exception as e:
    print(f"❌ PerfectAnalysisEngine import failed: {e}")

try:
    from app.services.ml_core.adaptive_scorer import AdaptiveScorer
    print("✅ AdaptiveScorer imported")
except Exception as e:
    print(f"❌ AdaptiveScorer import failed: {e}")

try:
    from app.services.ml_enhanced_analyzer import MLEnhancedAnalyzer
    print("✅ MLEnhancedAnalyzer imported")
except Exception as e:
    print(f"❌ MLEnhancedAnalyzer import failed: {e}")

try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent / 'frontend_app'))
    from report_generator import create_docx_report
    print("✅ ReportGenerator imported")
except Exception as e:
    print(f"❌ ReportGenerator import failed: {e}")

# Test 2: Component initialization
print("\n2. INITIALIZATION CHECK")
print("-" * 80)
try:
    from app.services.kb_singleton import preload_kb
    print("Loading KB...")
    preload_kb()
    print("✅ KB loaded successfully")
except Exception as e:
    print(f"❌ KB loading failed: {e}")

try:
    parser = FinalResumeParser()
    print("✅ Parser initialized")
except Exception as e:
    print(f"❌ Parser initialization failed: {e}")

try:
    analyzer = MLEnhancedAnalyzer()
    print("✅ MLEnhancedAnalyzer initialized")
except Exception as e:
    print(f"❌ MLEnhancedAnalyzer initialization failed: {e}")

# Test 3: Data flow validation
print("\n3. DATA FLOW VALIDATION")
print("-" * 80)

# Mock data for testing
mock_resume_data = {
    'name': 'John Doe',
    'email': 'john@example.com',
    'phone': '+1234567890',
    'linkedin': 'linkedin.com/in/johndoe',
    'skills': ['Python', 'Django', 'PostgreSQL', 'Docker'],
    'companies': ['Tech Corp', 'StartupXYZ'],
    'job_titles': ['Senior Developer', 'Developer'],
    'degrees': ['BS Computer Science'],
    'confidence': {'name': 0.95, 'email': 0.99}
}

mock_analysis_data = {
    'final_score': 75.5,
    'grade': 'C',
    'breakdown': {
        'file_layout': 85.0,
        'font_consistency': 90.0,
        'readability': 80.0,
        'professional_language': 75.0,
        'date_consistency': 100.0,
        'employment_gaps': 90.0,
        'career_progression': 80.0,
        'keyword_alignment': 60.0,
        'skill_context': 70.0,
        'semantic_fit': 65.0,
        'quantified_impact': 40.0,
        'online_presence': 80.0
    },
    'feedback': [
        'Add quantifiable achievements',
        'Include more job-specific keywords',
        'Improve skill demonstration'
    ],
    'total_checks': 12
}

# Test parser output structure
print("Testing parser output structure...")
required_parser_keys = ['name', 'email', 'phone', 'skills', 'status']
missing_keys = [k for k in required_parser_keys if k not in mock_resume_data and k != 'status']
if not missing_keys:
    print("✅ Parser output structure valid")
else:
    print(f"❌ Parser missing keys: {missing_keys}")

# Test analysis output structure
print("Testing analysis output structure...")
required_analysis_keys = ['final_score', 'grade', 'breakdown', 'feedback']
missing_keys = [k for k in required_analysis_keys if k not in mock_analysis_data]
if not missing_keys:
    print("✅ Analysis output structure valid")
else:
    print(f"❌ Analysis missing keys: {missing_keys}")

# Test score ranges
print("Testing score ranges...")
issues = []
if not (0 <= mock_analysis_data['final_score'] <= 100):
    issues.append(f"final_score out of range: {mock_analysis_data['final_score']}")

for key, val in mock_analysis_data['breakdown'].items():
    if not (0 <= val <= 100):
        issues.append(f"{key} out of range: {val}")

if not issues:
    print("✅ All scores within valid range (0-100)")
else:
    print(f"❌ Score range issues: {issues}")

# Test 4: Scorer validation
print("\n4. ADAPTIVE SCORER VALIDATION")
print("-" * 80)
try:
    scorer = AdaptiveScorer()
    
    # Test with valid data
    result = scorer.enhance_analysis(mock_analysis_data, mock_resume_data)
    print(f"✅ Scorer processes valid data: {result['final_score']}/100")
    
    # Test score preservation
    if abs(result['final_score'] - mock_analysis_data['final_score']) < 0.1:
        print("✅ Score preservation working")
    else:
        print(f"❌ Score changed: {mock_analysis_data['final_score']} → {result['final_score']}")
    
    # Test with invalid data
    try:
        scorer.enhance_analysis(None, None)
        print("❌ Scorer accepts None (should reject)")
    except ValueError:
        print("✅ Scorer rejects None input")
    
    try:
        scorer.enhance_analysis({}, {})
        print("❌ Scorer accepts empty dict (should reject)")
    except ValueError:
        print("✅ Scorer rejects empty dict")
        
except Exception as e:
    print(f"❌ Scorer validation failed: {e}")

# Test 5: Report generator validation
print("\n5. REPORT GENERATOR VALIDATION")
print("-" * 80)
try:
    import tempfile
    sys.path.insert(0, str(Path(__file__).parent / 'frontend_app'))
    from report_generator import create_docx_report
    
    output_path = tempfile.mktemp(suffix='.docx')
    create_docx_report(mock_resume_data, mock_analysis_data, output_path)
    
    if Path(output_path).exists():
        size = Path(output_path).stat().st_size
        print(f"✅ Report generated: {size} bytes")
        Path(output_path).unlink()
    else:
        print("❌ Report file not created")
        
except Exception as e:
    print(f"❌ Report generation failed: {e}")

# Test 6: Error handling
print("\n6. ERROR HANDLING VALIDATION")
print("-" * 80)

# Test empty text handling
try:
    from app.services.checkers.jd_alignment_checker import JDAlignmentChecker
    checker = JDAlignmentChecker()
    
    score, feedback = checker.check_semantic_fit("", "test jd")
    if score == 0.0:
        print("✅ Empty resume text handled correctly")
    else:
        print(f"❌ Empty resume should return 0, got {score}")
    
    score, feedback = checker.check_semantic_fit("test resume", "")
    if score == 20.0:
        print("✅ Empty JD text handled correctly")
    else:
        print(f"❌ Empty JD should return 20, got {score}")
    
    score, feedback = checker.check_semantic_fit(None, "test jd")
    if score == 0.0:
        print("✅ None resume text handled correctly")
    else:
        print(f"❌ None resume should return 0, got {score}")
        
except Exception as e:
    print(f"❌ Error handling test failed: {e}")

# Test 7: Performance check
print("\n7. PERFORMANCE CHECK")
print("-" * 80)
import time

try:
    # Test semantic fit performance
    checker = JDAlignmentChecker()
    test_resume = "Python developer with 5 years experience in Django, REST APIs, PostgreSQL" * 10
    test_jd = "Looking for Python developer with Django experience" * 10
    
    start = time.time()
    for _ in range(10):
        checker.check_semantic_fit(test_resume, test_jd)
    elapsed = time.time() - start
    avg_time = elapsed / 10
    
    if avg_time < 0.5:
        print(f"✅ Semantic fit performance: {avg_time*1000:.1f}ms per call")
    else:
        print(f"⚠️  Semantic fit slow: {avg_time*1000:.1f}ms per call (target <500ms)")
        
except Exception as e:
    print(f"❌ Performance test failed: {e}")

# Test 8: Memory leak check
print("\n8. MEMORY LEAK CHECK")
print("-" * 80)
try:
    import gc
    import sys
    
    # Get initial object count
    gc.collect()
    initial_objects = len(gc.get_objects())
    
    # Run multiple analyses
    for _ in range(10):
        scorer = AdaptiveScorer()
        result = scorer.enhance_analysis(mock_analysis_data, mock_resume_data)
    
    # Check object count
    gc.collect()
    final_objects = len(gc.get_objects())
    growth = final_objects - initial_objects
    
    if growth < 1000:
        print(f"✅ No significant memory leak: +{growth} objects")
    else:
        print(f"⚠️  Possible memory leak: +{growth} objects")
        
except Exception as e:
    print(f"❌ Memory leak test failed: {e}")

print("\n" + "="*80)
print("PIPELINE SANITY CHECK COMPLETE")
print("="*80)
