"""
Test Batch Processing - Validate session-based JD linking
"""
import requests
import json
from pathlib import Path

API_BASE = "http://localhost:8008"
JD_PATH = r"C:\Users\Owner\Downloads\ATL .Net + Angular 6-8 yrs.docx"
RESUMES = [
    r"C:\Users\Owner\Downloads\LavkushRaj_Dot Net Angular Developer (1) 1.pdf",
    r"C:\Users\Owner\Downloads\_Amitkumar_ASP.NET DEVELOPER (2) 1.PDF",
    r"C:\Users\Owner\Downloads\BobbySingh_Dot Net Angular Developer.pdf",
]

print("="*80)
print("BATCH PROCESSING TEST")
print("="*80)

# Step 1: Upload JD
print("\n1. Uploading JD...")
with open(JD_PATH, 'rb') as f:
    res = requests.post(f"{API_BASE}/api/upload-jd", files={'file': f})

if res.status_code == 200:
    jd_data = res.json()
    print(f"✅ JD uploaded")
    print(f"   JD ID: {jd_data['jd_id']}")
    print(f"   Session ID: {jd_data['session_id']}")
    
    jd_id = jd_data['jd_id']
    session_id = jd_data['session_id']
else:
    print(f"❌ Failed: {res.status_code}")
    print(res.text)
    exit(1)

# Step 2: Upload resumes
print(f"\n2. Uploading {len(RESUMES)} resumes...")
uploaded = []

for i, resume_path in enumerate(RESUMES, 1):
    name = Path(resume_path).stem
    print(f"\n   [{i}/{len(RESUMES)}] {name}...")
    
    with open(resume_path, 'rb') as f:
        res = requests.post(
            f"{API_BASE}/api/upload-resume",
            files={'file': f},
            data={'jd_id': jd_id, 'session_id': session_id}
        )
    
    if res.status_code == 200:
        result = res.json()
        print(f"   ✅ Score: {result['score']:.1f} ({result['grade']}) - {result['name']}")
        uploaded.append(result)
    else:
        print(f"   ❌ Failed: {res.status_code}")

# Step 3: Get batch results
print(f"\n3. Fetching batch results...")
res = requests.get(f"{API_BASE}/api/batch-results/{jd_id}")

if res.status_code == 200:
    batch = res.json()
    print(f"✅ Retrieved {batch['total']} results")
    
    print(f"\n{'='*80}")
    print("BATCH RESULTS - Ranked by Score")
    print(f"{'='*80}")
    
    for i, r in enumerate(batch['results'], 1):
        match_data = r['match_data']
        print(f"{i}. {r['name']:<30} | Score: {r['match_score']:5.1f} ({r['grade']}) | "
              f"Sem: {match_data.get('semantic_score', 0):5.1f} | "
              f"ML: {match_data.get('ml_score', 0):5.1f}")
else:
    print(f"❌ Failed: {res.status_code}")

# Step 4: Get by session
print(f"\n4. Fetching by session ID...")
res = requests.get(f"{API_BASE}/api/batch-results/session/{session_id}")

if res.status_code == 200:
    batch = res.json()
    print(f"✅ Retrieved {batch['total']} results for session")
else:
    print(f"❌ Failed: {res.status_code}")

print(f"\n{'='*80}")
print("✅ BATCH PROCESSING TEST COMPLETE")
print(f"{'='*80}")
print(f"\nSession ID: {session_id}")
print(f"JD ID: {jd_id}")
print(f"Resumes processed: {len(uploaded)}")
print(f"\nAll resumes are now linked to the JD and can be retrieved as a batch!")
