"""Test NER extraction with structured output"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.ner_extractor import NERExtractor

ner = NERExtractor()

test_text = """
John Smith
Senior Software Engineer
john.smith@email.com | +1-555-123-4567

EXPERIENCE
Senior Software Engineer at Google Inc.
2020 - Present

EDUCATION
Master of Science in Computer Science
Stanford University, 2018

SKILLS
Python, Java, AWS, Docker, Kubernetes
"""

print("="*80)
print("NER EXTRACTION TEST")
print("="*80)

result = ner.extract(test_text)

print("\n📋 STRUCTURED OUTPUT:\n")
for key, value in result.items():
    if value:
        print(f"  {key:15} : {value}")

print("\n" + "="*80)
print("✅ Extraction complete!")
print("="*80)
