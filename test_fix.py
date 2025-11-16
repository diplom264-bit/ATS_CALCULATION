"""Quick test to verify scoring fix"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.ml_core.adaptive_scorer import AdaptiveScorer

# Simulate two different raw analyses from PerfectAnalysisEngine
scorer = AdaptiveScorer()

# GOOD RESUME - high scores
good_raw = {
    'final_score': 85.5,  # Already weighted by PerfectAnalysisEngine
    'grade': 'B',
    'breakdown': {
        'file_layout': 18.0,      # out of 20
        'font_consistency': 9.0,   # out of 10
        'readability': 8.5,        # out of 10
        'professional_language': 8.0,  # out of 10
        'date_consistency': 5.0,   # out of 5
        'employment_gaps': 9.0,    # out of 10
        'career_progression': 4.5, # out of 5
        'keyword_alignment': 12.0, # out of 15
        'skill_context': 4.0,      # out of 5
        'semantic_fit': 16.0,      # out of 20
        'quantified_impact': 8.0,  # out of 10
        'online_presence': 5.0     # out of 5
    },
    'feedback': [],
    'total_checks': 12
}

# BAD RESUME - low scores
bad_raw = {
    'final_score': 42.3,  # Already weighted by PerfectAnalysisEngine
    'grade': 'F',
    'breakdown': {
        'file_layout': 12.0,       # out of 20
        'font_consistency': 6.0,   # out of 10
        'readability': 5.0,        # out of 10
        'professional_language': 4.0,  # out of 10
        'date_consistency': 3.0,   # out of 5
        'employment_gaps': 5.0,    # out of 10
        'career_progression': 2.0, # out of 5
        'keyword_alignment': 4.0,  # out of 15
        'skill_context': 1.5,      # out of 5
        'semantic_fit': 6.0,       # out of 20
        'quantified_impact': 2.0,  # out of 10
        'online_presence': 2.0     # out of 5
    },
    'feedback': [],
    'total_checks': 12
}

mock_data = {
    'email': 'test@test.com',
    'phone': '1234567890',
    'skills': ['Python', 'Django', 'SQL'],
    'work_history': [{'title': 'Developer'}],
    'degrees': ['BS Computer Science']
}

print("="*80)
print("SCORING FIX VERIFICATION")
print("="*80)

print("\nGOOD RESUME:")
print(f"  Raw Final Score (from PerfectAnalysisEngine): {good_raw['final_score']}")
enhanced_good = scorer.enhance_analysis(good_raw, mock_data)
print(f"  Enhanced Final Score (after AdaptiveScorer): {enhanced_good['final_score']}")
print(f"  Grade: {enhanced_good['grade']}")
print(f"  Should be: ~85 (Grade B)")

print("\nBAD RESUME:")
print(f"  Raw Final Score (from PerfectAnalysisEngine): {bad_raw['final_score']}")
enhanced_bad = scorer.enhance_analysis(bad_raw, mock_data)
print(f"  Enhanced Final Score (after AdaptiveScorer): {enhanced_bad['final_score']}")
print(f"  Grade: {enhanced_bad['grade']}")
print(f"  Should be: ~42 (Grade F)")

print("\n" + "="*80)
print("RESULT:")
if abs(enhanced_good['final_score'] - good_raw['final_score']) < 1 and \
   abs(enhanced_bad['final_score'] - bad_raw['final_score']) < 1:
    print("✅ FIX SUCCESSFUL - Scores preserved correctly!")
    print("   Good resume stays high, bad resume stays low")
else:
    print("❌ ISSUE REMAINS - Scores are being modified incorrectly")
print("="*80)
