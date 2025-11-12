"""Test report generation with sample data"""
from report_generator import create_docx_report

# Sample data
resume_data = {
    'name': 'John Doe',
    'email': 'john.doe@example.com',
    'phone': '+1-234-567-8900',
    'skills': ['Python', 'SQL', 'Power BI', 'DAX', 'Azure', 'ETL', 'Data Analysis'],
    'companies': ['Tech Corp', 'Data Inc', 'Analytics Ltd'],
    'job_titles': ['Data Analyst', 'BI Developer'],
    'degrees': ['B.Sc. Computer Science']
}

analysis_data = {
    'final_score': 72.5,
    'grade': 'C',
    'breakdown': {
        'file_layout': 85.0,
        'font_consistency': 70.0,
        'readability': 65.0,
        'professional_language': 60.0,
        'date_consistency': 90.0,
        'employment_gaps': 85.0,
        'career_progression': 75.0,
        'keyword_alignment': 80.0,
        'skill_context': 55.0,
        'semantic_fit': 50.0,
        'quantified_impact': 40.0,
        'online_presence': 70.0
    },
    'feedback': [
        'Add quantifiable achievements with metrics (%, $, numbers)',
        'Improve semantic fit by tailoring content to job requirements',
        'Enhance skill context by demonstrating skills in experience section',
        'Include more job-specific keywords',
        'Add measurable results to accomplishments'
    ]
}

print("="*60)
print("REPORT GENERATION DRY RUN")
print("="*60)
print("\nGenerating test report...")
print(f"Candidate: {resume_data['name']}")
print(f"Score: {analysis_data['final_score']}/100")
print(f"Grade: {analysis_data['grade']}")
print("\nGenerating DOCX report with Ollama...")

try:
    output_path = "test_report.docx"
    create_docx_report(resume_data, analysis_data, output_path)
    print(f"\nReport generated successfully: {output_path}")
    print(f"Full path: d:\\ATSsys\\version_4\\frontend_app\\{output_path}")
    print("\nOpen the file to review the AI-generated content!")
except Exception as e:
    print(f"\nError: {e}")
