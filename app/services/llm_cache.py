"""
LLM Response Cache - Avoid re-parsing same documents
"""
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

class LLMCache:
    """File-based cache for LLM parsing results"""
    
    def __init__(self, cache_dir: str = "llm_cache", ttl_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
    
    def _get_hash(self, text: str) -> str:
        """Generate MD5 hash of text"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def _get_cache_path(self, text_hash: str, doc_type: str) -> Path:
        """Get cache file path"""
        return self.cache_dir / f"{doc_type}_{text_hash}.json"
    
    def get(self, text: str, doc_type: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached result if exists and not expired"""
        text_hash = self._get_hash(text)
        cache_path = self._get_cache_path(text_hash, doc_type)
        
        if not cache_path.exists():
            return None
        
        # Check expiry
        mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
        if datetime.now() - mtime > self.ttl:
            cache_path.unlink()  # Delete expired
            return None
        
        # Load cached data
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def set(self, text: str, doc_type: str, data: Dict[str, Any]):
        """Cache LLM result"""
        text_hash = self._get_hash(text)
        cache_path = self._get_cache_path(text_hash, doc_type)
        
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def clear_expired(self):
        """Remove expired cache files"""
        for cache_file in self.cache_dir.glob("*.json"):
            mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if datetime.now() - mtime > self.ttl:
                cache_file.unlink()
    
    def clear_all(self):
        """Clear entire cache"""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
