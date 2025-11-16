"""
Test JD Change & Database Persistence
Verifies that JD changes are properly tracked in the database
"""

import requests
import sqlite3
from pathlib import Path

BASE_URL = "http://localhost:8008"
DB_PATH = "app/database/ats.db"

def print_header(text):
    print("\n" + "="*80)
    print(text)
    print("="*80)

def check_database():
    """Check database state"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM job_descriptions")
    jd_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM resumes")
    resume_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM match_results")
    match_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT session_id) FROM match_results")
    session_count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'jd_count': jd_count,
        'resume_count': resume_count,
        'match_count': match_count,
        'session_count': session_count
    }

def get_latest_session():
    """Get latest session data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            jd.session_id,
            jd.text,
            r.name,
            mr.match_score,
            mr.grade
        FROM match_results mr
        JOIN job_descriptions jd ON mr.jd_id = jd.id
        JOIN resumes r ON mr.resume_id = r.id
        ORDER BY mr.created_at DESC
        LIMIT 1
    """)
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'session_id': row[0],
            'jd_text': row[1][:50] + '...' if len(row[1]) > 50 else row[1],
            'name': row[2],
            'score': row[3],
            'grade': row[4]
        }
    return None

def test_jd_change_persistence():
    """Test JD change and database persistence"""
    
    print_header("JD CHANGE & DATABASE PERSISTENCE TEST")
    
    # Check initial database state
    print("\n1. Initial Database State")
    initial_state = check_database()
    print(f"   JD entries: {initial_state['jd_count']}")
    print(f"   Resume entries: {initial_state['resume_count']}")
    print(f"   Match results: {initial_state['match_count']}")
    print(f"   Unique sessions: {initial_state['session_count']}")
    
    # Test 1: Upload JD v1
    print("\n2. Uploading JD Version 1...")
    jd_v1 = ".NET Developer with 5+ years experience in C# and Angular"
    
    jd_data = {'jd_text': jd_v1}
    res = requests.post(f"{BASE_URL}/api/upload-jd", data=jd_data)
    result = res.json()
    
    if result['status'] == 'ok':
        jd_id_v1 = result['jd_id']
        session_id_v1 = result['session_id']
        print(f"   ✅ JD uploaded")
        print(f"   JD ID: {jd_id_v1}")
        print(f"   Session ID: {session_id_v1}")
    else:
        print(f"   ❌ Failed: {result.get('error')}")
        return
    
    # Test 2: Upload Resume
    print("\n3. Uploading Resume...")
    resume_path = Path("test_resumes/LavkushRaj_Dot Net Angular Developer (1) 1.pdf")
    
    if not resume_path.exists():
        print(f"   ⚠️  Resume not found: {resume_path}")
        print("   Skipping resume upload test")
    else:
        with open(resume_path, 'rb') as f:
            files = {'file': f}
            data = {
                'jd_id': jd_id_v1,
                'session_id': session_id_v1,
                'jd_text': jd_v1
            }
            res = requests.post(f"{BASE_URL}/api/upload-resume", files=files, data=data)
            result = res.json()
        
        if result['status'] == 'ok':
            resume_id_v1 = result['resume_id']
            score_v1 = result['score']
            grade_v1 = result['grade']
            print(f"   ✅ Resume uploaded")
            print(f"   Resume ID: {resume_id_v1}")
            print(f"   Score: {score_v1:.1f} ({grade_v1})")
        else:
            print(f"   ❌ Failed: {result.get('error')}")
            return
    
    # Check database after first upload
    print("\n4. Database State After First Upload")
    state_v1 = check_database()
    print(f"   JD entries: {state_v1['jd_count']} (+{state_v1['jd_count'] - initial_state['jd_count']})")
    print(f"   Resume entries: {state_v1['resume_count']} (+{state_v1['resume_count'] - initial_state['resume_count']})")
    print(f"   Match results: {state_v1['match_count']} (+{state_v1['match_count'] - initial_state['match_count']})")
    print(f"   Unique sessions: {state_v1['session_count']} (+{state_v1['session_count'] - initial_state['session_count']})")
    
    # Test 3: Upload JD v2 (simulating JD change)
    print("\n5. Uploading JD Version 2 (Changed)...")
    jd_v2 = ".NET Developer with 7+ years experience in C#, Angular, and Azure"
    
    jd_data = {'jd_text': jd_v2}
    res = requests.post(f"{BASE_URL}/api/upload-jd", data=jd_data)
    result = res.json()
    
    if result['status'] == 'ok':
        jd_id_v2 = result['jd_id']
        session_id_v2 = result['session_id']
        print(f"   ✅ JD uploaded")
        print(f"   JD ID: {jd_id_v2}")
        print(f"   Session ID: {session_id_v2}")
        print(f"   New session created: {session_id_v2 != session_id_v1}")
    else:
        print(f"   ❌ Failed: {result.get('error')}")
        return
    
    # Test 4: Upload same resume with new JD
    if resume_path.exists():
        print("\n6. Re-uploading Resume with New JD...")
        with open(resume_path, 'rb') as f:
            files = {'file': f}
            data = {
                'jd_id': jd_id_v2,
                'session_id': session_id_v2,
                'jd_text': jd_v2
            }
            res = requests.post(f"{BASE_URL}/api/upload-resume", files=files, data=data)
            result = res.json()
        
        if result['status'] == 'ok':
            resume_id_v2 = result['resume_id']
            score_v2 = result['score']
            grade_v2 = result['grade']
            print(f"   ✅ Resume uploaded")
            print(f"   Resume ID: {resume_id_v2}")
            print(f"   Score: {score_v2:.1f} ({grade_v2})")
            print(f"   Score changed: {abs(score_v2 - score_v1) > 0.1}")
        else:
            print(f"   ❌ Failed: {result.get('error')}")
            return
    
    # Check final database state
    print("\n7. Database State After JD Change")
    state_v2 = check_database()
    print(f"   JD entries: {state_v2['jd_count']} (+{state_v2['jd_count'] - state_v1['jd_count']})")
    print(f"   Resume entries: {state_v2['resume_count']} (+{state_v2['resume_count'] - state_v1['resume_count']})")
    print(f"   Match results: {state_v2['match_count']} (+{state_v2['match_count'] - state_v1['match_count']})")
    print(f"   Unique sessions: {state_v2['session_count']} (+{state_v2['session_count'] - state_v1['session_count']})")
    
    # Show latest session
    print("\n8. Latest Session Data")
    latest = get_latest_session()
    if latest:
        print(f"   Session ID: {latest['session_id']}")
        print(f"   JD Text: {latest['jd_text']}")
        print(f"   Candidate: {latest['name']}")
        print(f"   Score: {latest['score']:.1f} ({latest['grade']})")
    
    # Validation
    print("\n" + "="*80)
    print("VALIDATION RESULTS")
    print("="*80)
    
    checks = []
    
    # Check 1: New JD entry created
    if state_v2['jd_count'] > state_v1['jd_count']:
        print("✅ New JD entry created on change")
        checks.append(True)
    else:
        print("❌ No new JD entry created")
        checks.append(False)
    
    # Check 2: New session created
    if state_v2['session_count'] > state_v1['session_count']:
        print("✅ New session created on JD change")
        checks.append(True)
    else:
        print("❌ No new session created")
        checks.append(False)
    
    # Check 3: New resume entry created
    if state_v2['resume_count'] > state_v1['resume_count']:
        print("✅ New resume entry created")
        checks.append(True)
    else:
        print("❌ No new resume entry created")
        checks.append(False)
    
    # Check 4: New match result created
    if state_v2['match_count'] > state_v1['match_count']:
        print("✅ New match result created")
        checks.append(True)
    else:
        print("❌ No new match result created")
        checks.append(False)
    
    # Check 5: Latest session is v2
    if latest and latest['session_id'] == session_id_v2:
        print("✅ Latest session is the new one")
        checks.append(True)
    else:
        print("❌ Latest session is not the new one")
        checks.append(False)
    
    print("\n" + "="*80)
    if all(checks):
        print("✅ ALL CHECKS PASSED - JD CHANGE PERSISTENCE WORKING CORRECTLY")
    else:
        print(f"⚠️  {sum(checks)}/{len(checks)} CHECKS PASSED")
    print("="*80)

if __name__ == "__main__":
    try:
        test_jd_change_persistence()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
