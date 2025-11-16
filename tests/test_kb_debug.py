"""Debug KB integration"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.checkers.jd_alignment_checker import JDAlignmentChecker

print("Initializing checker...")
checker = JDAlignmentChecker(use_kb=True)

print(f"\nKB loaded: {checker.kb is not None}")
print(f"Use KB: {checker.use_kb}")

if checker.kb:
    print("\n✅ KB is available!")
    print(f"KB entries: {len(checker.kb.entries):,}")
    
    # Test skill extraction
    test_text = "Python programming and SQL database"
    skills = checker.kb.extract_skills(test_text, top_k=5)
    print(f"\nTest skill extraction:")
    for s in skills:
        print(f"  - {s['label']} (score: {s['score']:.3f})")
else:
    print("\n❌ KB not loaded - using fallback")
