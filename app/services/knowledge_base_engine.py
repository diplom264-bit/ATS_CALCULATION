"""
Knowledge Base Search Engine
Fast semantic search with FAISS and relation traversal
"""
import json
import faiss
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional, Union

class KnowledgeBase:
    """GPU-aware semantic search engine for unified KB"""
    
    def __init__(self, kb_path: str = "kb"):
        """Load KB, FAISS index, and relations"""
        self.kb_path = Path(kb_path)
        self.model = None
        self.index = None
        self.entries = []
        self.id_map = {}
        self.relations = {}
        self._load()
    
    def _load(self):
        """Load all KB components"""
        print("📦 Loading Knowledge Base...")
        
        # Load model - check metadata for correct model
        try:
            import torch
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
        except:
            device = 'cpu'
        
        # Load model from metadata if available
        model_name = "all-MiniLM-L6-v2"  # default
        metadata_path = self.kb_path / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                model_name = metadata.get('model', model_name)
        
        self.model = SentenceTransformer(model_name, device=device)
        print(f"  Model: {model_name} (device: {device})")
        
        # Load entries
        with open(self.kb_path / "knowledge.jsonl", "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                entry = json.loads(line)
                entry.pop('embedding', None)  # Remove embedding to save memory
                self.entries.append(entry)
                self.id_map[entry['id']] = i
        print(f"  Entries: {len(self.entries):,}")
        
        # Load FAISS index
        self.index = faiss.read_index(str(self.kb_path / "knowledge.index"))
        print(f"  FAISS index: {self.index.ntotal:,} vectors")
        
        # Load relations
        with open(self.kb_path / "relations.json", "r", encoding="utf-8") as f:
            self.relations = json.load(f)
        print(f"  Relations: {len(self.relations['occupation_skills']):,} occ-skill, {len(self.relations['related_occupations']):,} related")
        print("✅ KB loaded\n")
    
    def search(self, query: str, type_filter: Optional[str] = None, top_k: int = 10) -> List[Dict]:
        """
        Semantic search with optional type filtering
        
        Args:
            query: Search text
            type_filter: Filter by type (skill, occupation, jd, etc.)
            top_k: Number of results
            
        Returns:
            List of matching entries with scores
        """
        # Encode query
        query_emb = self.model.encode([query], normalize_embeddings=True, convert_to_numpy=True)
        
        # Search FAISS
        scores, indices = self.index.search(query_emb.astype('float32'), top_k * 3 if type_filter else top_k)
        
        # Build results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1: continue
            entry = self.entries[idx].copy()
            entry['score'] = float(score)
            
            # Apply type filter
            if type_filter and entry['type'] != type_filter:
                continue
            
            results.append(entry)
            if len(results) >= top_k:
                break
        
        return results
    
    def search_batch(self, queries: List[str], type_filter: Optional[str] = None, top_k: int = 10) -> List[List[Dict]]:
        """Batch search for multiple queries"""
        query_embs = self.model.encode(queries, normalize_embeddings=True, convert_to_numpy=True, batch_size=32)
        scores, indices = self.index.search(query_embs.astype('float32'), top_k * 3 if type_filter else top_k)
        
        all_results = []
        for query_scores, query_indices in zip(scores, indices):
            results = []
            for score, idx in zip(query_scores, query_indices):
                if idx == -1: continue
                entry = self.entries[idx].copy()
                entry['score'] = float(score)
                if type_filter and entry['type'] != type_filter:
                    continue
                results.append(entry)
                if len(results) >= top_k:
                    break
            all_results.append(results)
        
        return all_results
    
    def get_by_id(self, entry_id: str) -> Optional[Dict]:
        """Retrieve entry by ID"""
        idx = self.id_map.get(entry_id)
        return self.entries[idx].copy() if idx is not None else None
    
    def get_skills_for_occupation(self, occupation_uri: str, relation_type: Optional[str] = None) -> List[Dict]:
        """
        Get skills required for an occupation
        
        Args:
            occupation_uri: ESCO occupation URI
            relation_type: Filter by 'essential' or 'optional'
            
        Returns:
            List of skill entries with relation metadata
        """
        skills = []
        for rel in self.relations['occupation_skills']:
            if rel['occupation_uri'] != occupation_uri:
                continue
            if relation_type and rel['relation_type'] != relation_type:
                continue
            
            # Find skill entry
            skill_uri = rel['skill_uri']
            skill_id = f"skill:{skill_uri.split('/')[-1]}"
            skill = self.get_by_id(skill_id)
            if skill:
                skill['relation_type'] = rel['relation_type']
                skill['skill_type'] = rel['skill_type']
                skills.append(skill)
        
        return skills
    
    def get_related_occupations(self, occupation_title: str, max_tier: int = 3) -> List[Dict]:
        """
        Get related occupations
        
        Args:
            occupation_title: Occupation title
            max_tier: Maximum relatedness tier (1=most related, 5=least)
            
        Returns:
            List of related occupation entries
        """
        related = []
        for rel in self.relations['related_occupations']:
            if rel['title'].lower() != occupation_title.lower():
                continue
            tier = int(rel.get('relatedness_tier', 5))
            if tier > max_tier:
                continue
            
            # Search for related occupation
            results = self.search(rel['related_title'], type_filter='occupation', top_k=1)
            if results:
                occ = results[0]
                occ['relatedness_tier'] = tier
                related.append(occ)
        
        return related
    
    def extract_skills(self, text: str, top_k: int = 20, threshold: float = 0.3) -> List[Dict]:
        """
        Extract skills from text (resume/JD)
        
        Args:
            text: Input text
            top_k: Max skills to extract
            threshold: Minimum similarity score
            
        Returns:
            List of matching skills
        """
        results = self.search(text, type_filter='skill', top_k=top_k)
        return [r for r in results if r['score'] >= threshold]
    
    def match_resume_to_jd(self, resume_text: str, jd_text: str) -> Dict:
        """
        Match resume to job description
        
        Returns:
            Match analysis with scores and gaps
        """
        # Generic words to filter out
        GENERIC_WORDS = {
            'technical', 'using', 'experience', 'skills', 'knowledge', 'ability',
            'working', 'understanding', 'strong', 'good', 'excellent', 'proficient',
            'familiar', 'expertise', 'background', 'years', 'work', 'team', 'teams',
            'business', 'performance', 'management', 'development', 'support',
            'analysis', 'design', 'implementation', 'testing', 'documentation'
        }
        
        # Extract skills from both
        resume_skills = self.extract_skills(resume_text, top_k=50, threshold=0.4)
        jd_skills = self.extract_skills(jd_text, top_k=50, threshold=0.4)
        
        # Filter and normalize skills
        def filter_skills(skills):
            filtered = []
            seen = set()
            for s in skills:
                label = s['label']
                label_lower = label.lower()
                
                # Skip generic words
                if label_lower in GENERIC_WORDS:
                    continue
                
                # Skip single words < 3 chars (except SQL, AWS, etc.)
                if len(label_lower) < 3 and label_lower not in {'sql', 'aws', 'gcp', 'c++', 'c#', 'r', 'go'}:
                    continue
                
                # Skip duplicates (case-insensitive)
                if label_lower in seen:
                    continue
                
                seen.add(label_lower)
                filtered.append(s)
            
            return filtered
        
        resume_skills_filtered = filter_skills(resume_skills)
        jd_skills_filtered = filter_skills(jd_skills)
        
        # Find matching occupations
        jd_occupations = self.search(jd_text, type_filter='occupation', top_k=5)
        
        # Build skill maps (lowercase → original label)
        resume_map = {s['label'].lower(): s['label'] for s in resume_skills_filtered}
        jd_map = {s['label'].lower(): s['label'] for s in jd_skills_filtered}
        
        # Calculate overlap
        resume_keys = set(resume_map.keys())
        jd_keys = set(jd_map.keys())
        
        matched_keys = resume_keys & jd_keys
        missing_keys = jd_keys - resume_keys
        
        # Return original formatted labels
        matched = [jd_map[k] for k in matched_keys]
        missing = [jd_map[k] for k in missing_keys]
        
        return {
            'resume_skills': [s['label'] for s in resume_skills_filtered[:15]],
            'jd_skills': [s['label'] for s in jd_skills_filtered[:15]],
            'matched_skills': sorted(matched),
            'missing_skills': sorted(missing),
            'match_score': len(matched) / len(jd_keys) if jd_keys else 0,
            'suggested_occupations': jd_occupations[:3]
        }
    
    def get_stats(self) -> Dict:
        """Get KB statistics"""
        type_counts = {}
        for entry in self.entries:
            t = entry['type']
            type_counts[t] = type_counts.get(t, 0) + 1
        
        return {
            'total_entries': len(self.entries),
            'types': type_counts,
            'relations': {
                'occupation_skills': len(self.relations['occupation_skills']),
                'related_occupations': len(self.relations['related_occupations'])
            }
        }

# Convenience functions
_kb_instance = None

def get_kb(kb_path: str = "kb") -> KnowledgeBase:
    """Get singleton KB instance"""
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = KnowledgeBase(kb_path)
    return _kb_instance

def search(query: str, type_filter: Optional[str] = None, top_k: int = 10) -> List[Dict]:
    """Quick search function"""
    return get_kb().search(query, type_filter, top_k)

if __name__ == "__main__":
    # Demo usage
    kb = KnowledgeBase()
    
    print("🔍 Demo Searches:\n")
    
    # Search skills
    print("1️⃣ Search: 'python programming'")
    results = kb.search("python programming", type_filter="skill", top_k=5)
    for r in results:
        print(f"  {r['label']} (score: {r['score']:.3f})")
    
    # Search occupations
    print("\n2️⃣ Search: 'software developer'")
    results = kb.search("software developer", type_filter="occupation", top_k=5)
    for r in results:
        print(f"  {r['label']} (score: {r['score']:.3f})")
    
    # Stats
    print("\n3️⃣ KB Statistics:")
    stats = kb.get_stats()
    print(f"  Total entries: {stats['total_entries']:,}")
    for t, count in stats['types'].items():
        print(f"    {t}: {count:,}")
