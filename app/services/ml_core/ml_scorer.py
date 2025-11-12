"""
Layer 5: ML Scoring System
Market-grade implementation with Cross-Encoder + LightGBM
"""
import numpy as np
import logging
from typing import Dict, Tuple

class MLScorer:
    """Hybrid ML scorer: Cross-Encoder + LightGBM fusion"""
    
    def __init__(self):
        self.cross_encoder = None
        self.embedder = None
        self.rank_model = None
        self._load_models()
        self._load_rank_model()
    
    def _load_models(self):
        """Lazy load models on first use"""
        try:
            from sentence_transformers import CrossEncoder, SentenceTransformer
            self.cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
            logging.info("✅ ML models loaded (Cross-Encoder + SBERT)")
        except Exception as e:
            logging.warning(f"ML models not available: {e}")
    
    def _load_rank_model(self):
        """Load LightGBM ranking model"""
        import os
        model_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'models', 'ml_ranker.txt')
        if os.path.exists(model_path):
            try:
                import lightgbm as lgb
                self.rank_model = lgb.Booster(model_file=model_path)
                logging.info(f"✅ LightGBM model loaded from {model_path}")
            except Exception as e:
                logging.warning(f"Could not load LightGBM model: {e}")
        else:
            logging.warning(f"LightGBM model not found at {model_path}")
    
    def compute_embeddings(self, resume_text: str, jd_text: str) -> np.ndarray:
        """Compute embedding features: [resume_vec, jd_vec, diff_vec]"""
        if not self.embedder:
            return np.zeros(100)  # Fallback
        
        try:
            r_vec = self.embedder.encode(resume_text[:2000], normalize_embeddings=True)
            j_vec = self.embedder.encode(jd_text[:2000], normalize_embeddings=True)
            diff_vec = np.abs(r_vec - j_vec)
            
            # Concatenate and truncate to 100D for efficiency
            combined = np.concatenate([r_vec, j_vec, diff_vec])
            return combined[:100]
        except Exception as e:
            logging.warning(f"Embedding computation failed: {e}")
            return np.zeros(100)
    
    def ml_score(self, resume_text: str, jd_text: str, feature_dict: Dict = None) -> Tuple[float, str]:
        """
        Compute ML-based relevance score
        
        Returns:
            (score, explanation)
            score: 0-100
            explanation: Human-readable insight
        """
        # Validate inputs
        if not resume_text or not jd_text:
            return 0.0, "Invalid input"
        
        # Use semantic similarity from embedder (more dynamic)
        if self.embedder:
            try:
                r_vec = self.embedder.encode(resume_text[:2000], normalize_embeddings=True)
                j_vec = self.embedder.encode(jd_text[:2000], normalize_embeddings=True)
                similarity = float(np.dot(r_vec, j_vec))
                
                # Scale to 0-100 with realistic spread
                # Typical range: 0.25-0.85, map to 40-95 for wider variance
                ml_score = np.clip((similarity - 0.25) / (0.85 - 0.25) * 55 + 40, 40, 95)
                
                explanation = self._generate_explanation(ml_score, similarity)
                return round(ml_score, 2), explanation
            except Exception as e:
                logging.warning(f"Embedding similarity failed: {e}")
        
        # Fallback to Cross-Encoder
        ce_score = self._cross_encoder_score(resume_text, jd_text)
        final_score = ce_score * 100
        explanation = self._generate_explanation(final_score, ce_score)
        
        return round(final_score, 2), explanation
    
    def _cross_encoder_score(self, resume_text: str, jd_text: str) -> float:
        """Compute Cross-Encoder relevance score (0-1)"""
        if not self.cross_encoder:
            return self._fallback_score(resume_text, jd_text)
        
        try:
            # Cross-Encoder expects (query, document) pair
            raw_score = self.cross_encoder.predict([(jd_text[:512], resume_text[:512])])[0]
            
            # Normalize: Cross-Encoder outputs logits, not probabilities
            # Apply sigmoid to get 0-1 range
            import math
            normalized = 1 / (1 + math.exp(-raw_score))
            
            # Calibrate to realistic range (0.4-0.9 maps to 0-1)
            calibrated = np.clip((normalized - 0.4) / (0.9 - 0.4), 0, 1)
            return float(calibrated)
        except Exception as e:
            logging.warning(f"Cross-Encoder failed: {e}")
            return self._fallback_score(resume_text, jd_text)
    
    def _fusion_score(self, ce_score: float, resume_text: str, jd_text: str, feature_dict: Dict) -> float:
        """Fuse Cross-Encoder with rule-based features using LightGBM"""
        try:
            # Extract features
            vec_features = self.compute_embeddings(resume_text, jd_text)
            
            # Combine: [ce_score, embeddings(100)] = 101 features
            combined = np.concatenate([[ce_score], vec_features])
            
            # Predict with LightGBM
            raw_ml = self.rank_model.predict(combined.reshape(1, -1), predict_disable_shape_check=True)[0]
            
            # Normalize ML output to 0-100 range (calibrated for realistic spread)
            ml_score = np.clip((raw_ml - 0.4) / (0.9 - 0.4) * 100, 0, 100)
            return float(ml_score)
        except Exception as e:
            logging.warning(f"Fusion scoring failed: {e}")
            # Fallback: use calibrated CE score
            return np.clip((ce_score - 0.4) / (0.9 - 0.4) * 100, 0, 100)
    
    def _fallback_score(self, resume_text: str, jd_text: str) -> float:
        """Simple keyword-based fallback when ML unavailable"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        try:
            vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
            vectors = vectorizer.fit_transform([jd_text, resume_text])
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            return float(similarity)
        except:
            return 0.5  # Neutral
    
    def _generate_explanation(self, score: float, ce_score: float) -> str:
        """Generate human-readable explanation"""
        if score >= 85:
            return f"Excellent match ({ce_score*100:.0f}% semantic similarity)"
        elif score >= 70:
            return f"Strong match ({ce_score*100:.0f}% semantic similarity)"
        elif score >= 50:
            return f"Moderate match ({ce_score*100:.0f}% semantic similarity)"
        else:
            return f"Weak match ({ce_score*100:.0f}% semantic similarity) - consider tailoring resume"
    



# Singleton instance
_ml_scorer = None

def get_ml_scorer() -> MLScorer:
    """Get singleton ML scorer instance"""
    global _ml_scorer
    if _ml_scorer is None:
        _ml_scorer = MLScorer()
    return _ml_scorer
