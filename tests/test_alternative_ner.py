"""Step 2: Test alternative NER models"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from transformers import pipeline
import torch

device = 0 if torch.cuda.is_available() else -1

test_text = """
Ritik Sharma
BI Developer
ritik.sharma@email.com | +91-9876543210

EXPERIENCE
Senior BI Developer at Tech Corp
2020 - Present

SKILLS
Python, SQL, Tableau, Power BI

EDUCATION
Bachelor of Technology in Computer Science
IIT Delhi, 2018
"""

print("="*80)
print("STEP 2: TEST ALTERNATIVE NER MODELS")
print("="*80)

# Test 1: dslim/bert-base-NER (general purpose, proven)
print("\n--- Model 1: dslim/bert-base-NER (General NER) ---")
try:
    ner1 = pipeline("ner", model="dslim/bert-base-NER", device=device, aggregation_strategy="simple")
    entities1 = ner1(test_text[:500])
    for e in entities1:
        print(f"  {e['entity_group']:15} | {e['word']}")
except Exception as ex:
    print(f"  Error: {ex}")

# Test 2: Current model
print("\n--- Model 2: yashpwr/resume-ner-bert-v2 (Current) ---")
try:
    ner2 = pipeline("ner", model="models/ner_model", device=device, aggregation_strategy="simple")
    entities2 = ner2(test_text[:500])
    for e in entities2:
        print(f"  {e['entity_group']:15} | {e['word']}")
except Exception as ex:
    print(f"  Error: {ex}")

print("\n" + "="*80)
