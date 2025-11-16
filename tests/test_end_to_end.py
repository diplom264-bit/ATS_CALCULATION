"""End-to-end test: Parse documents → Score → Analyze"""
import requests
import json
import time

API_URL = "http://localhost:8008"

def test_end_to_end():
    """Complete pipeline test"""
    resume_path = r"C:\Users\Owner\Downloads\RitikSharma_BI Developer.pdf"
    jd_path = r"C:\Users\Owner\Downloads\JD- BI Developer 2 to 4 years.docx"
    
    print("=" * 80)
    print("END-TO-END PIPELINE TEST")
    print("=" * 80)
    
    # Step 1: Parse Resume
    print("\n[1/4] Parsing Resume...")
    start = time.time()
    with open(resume_path, 'rb') as f:
        response = requests.post(
            f"{API_URL}/api/v1/document/parse-resume",
            files={'file': f},
            timeout=120
        )
    
    if response.status_code != 200:
        print(f"❌ Resume parsing failed: {response.status_code}")
        print(response.text)
        return
    
    resume_data = response.json()['data']
    print(f"✅ Resume parsed in {time.time()-start:.1f}s")
    print(f"   Name: {resume_data.get('personal_information', {}).get('name', 'N/A')}")
    print(f"   Skills: {sum(len(v) for v in resume_data.get('technical_skills', {}).values())} total")
    
    # Step 2: Parse JD
    print("\n[2/4] Parsing Job Description...")
    start = time.time()
    with open(jd_path, 'rb') as f:
        response = requests.post(
            f"{API_URL}/api/v1/document/parse-jd",
            files={'file': f},
            timeout=120
        )
    
    if response.status_code != 200:
        print(f"❌ JD parsing failed: {response.status_code}")
        print(response.text)
        return
    
    jd_data = response.json()['data']
    print(f"✅ JD parsed in {time.time()-start:.1f}s")
    print(f"   Position: {jd_data.get('position', 'N/A')}")
    print(f"   Required Skills: {len(jd_data.get('required_skills', []))}")
    
    # Step 3: Save parsed data as JSON files for analysis
    print("\n[3/4] Preparing data for analysis...")
    
    with open('parsed_resume.json', 'w') as f:
        json.dump(resume_data, f, indent=2)
    
    with open('parsed_jd.json', 'w') as f:
        json.dump(jd_data, f, indent=2)
    
    print("✅ Data saved to parsed_resume.json and parsed_jd.json")
    
    # Step 4: Run analysis using JSON Analysis API
    print("\n[4/4] Running analysis...")
    start = time.time()
    
    with open('parsed_resume.json', 'rb') as rf, open('parsed_jd.json', 'rb') as jf:
        response = requests.post(
            f"{API_URL}/api/v1/json-analysis/analyze",
            files={
                'resume_file': ('resume.json', rf, 'application/json'),
                'jd_file': ('jd.json', jf, 'application/json')
            },
            timeout=30
        )
    
    if response.status_code != 200:
        print(f"❌ Analysis failed: {response.status_code}")
        print(response.text)
        return
    
    analysis = response.json()['analysis']
    print(f"✅ Analysis completed in {time.time()-start:.1f}s")
    
    # Display Results
    print("\n" + "=" * 80)
    print("ANALYSIS RESULTS")
    print("=" * 80)
    
    print(f"\n📊 Overall Score: {analysis['final_score']:.1f}/100")
    print(f"   Grade: {analysis['grade']}")
    
    print(f"\n📈 Factor Scores:")
    for factor, score in analysis['scores'].items():
        bar = "█" * int(score/5) + "░" * (20 - int(score/5))
        print(f"   {factor:20s}: {bar} {score:.1f}%")
    
    print(f"\n✅ Matched Skills ({analysis['evidence']['matched_count']}):")
    for skill in analysis['evidence']['matched_skills'][:10]:
        print(f"   • {skill}")
    if analysis['evidence']['matched_count'] > 10:
        print(f"   ... and {analysis['evidence']['matched_count']-10} more")
    
    print(f"\n❌ Missing Skills ({analysis['evidence']['missing_count']}):")
    for skill in analysis['evidence']['missing_skills'][:10]:
        print(f"   • {skill}")
    if analysis['evidence']['missing_count'] > 10:
        print(f"   ... and {analysis['evidence']['missing_count']-10} more")
    
    print(f"\n💡 Recommendations:")
    for i, rec in enumerate(analysis['recommendations'], 1):
        print(f"   {i}. {rec}")
    
    print(f"\n📋 Detailed Breakdown:")
    for item in analysis['breakdown']:
        print(f"   {item['factor']:20s}: {item['score']:.1f}% (weight: {item['weight']*100:.0f}%) → contributes {item['contribution']:.1f} points")
    
    print("\n" + "=" * 80)
    print("✅ END-TO-END TEST COMPLETED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    test_end_to_end()
