"""Test role recommender"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'app'))

from services.role_recommender import get_role_recommender

recommender = get_role_recommender()

# Test with data analyst skills
skills = ["Python", "SQL", "Excel", "statistics", "data analysis", "pandas"]

print("="*70)
print("ROLE RECOMMENDATIONS")
print("="*70)
print(f"\nResume Skills: {', '.join(skills)}\n")

roles = recommender.recommend_roles(skills, top_n=5)

for i, role in enumerate(roles, 1):
    print(f"{i}. {role['role']}")
    print(f"   Score: {role['score']}%")
    print(f"   Essential Coverage: {role['essential_coverage']}%")
    print(f"   Optional Coverage: {role['optional_coverage']}%")
    print(f"   Matched: {', '.join(role['matched_skills'][:3])}")
    print()
