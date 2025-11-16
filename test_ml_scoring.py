"""Test ML Scoring (Layer 5)"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.ml_core.ml_scorer import get_ml_scorer

print("="*80)
print("ML SCORING TEST (Layer 5)")
print("="*80)

# Initialize
print("\n1. Loading ML scorer...")
scorer = get_ml_scorer()

# Test cases
test_cases = [
    ("Power BI Developer with DAX", 
     "Created dashboards using Power BI and DAX", 
     "Expected: 85-95"),
    
    (".NET Developer with C#", 
     "Power BI Developer with DAX", 
     "Expected: 20-40"),
    
    ("Python Data Scientist", 
     "Data analyst with Python and pandas", 
     "Expected: 70-85"),
]

print("\n2. Testing ML scoring...")
print("-" * 80)

for jd, resume, expected in test_cases:
    score, explanation = scorer.ml_score(resume, jd)
    print(f"\nJD: {jd}")
    print(f"Resume: {resume}")
    print(f"Score: {score:.1f}/100")
    print(f"Explanation: {explanation}")
    print(f"{expected}")

# Test with trained model if available
model_path = Path(__file__).parent / "models" / "ml_ranker.txt"
if model_path.exists():
    print("\n3. Testing with trained LightGBM model...")
    print("-" * 80)
    scorer.load_trained_model(str(model_path))
    
    for jd, resume, expected in test_cases:
        score, explanation = scorer.ml_score(resume, jd)
        print(f"\nJD: {jd}")
        print(f"Score (with LightGBM): {score:.1f}/100")
        print(f"{expected}")
else:
    print("\n⚠️  No trained model found. Run: python train_ml_model.py")

print("\n" + "="*80)
print("ML SCORING TEST COMPLETE")
print("="*80)
