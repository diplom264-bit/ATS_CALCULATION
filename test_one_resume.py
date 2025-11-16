"""Quick test of one resume"""
import requests
import json
from pathlib import Path

JD_PATH = r"C:\Users\Owner\Downloads\ATL .Net + Angular 6-8 yrs.docx"
RESUME_PATH = r"C:\Users\Owner\Downloads\BobbySingh_Dot Net Angular Developer.pdf"

# Read JD
from docx import Document
doc = Document(JD_PATH)
jd_text = '\n'.join([p.text for p in doc.paragraphs if p.text.strip()])

print(f"JD length: {len(jd_text)} chars")
print(f"Resume: {Path(RESUME_PATH).name}")

# Test
with open(RESUME_PATH, 'rb') as f:
    response = requests.post(
        "http://localhost:8008/api/analyze",
        files={'resume_file': f},
        data={'jd_text': jd_text, 'resume_data': '{}'},
        timeout=60
    )

print(f"\nStatus: {response.status_code}")
result = response.json()
print(f"\nResponse keys: {list(result.keys())}")

if result.get('status') == 'ok':
    data = result.get('data', {})
    print(f"Data keys: {list(data.keys())}")
    
    analysis = data.get('analysis', {})
    print(f"Analysis keys: {list(analysis.keys())}")
    print(f"\nFinal Score: {analysis.get('final_score')}")
    print(f"Grade: {analysis.get('grade')}")
    print(f"Breakdown: {analysis.get('breakdown')}")
    print(f"\nSemantic Score: {data.get('semantic_score')}")
    print(f"ML Score: {data.get('ml_score')}")
    print(f"\nSkill Match: {data.get('skill_match_details')}")
else:
    print(f"Error: {result.get('error')}")

print(f"\n=== FULL RESPONSE ===\n{json.dumps(result, indent=2)[:2000]}...")
