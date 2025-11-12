"""Debug extraction for specific resume"""
import sys
sys.path.insert(0, 'd:/ATSsys/version_4')

from app.services.final_resume_parser import FinalResumeParser
import fitz

resume_path = r"C:\Users\Owner\Downloads\Naukri_NikharJain[4y_6m] 1  python cv.pdf"

print("="*80)
print("DEBUGGING RESUME EXTRACTION")
print("="*80)

# Parse
parser = FinalResumeParser()
result = parser.parse(resume_path)

print("\nRaw Extraction:")
print(f"Name: {result['name']}")
print(f"Email: {result['email']}")
print(f"Phone: {result['phone']}")
print(f"Skills: {result['skills']}")
print(f"Companies: {result['companies']}")
print(f"Titles: {result['job_titles']}")
print(f"Degrees: {result['degrees']}")

# Check preprocessed text
print("\n" + "="*80)
print("PREPROCESSED TEXT (first 2000 chars)")
print("="*80)
preprocessed = parser.preprocessor.process(resume_path)
text = preprocessed.get('clean_text', '')
print(text[:2000])

# Check sections
print("\n" + "="*80)
print("DETECTED SECTIONS")
print("="*80)
sections = preprocessed.get('sections', [])
for section in sections[:10]:
    print(f"- {section['header']} (confidence: {section['confidence']:.2f})")

# Extract skills manually from text
print("\n" + "="*80)
print("MANUAL SKILL SEARCH")
print("="*80)
common_skills = ['python', 'django', 'flask', 'sql', 'mysql', 'postgresql', 'mongodb', 
                 'aws', 'docker', 'kubernetes', 'git', 'rest', 'api', 'fastapi',
                 'pandas', 'numpy', 'tensorflow', 'pytorch', 'opencv', 'nlp']

text_lower = text.lower()
found_skills = [skill for skill in common_skills if skill in text_lower]
print(f"Found skills in text: {found_skills}")
