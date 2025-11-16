"""Test role mismatch detection"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.checkers.jd_alignment_checker import JDAlignmentChecker
from app.services.kb_singleton import preload_kb

print("Loading KB...")
preload_kb()

checker = JDAlignmentChecker()

# Power BI Developer JD
powerbi_jd = """
Power BI Developer
We need a Power BI Developer with 3+ years experience in:
- Power BI Desktop and Power BI Service
- DAX, Power Query, M language
- Data modeling and ETL
- SQL Server, SSAS, SSRS
- Creating dashboards and reports
- Row-level security (RLS)
"""

# .NET Developer Resume (WRONG FIT)
dotnet_resume = """
Senior .NET Developer
5 years experience in C#, ASP.NET Core, MVC, Web API
Skills: C#, .NET Framework, Entity Framework, SQL Server, Azure
Built enterprise applications using microservices architecture
Experience with REST APIs, Docker, CI/CD pipelines
"""

# Power BI Developer Resume (GOOD FIT)
powerbi_resume = """
Power BI Developer
3 years experience creating interactive dashboards
Skills: Power BI Desktop, DAX, Power Query, SQL Server, SSAS
Built 50+ reports with advanced data modeling
Expert in ETL processes and data visualization
Implemented row-level security for enterprise clients
"""

print("\n" + "="*80)
print("ROLE MISMATCH TEST")
print("="*80)

print("\n1. WRONG FIT: .NET Developer → Power BI JD")
print("-" * 80)
score1, feedback1 = checker.check_semantic_fit(dotnet_resume, powerbi_jd)
print(f"Semantic Fit Score: {score1:.1f}/20")
print(f"Feedback: {feedback1}")
print(f"Expected: <5/20 (Critical mismatch)")

print("\n2. GOOD FIT: Power BI Developer → Power BI JD")
print("-" * 80)
score2, feedback2 = checker.check_semantic_fit(powerbi_resume, powerbi_jd)
print(f"Semantic Fit Score: {score2:.1f}/20")
print(f"Feedback: {feedback2}")
print(f"Expected: >15/20 (Strong match)")

print("\n" + "="*80)
print("RESULT:")
if score1 < 5 and score2 > 15:
    print("✅ ROLE VALIDATION WORKING - Mismatched roles properly rejected!")
elif score1 < 10:
    print("⚠️  PARTIAL - Mismatch detected but could be stricter")
else:
    print("❌ ISSUE - .NET developer scoring too high for Power BI role")
print("="*80)
