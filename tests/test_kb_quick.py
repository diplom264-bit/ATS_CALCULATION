"""Quick KB integration test"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("Testing KB import...")
try:
    from app.services.knowledge_base_engine import get_kb
    print("✅ KB engine imported")
    
    kb_path = Path(__file__).parent.parent.parent / "knowledge_base" / "kb"
    print(f"KB path: {kb_path}")
    print(f"KB exists: {kb_path.exists()}")
    
    if kb_path.exists():
        kb = get_kb(str(kb_path))
        print("✅ KB loaded successfully")
        
        # Test search
        results = kb.search("python programming", type_filter="skill", top_k=3)
        print(f"\n🔍 Test search results:")
        for r in results:
            print(f"  - {r['label']} (score: {r['score']:.3f})")
    else:
        print("❌ KB directory not found")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
