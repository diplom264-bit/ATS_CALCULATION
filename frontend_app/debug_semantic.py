"""Debug semantic fit scoring"""
import sys
sys.path.insert(0, 'd:/ATSsys/version_4')

from app.services.checkers.jd_alignment_checker import JDAlignmentChecker
import fitz

resume_path = r"C:\Users\Owner\Downloads\Naukri_NikharJain[4y_6m] 1  python cv.pdf"
jd_path = r"C:\Users\Owner\Downloads\Python Developer - 3 to 6 years.docx"

# Extract texts
doc = fitz.open(resume_path)
resume_text = "\n".join(page.get_text() for page in doc)
doc.close()

doc = fitz.open(jd_path)
jd_text = "\n".join(page.get_text() for page in doc)
doc.close()

print("="*80)
print("SEMANTIC FIT DEBUG")
print("="*80)

checker = JDAlignmentChecker(use_kb=True)

print("\nChecking semantic fit...")
score, feedback = checker.check_semantic_fit(resume_text, jd_text)

print(f"\nScore: {score}/20")
print(f"Feedback: {feedback}")

print("\n" + "="*80)
print("RESUME PREVIEW (first 500 chars)")
print("="*80)
print(resume_text[:500])

print("\n" + "="*80)
print("JD PREVIEW (first 500 chars)")
print("="*80)
print(jd_text[:500])
