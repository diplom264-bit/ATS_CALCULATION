"""
Rigorous NER Extractor Testing - Edge Cases & MVP Validation
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.ner_extractor import NERExtractor
import time

print("="*80)
print("NER EXTRACTOR - EDGE CASE TESTING")
print("="*80)

# Initialize
ner = NERExtractor()

# Test Cases
test_cases = {
    "1. Standard Resume": """
John Smith
Senior Software Engineer
john.smith@email.com | +1-555-123-4567 | New York, NY

EXPERIENCE
Senior Software Engineer at Google Inc.
2020 - Present
- Led development of cloud infrastructure
- Managed team of 5 engineers

EDUCATION
Master of Science in Computer Science
Stanford University, 2018

SKILLS
Python, Java, AWS, Docker, Kubernetes
""",
    
    "2. Minimal Resume": """
Jane Doe
jane@email.com
Skills: Python, SQL
""",
    
    "3. No Contact Info": """
PROFESSIONAL EXPERIENCE
Software Developer at Microsoft
Built web applications using React and Node.js

EDUCATION
BS Computer Science, MIT
""",
    
    "4. International Format": """
Rajesh Kumar
+91-9876543210 | rajesh.kumar@gmail.com
Mumbai, India

WORK EXPERIENCE
Data Scientist at Infosys Technologies Ltd
2019 - 2023

EDUCATION
B.Tech in Information Technology
Indian Institute of Technology, Delhi

TECHNICAL SKILLS
Machine Learning, Python, TensorFlow, SQL, Power BI
""",
    
    "5. Non-Standard Sections": """
ABOUT ME
Alex Johnson | alex.j@company.com | 555-0123

PROFESSIONAL BACKGROUND
Tech Lead @ Amazon Web Services (2021-Present)
Senior Developer @ Facebook (2018-2021)

ACADEMIC CREDENTIALS
PhD Computer Science - Carnegie Mellon University

CORE COMPETENCIES
JavaScript, TypeScript, React, Node.js, MongoDB
""",
    
    "6. Multiple Emails/Phones": """
Sarah Williams
Primary: sarah.w@work.com | Personal: sarah@personal.com
Office: +1-555-111-2222 | Mobile: +1-555-333-4444

Experience at Apple Inc. and Tesla Motors
Education: Harvard University, Yale University
Skills: C++, Rust, Go, Blockchain
""",
    
    "7. Special Characters": """
José García-López
josé.garcía@email.com | +34-612-345-678
Barcelona, España

Trabajó en: Banco Santander, S.A.
Educación: Universidad de Barcelona
Habilidades: Python, R, SQL, Tableau
""",
    
    "8. Very Short": """
Bob Lee
bob@email.com
Python Developer
""",
    
    "9. No Structure": """
I am a software engineer with 5 years experience working at various companies 
including Microsoft and Google. I have a degree from MIT and know Python, Java, 
and C++. You can reach me at engineer@email.com or call 555-1234.
""",
    
    "10. Empty/Whitespace": """


    
    
"""
}

# Run tests
results = []
for name, text in test_cases.items():
    print(f"\n{'='*80}")
    print(f"TEST: {name}")
    print(f"{'='*80}")
    print(f"Input length: {len(text)} chars")
    
    try:
        start = time.time()
        result = ner.extract(text)
        elapsed = time.time() - start
        
        print(f"⏱️  Time: {elapsed:.3f}s")
        print(f"\n📊 Extracted:")
        print(f"   Name: {result.get('name', 'N/A')}")
        print(f"   Email: {result.get('email', 'N/A')}")
        print(f"   Phone: {result.get('phone', 'N/A')}")
        print(f"   Job Titles: {len(result.get('job_titles', []))} found")
        if result.get('job_titles'):
            for title in result['job_titles'][:3]:
                print(f"      • {title}")
        print(f"   Companies: {len(result.get('companies', []))} found")
        if result.get('companies'):
            for company in result['companies'][:3]:
                print(f"      • {company}")
        print(f"   Universities: {len(result.get('universities', []))} found")
        if result.get('universities'):
            for uni in result['universities'][:3]:
                print(f"      • {uni}")
        print(f"   Skills: {len(result.get('skills', []))} found")
        if result.get('skills'):
            for skill in result['skills'][:5]:
                print(f"      • {skill}")
        
        # Validation
        issues = []
        if not result.get('name'):
            issues.append("⚠️  No name extracted")
        if not result.get('email'):
            issues.append("⚠️  No email extracted")
        if not result.get('job_titles') and "experience" in text.lower():
            issues.append("⚠️  No job titles found (expected)")
        if not result.get('skills') and "skill" in text.lower():
            issues.append("⚠️  No skills found (expected)")
        
        if issues:
            print(f"\n⚠️  Issues:")
            for issue in issues:
                print(f"   {issue}")
            status = "PARTIAL"
        else:
            status = "PASS"
        
        print(f"\n✅ Status: {status}")
        
        results.append({
            "test": name,
            "status": status,
            "time": elapsed,
            "extracted": result
        })
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        results.append({
            "test": name,
            "status": "FAIL",
            "error": str(e)
        })

# Summary
print(f"\n{'='*80}")
print("SUMMARY")
print(f"{'='*80}")

passed = sum(1 for r in results if r['status'] == 'PASS')
partial = sum(1 for r in results if r['status'] == 'PARTIAL')
failed = sum(1 for r in results if r['status'] == 'FAIL')

print(f"\nTotal Tests: {len(results)}")
print(f"✅ Passed: {passed}")
print(f"⚠️  Partial: {partial}")
print(f"❌ Failed: {failed}")

avg_time = sum(r.get('time', 0) for r in results if 'time' in r) / len([r for r in results if 'time' in r])
print(f"\n⏱️  Average Time: {avg_time:.3f}s")

print(f"\n{'='*80}")
