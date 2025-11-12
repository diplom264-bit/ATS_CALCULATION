"""
Feature Fusion Layer
Combines embeddings + rule-based features for ML scoring
"""
import numpy as np
from typing import Dict, List
from sklearn.preprocessing import StandardScaler

class FeatureFusion:
    """Fuses multiple feature types into unified representation"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.feature_names = []
        
    def extract_rule_features(self, parsed_data: Dict, resume_text: str) -> np.ndarray:
        """Extract rule-based features"""
        features = []
        
        # Content features
        features.append(len(parsed_data.get('skills', [])))
        features.append(len(parsed_data.get('work_history', [])))
        features.append(len(resume_text.split()))
        features.append(len(parsed_data.get('degrees', [])))
        
        # Experience features
        work_history = parsed_data.get('work_history', [])
        total_years = sum(self._calculate_duration(job) for job in work_history)
        features.append(total_years)
        features.append(len(work_history) / max(total_years, 1))  # Job change frequency
        
        # Quality signals
        features.append(1 if parsed_data.get('email') else 0)
        features.append(1 if parsed_data.get('phone') else 0)
        features.append(1 if parsed_data.get('linkedin') else 0)
        
        # Text quality
        features.append(len(resume_text) / max(len(resume_text.split()), 1))  # Avg word length
        features.append(resume_text.count('%') + resume_text.count('$'))  # Quantification signals
        
        return np.array(features, dtype=np.float32)
    
    def _calculate_duration(self, job: Dict) -> float:
        """Calculate job duration in years"""
        try:
            start = job.get('start_date', '')
            end = job.get('end_date', '')
            if start and end:
                return 1.0  # Simplified
        except:
            pass
        return 0.0
    
    def fuse_features(self, embedding: np.ndarray, rule_features: np.ndarray) -> np.ndarray:
        """Combine embedding and rule features"""
        return np.concatenate([embedding, rule_features])
    
    def extract_all_features(self, resume_text: str, parsed_data: Dict, embedding_engine) -> Dict:
        """Extract all feature types"""
        # Embedding features
        resume_embedding = embedding_engine.encode([resume_text])[0]
        
        # Rule features
        rule_features = self.extract_rule_features(parsed_data, resume_text)
        
        # Fused features
        fused = self.fuse_features(resume_embedding, rule_features)
        
        return {
            'embedding': resume_embedding,
            'rule_features': rule_features,
            'fused': fused,
            'embedding_dim': len(resume_embedding),
            'rule_dim': len(rule_features),
            'total_dim': len(fused)
        }
