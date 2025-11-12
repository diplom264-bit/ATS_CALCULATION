"""
Download and cache all required ML models
Run this after pip install to prepare the system
"""
import sys
from pathlib import Path

def download_models():
    """Download all required models"""
    print("🔄 Downloading ML models...")
    
    # 1. Sentence Transformer (for semantic matching)
    print("\n1/3 Downloading Sentence Transformer...")
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Sentence Transformer downloaded")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # 2. NER Model (for entity extraction)
    print("\n2/3 Downloading NER Model...")
    try:
        from transformers import AutoTokenizer, AutoModelForTokenClassification
        tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
        model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")
        print("✅ NER Model downloaded")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # 3. QA Model (for information extraction)
    print("\n3/3 Downloading QA Model...")
    try:
        from transformers import AutoTokenizer, AutoModelForQuestionAnswering
        tokenizer = AutoTokenizer.from_pretrained("deepset/roberta-base-squad2")
        model = AutoModelForQuestionAnswering.from_pretrained("deepset/roberta-base-squad2")
        print("✅ QA Model downloaded")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    print("\n✅ All models downloaded successfully!")
    print("Models cached in: ~/.cache/huggingface/")

if __name__ == "__main__":
    download_models()
