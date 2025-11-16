"""Test with actual JD and Resume files"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.file_parser import FileParser
from app.services.production_ner_extractor import ProductionNERExtractor
from app.services.perfect_analysis_engine import PerfectAnalysisEngine
from app.services.data_adapter import DataAdapter

# File paths
resume_path = r"C:\Users\Owner\Downloads\RitikSharma_BI Developer.pdf"
jd_path = r"C:\Users\Owner\Downloads\JD- BI Developer 2 to 4 years.docx"

print("=" * 80)
print("REAL JD + RESUME TEST")
print("=" * 80)

# Parse files
print("\n1️⃣ Parsing files...")
resume_result = FileParser.parse(resume_path)
resume_text = resume_result.get('text', '')
print(f"✅ Resume: {len(resume_text)} chars")

jd_result = FileParser.parse(jd_path)
jd_text = jd_result.get('text', '')
print(f"✅ JD: {len(jd_text)} chars")

# Extract entities
print("\n2️⃣ Extracting entities...")
extractor = ProductionNERExtractor()
entities = extractor.extract(resume_text)
print(f"✅ Skills: {len(entities['skills'])}, Companies: {len(entities['companies'])}")

# Adapt data
parsed_data = DataAdapter.adapt_ner_to_analysis(entities, resume_text)

# Run analysis
print("\n3️⃣ Running KB-enhanced analysis...")
engine = PerfectAnalysisEngine()
result = engine.analyze(resume_path, resume_text, jd_text, parsed_data)

print("\n" + "=" * 80)
print("RESULTS")
print("=" * 80)

print(f"\n📊 FINAL SCORE: {result['final_score']}/100")
print(f"🎓 GRADE: {result['grade']}")

print("\n📈 KEY SCORES:")
print(f"  Keyword Alignment  : {result['breakdown']['keyword_alignment']:.1f}/15")
print(f"  Semantic Fit (KB)  : {result['breakdown']['semantic_fit']:.1f}/20")
print(f"  Skill Context      : {result['breakdown']['skill_context']:.1f}/5")
print(f"  File Layout        : {result['breakdown']['file_layout']:.1f}/20")
print(f"  Career Progression : {result['breakdown']['career_progression']:.1f}/5")

print("\n💡 TOP FEEDBACK:")
for i, msg in enumerate(result['feedback'][:10], 1):
    print(f"  {i}. {msg}")

print("\n✅ Test complete!")
