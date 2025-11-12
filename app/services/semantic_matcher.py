"""
S-BERT Semantic Job-Fit Matcher
Model: all-MiniLM-L6-v2 (already in KB)
"""
from sentence_transformers import SentenceTransformer
import torch
import numpy as np
from pathlib import Path

class SemanticMatcher:
    """S-BERT for semantic job-fit scoring"""
    
    def __init__(self, model_cache_dir="models/sentence_transformer"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_cache_dir = Path(model_cache_dir)
        
        print(f"🔧 Loading S-BERT model (device: {self.device})...")
        
        if (self.model_cache_dir / "sentence-transformers_all-MiniLM-L6-v2").exists():
            print("✅ Using cached S-BERT model")
            self.model = SentenceTransformer("all-MiniLM-L6-v2", cache_folder=str(self.model_cache_dir), device=self.device)
        else:
            print("📥 Downloading S-BERT model (~90MB)...")
            self.model = SentenceTransformer("all-MiniLM-L6-v2", cache_folder=str(self.model_cache_dir), device=self.device)
        
        print(f"✅ S-BERT ready (GPU: {torch.cuda.is_available()})")
    
    def calculate_job_fit(self, resume_text: str, jd_text: str) -> float:
        """
        Calculate semantic similarity between resume and JD
        Returns: 0.0-1.0 (e.g., 0.82 = 82% semantic match)
        """
        # Encode both texts
        emb1 = self.model.encode(resume_text[:2000], convert_to_numpy=True)
        emb2 = self.model.encode(jd_text[:2000], convert_to_numpy=True)
        
        # Cosine similarity
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        
        return float(similarity)
