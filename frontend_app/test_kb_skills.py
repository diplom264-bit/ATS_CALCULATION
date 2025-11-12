"""Test what KB returns for skill extraction"""
import sys
sys.path.insert(0, 'd:/ATSsys/version_4')

from app.services.kb_singleton import get_kb_instance

text = """
Technical Skills: Python, Django, HTML, CSS, JavaScript, Bootstrap, Aws, GitHub
Technologies Used: Python, Django, Html, Css, Js, Redis, celery
"""

kb = get_kb_instance()

print("Testing KB skill extraction...")
print("="*80)

# Test with different thresholds
for threshold in [0.2, 0.3, 0.4, 0.5]:
    print(f"\nThreshold: {threshold}")
    results = kb.extract_skills(text, top_k=20, threshold=threshold)
    print(f"Found {len(results)} skills:")
    for r in results[:10]:
        print(f"  - {r['label']} (score: {r['score']:.3f}, type: {r.get('type', 'N/A')})")
