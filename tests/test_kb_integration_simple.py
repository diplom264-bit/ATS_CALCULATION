"""Simple KB integration test for semantic matching"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.checkers.jd_alignment_checker import JDAlignmentChecker

print("=" * 60)
print("KB INTEGRATION TEST - Semantic Matching")
print("=" * 60)

# Sample resume and JD
resume_text = """
Ritik Sharma
BI Developer

Skills:
- Power BI
- Tableau
- SQL
- Python
- Data Analysis

Experience:
Worked on data visualization projects using Power BI and Tableau.
Developed SQL queries for data extraction and analysis.
"""

jd_text = """
Senior BI Developer

Required Skills:
- Power BI and Tableau for data visualization
- SQL and Python for data analysis
- Data warehousing and ETL processes
- Cloud platforms (Azure, AWS)

Requirements:
- 5+ years of experience in BI development
- Strong analytical and problem-solving skills
"""

print("\n1️⃣ Initializing JD Alignment Checker...")
checker = JDAlignmentChecker(use_kb=True)

print("\n2️⃣ Running semantic fit check...")
score, feedback = checker.check_semantic_fit(resume_text, jd_text)

print("\n" + "=" * 60)
print("RESULTS")
print("=" * 60)
print(f"\n📊 Semantic Fit Score: {score:.1f}/20")
print(f"📈 Percentage: {(score/20)*100:.1f}%")

print("\n💡 Feedback:")
for i, msg in enumerate(feedback, 1):
    print(f"  {i}. {msg}")

print("\n✅ Test complete!")
