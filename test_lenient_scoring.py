"""Test lenient scoring fixes"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.checkers.readability_checker import ReadabilityChecker
from app.services.checkers.impact_checker import ImpactChecker
from app.services.checkers.jd_alignment_checker import JDAlignmentChecker

print("="*80)
print("LENIENT SCORING TEST")
print("="*80)

# Test readability
print("\n1. READABILITY CHECK")
print("-" * 80)
checker = ReadabilityChecker()
text = "I am a software developer with experience in Python and Django. I have worked on multiple projects."
score, feedback = checker.check_readability(text)
print(f"Score: {score}/10")
print(f"Expected: 7-10 (was getting 5)")

# Test professional language
print("\n2. PROFESSIONAL LANGUAGE CHECK")
print("-" * 80)
bullets = [
    "Developed web applications using Django",
    "Worked with PostgreSQL databases",
    "Created REST APIs for mobile apps"
]
score, feedback = checker.check_professional_language(text, bullets)
print(f"Score: {score}/10")
print(f"Feedback: {feedback}")
print(f"Expected: 7-8 (was getting 4)")

# Test quantified impact
print("\n3. QUANTIFIED IMPACT CHECK")
print("-" * 80)
impact_checker = ImpactChecker()
experience = "Developed web applications using Django and Python. Created REST APIs. Worked with PostgreSQL databases."
score, feedback = impact_checker.check_quantified_achievements(experience)
print(f"Score: {score}/10")
print(f"Feedback: {feedback}")
print(f"Expected: 5 (was getting 0)")

# Test skill context
print("\n4. SKILL CONTEXT CHECK")
print("-" * 80)
jd_checker = JDAlignmentChecker(use_kb=False)
skills = ['Python', 'Django', 'PostgreSQL']
experience = "Developed web applications using Django and Python. Worked with PostgreSQL databases."
score, feedback = jd_checker.check_skill_context(skills, experience)
print(f"Score: {score}/5")
print(f"Feedback: {feedback}")
print(f"Expected: 3.5-5 (was getting 1.94)")

print("\n" + "="*80)
print("RESULT:")
print("If all scores improved, the fix is working!")
print("="*80)
