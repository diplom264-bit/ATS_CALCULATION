"""Quick test for skill matching improvements"""
from app.services.smart_skill_matcher import SmartSkillMatcher

matcher = SmartSkillMatcher()

# Test cases
tests = [
    {
        "name": "Python variations",
        "resume": ["Python", "SQL", "Data Analysis"],
        "jd": ["Python programming", "MySQL", "Data Analytics"]
    },
    {
        "name": "Power BI variations",
        "resume": ["Power BI", "Excel", "Tableau"],
        "jd": ["PowerBI", "Microsoft Excel", "Tableau Desktop"]
    },
    {
        "name": "Partial matches",
        "resume": ["Machine Learning", "Deep Learning"],
        "jd": ["ML", "Neural Networks"]
    }
]

print("=" * 60)
print("Skill Matching Improvement Tests")
print("=" * 60)

for test in tests:
    print(f"\n{test['name']}:")
    print(f"  Resume: {test['resume']}")
    print(f"  JD: {test['jd']}")
    
    matched, missing, pct = matcher.match_skills(test['resume'], test['jd'])
    
    print(f"  ✅ Matched: {matched}")
    print(f"  ❌ Missing: {missing}")
    print(f"  📊 Score: {pct:.1f}%")

print("\n" + "=" * 60)
print("✅ Tests complete!")
print("=" * 60)
