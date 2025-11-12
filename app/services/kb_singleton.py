"""KB Singleton - Load knowledge base once at application start"""
from pathlib import Path

_kb_instance = None
_kb_loaded = False

def get_kb_instance():
    """Get or create KB singleton instance"""
    global _kb_instance, _kb_loaded
    
    if not _kb_loaded:
        try:
            kb_path = Path(__file__).parent.parent.parent.parent / "knowledge_base" / "kb"
            if kb_path.exists():
                from app.services.knowledge_base_engine import get_kb
                _kb_instance = get_kb(str(kb_path))
                _kb_loaded = True
                print("✅ KB loaded (singleton)")
        except Exception as e:
            print(f"⚠️ KB load failed: {e}")
            _kb_loaded = True
    
    return _kb_instance

def preload_kb():
    """Preload KB at application start"""
    return get_kb_instance()
