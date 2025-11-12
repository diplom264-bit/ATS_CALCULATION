"""
Unified Embedding Pipeline
Generates and manages embeddings for resumes and JDs using SBERT + FAISS
"""
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from typing import List, Tuple
import pickle

class EmbeddingEngine:
    """Manages embeddings for semantic matching"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.dimension = 384
        self.index = None
        self.texts = []
        
    def encode(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for texts"""
        return self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    
    def build_index(self, texts: List[str]) -> faiss.Index:
        """Build FAISS index from texts"""
        embeddings = self.encode(texts)
        self.index = faiss.IndexFlatIP(self.dimension)
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
        self.texts = texts
        return self.index
    
    def search(self, query: str, k: int = 5) -> List[Tuple[str, float]]:
        """Search for similar texts"""
        if not self.index:
            return []
        
        query_embedding = self.encode([query])
        faiss.normalize_L2(query_embedding)
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for idx, score in zip(indices[0], distances[0]):
            if idx < len(self.texts):
                results.append((self.texts[idx], float(score)))
        return results
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute cosine similarity between two texts"""
        embeddings = self.encode([text1, text2])
        faiss.normalize_L2(embeddings)
        return float(np.dot(embeddings[0], embeddings[1]))
    
    def save(self, path: str):
        """Save index and texts"""
        if self.index:
            faiss.write_index(self.index, f"{path}.index")
            with open(f"{path}.pkl", 'wb') as f:
                pickle.dump(self.texts, f)
    
    def load(self, path: str):
        """Load index and texts"""
        self.index = faiss.read_index(f"{path}.index")
        with open(f"{path}.pkl", 'rb') as f:
            self.texts = pickle.load(f)
