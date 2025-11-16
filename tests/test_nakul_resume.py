import sys
sys.path.insert(0, 'D:/ATSsys/version_4')

from app.services.file_parser import FileParser
from app.services.production_ner_extractor import ProductionNERExtractor
from app.services.data_adapter import DataAdapter
from app.services.perfect_analysis_engine import PerfectAnalysisEngine

# Parse resume
print("Parsing Nakul's resume...")
result = FileParser.parse(r"C:\Users\Owner\Downloads\Nakul_Saraswat_Resume 1 (1).pdf")
text = result.get('text', '')

# Extract entities
print("\nExtracting entities...")
extractor = ProductionNERExtractor()
entities = extractor.extract(text)

print(f"\n{'='*80}")
print("EXTRACTED ENTITIES")
print(f"{'='*80}")
print(f"Name: {entities['name']}")
print(f"Email: {entities['email']}")
print(f"Phone: {entities['phone']}")
print(f"LinkedIn: {entities['linkedin']}")

print(f"\nCompanies ({len(entities['companies'])}):")
for c in entities['companies']:
    print(f"  - {c}")

print(f"\nJob Titles ({len(entities['job_titles'])}):")
for t in entities['job_titles']:
    print(f"  - {t}")

print(f"\nSkills ({len(entities['skills'])}):")
for s in entities['skills'][:15]:
    print(f"  - {s}")

print(f"\nDegrees ({len(entities['degrees'])}):")
for d in entities['degrees']:
    print(f"  - {d}")

# Analyze with JD
jd = """
Power BI Developer
We are seeking a skilled Power BI Developer to design and develop interactive dashboards and reports. 
The ideal candidate will have strong experience with Power BI, DAX, SQL, and data modeling.

Key Responsibilities:
- Design and develop Power BI dashboards and reports
- Write complex DAX queries and measures
- Optimize data models for performance
- Collaborate with stakeholders to gather requirements
- Implement row-level security

Required Skills:
- Power BI Desktop and Service
- DAX and M Query
- SQL Server
- Data modeling and ETL
- Excel and data visualization
"""

print(f"\n{'='*80}")
print("ANALYSIS RESULTS")
print(f"{'='*80}")

# Convert to analysis format
analysis_data = DataAdapter.adapt_ner_to_analysis(entities, text)

# Analyze
engine = PerfectAnalysisEngine()
analysis = engine.analyze(analysis_data, jd)

print(f"\nFinal Score: {analysis['final_score']:.1f}/100")
print(f"Grade: {analysis['grade']}")

print(f"\nScore Breakdown:")
for check in analysis['checks']:
    print(f"  {check['name']}: {check['score']:.1f}/{check['max_score']}")

print(f"\nTop Issues:")
for issue in analysis['recommendations'][:5]:
    print(f"  - {issue}")
