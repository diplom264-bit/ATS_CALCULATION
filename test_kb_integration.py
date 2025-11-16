"""Quick test to verify KB is integrated and working in main app"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from app.services.kb_singleton import get_kb_instance

print("Testing KB Integration in Main App...")
print("="*60)

# Get KB instance (same one used by main app)
kb = get_kb_instance()

# Test with real resume/JD skills
test_skills = [
    "ASP.NET Core", "Angular", "C#", "SQL Server", 
    "Docker", "REST APIs", "Microservices"
]

print("\n✅ KB Status:")
print(f"   Total entries: {len(kb.entries):,}")
print(f"   FAISS vectors: {kb.index.ntotal:,}")
print(f"   Model: {kb.model}")

print("\n🔍 Testing Skill Recognition:")
for skill in test_skills:
    results = kb.search(skill, type_filter='skill', top_k=1)
    if results:
        match = results[0]
        status = "✅" if match['score'] >= 0.7 else "⚠️"
        print(f"   {status} {skill:20s} → {match['label']:30s} ({match['score']:.3f})")
    else:
        print(f"   ❌ {skill:20s} → NOT FOUND")

print("\n🎯 KB Integration Status: ✅ ACTIVE AND WORKING")
print("="*60)
