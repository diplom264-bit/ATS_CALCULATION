"""Test SOTA Specialist Pipeline"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.sota_pipeline import SOTAPipeline

# Sample data
resume_text = """
Ritik Sharma
Delhi | +918109617693 | sharmaritik.1807@gmail.com

SUMMARY
Detail-oriented Power BI Developer with 2+ years of experience in designing 
scalable dashboards, optimizing ETL pipelines, and delivering actionable insights.

EXPERIENCE
Power BI Developer
Trident Information Systems Pvt. Ltd., Delhi
Feb 2023 - Present

- Built real-time dashboards in Power BI Service
- Developed SQL and DAX-based financial dashboards
- Implemented Row-Level Security (RLS)

EDUCATION
PGDM – Business Analytics & Marketing
Lloyd Business School, Greater Noida
2021 – 2023

SKILLS
Power BI Desktop, SQL (T-SQL), ETL Automation, Data Modeling, DAX, 
Data Warehousing, Microsoft Dynamics 365
"""

jd_text = """
Position: BI Developer
Experience: 2-4 years
Location: Jodhpur, Rajasthan

We are seeking a BI Developer with expertise in Power BI, SQL, and ETL processes.

Required Skills:
- Power BI, Tableau, Qlik
- SQL, OLAP, OLTP, SSAS
- ETL tools and processes
- Data modeling and warehousing

Responsibilities:
- Create and implement BI software and systems
- Develop dashboards and visualizations
- Build and maintain data models
"""

jd_skills = ["Power BI", "Tableau", "Qlik", "SQL", "OLAP", "OLTP", "SSAS", "ETL", "Data Modeling"]

print("="*80)
print("SOTA SPECIALIST PIPELINE TEST")
print("="*80)

# Initialize pipeline
pipeline = SOTAPipeline()

# Run analysis
print("\n" + "="*80)
print("ANALYZING RESUME")
print("="*80)

result = pipeline.analyze(resume_text, jd_text, jd_skills)

# Display results
print(f"\n📊 FINAL SCORE: {result['final_score']}/100 (Grade: {result['grade']})")

print(f"\n📈 FACTOR BREAKDOWN:")
for factor, data in result['breakdown'].items():
    score_pct = data['score'] * 100
    print(f"   {factor:20s}: {score_pct:5.1f}% (weight: {data['weight']*100:.0f}%) → {data['contribution']:.1f} points")

print(f"\n✅ MATCHED SKILLS:")
matched = set(s.lower() for s in result['structured_data']['skills']) & set(s.lower() for s in jd_skills)
for skill in matched:
    print(f"   • {skill}")

print(f"\n❌ MISSING SKILLS ({len(result['missing_skills'])}):")
for skill in result['missing_skills'][:5]:
    print(f"   • {skill}")

print(f"\n💡 FEEDBACK:")
for i, tip in enumerate(result['feedback'], 1):
    print(f"   {i}. {tip}")

print(f"\n⏱️ TIMING:")
for component, time_taken in result['timing'].items():
    print(f"   {component:25s}: {time_taken:.3f}s")
print(f"   {'TOTAL':25s}: {result['total_time']:.3f}s")

print("\n" + "="*80)
print("✅ SOTA PIPELINE TEST COMPLETE")
print("="*80)
