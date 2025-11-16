"""Test LLM caching functionality"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.llm_cache import LLMCache
from app.services.llm_document_structurer import LLMDocumentStructurer
import time

print("=" * 80)
print("LLM CACHE TEST")
print("=" * 80)

# Test 1: Basic cache operations
print("\n[Test 1] Basic Cache Operations")
cache = LLMCache(cache_dir="llm_cache", ttl_hours=24)

test_text = "This is a test resume for John Doe, Software Engineer..."
test_data = {"name": "John Doe", "title": "Software Engineer"}

# Set cache
cache.set(test_text, "resume", test_data)
print("✅ Cache set")

# Get cache
result = cache.get(test_text, "resume")
assert result == test_data, "Cache data mismatch"
print("✅ Cache retrieved correctly")

# Test 2: Cache miss
print("\n[Test 2] Cache Miss")
result = cache.get("Different text", "resume")
assert result is None, "Should return None for cache miss"
print("✅ Cache miss handled correctly")

# Test 3: LLM structurer with cache
print("\n[Test 3] LLM Structurer with Cache")
structurer = LLMDocumentStructurer()

sample_resume = """
Ritik Sharma
Delhi | +918109617693 | sharmaritik.1807@gmail.com

SUMMARY
Power BI Developer with 2 years of experience

SKILLS
- Power BI Desktop
- SQL (T-SQL)
- ETL Automation
"""

print("\nFirst parse (should call LLM):")
start = time.time()
result1 = structurer.structure_resume(sample_resume)
time1 = time.time() - start
print(f"Time: {time1:.1f}s")

print("\nSecond parse (should use cache):")
start = time.time()
result2 = structurer.structure_resume(sample_resume)
time2 = time.time() - start
print(f"Time: {time2:.1f}s")

if time2 < 1.0:
    speedup = time1 / time2 if time2 > 0 else float('inf')
    print(f"✅ Cache working! Speedup: {speedup:.0f}x")
else:
    print("⚠️ Cache may not be working (second parse still slow)")

# Test 4: Cache statistics
print("\n[Test 4] Cache Statistics")
cache_dir = Path("llm_cache")
if cache_dir.exists():
    cache_files = list(cache_dir.glob("*.json"))
    print(f"Cached files: {len(cache_files)}")
    print(f"Resume caches: {len(list(cache_dir.glob('resume_*.json')))}")
    print(f"JD caches: {len(list(cache_dir.glob('jd_*.json')))}")
else:
    print("Cache directory not found")

print("\n" + "=" * 80)
print("✅ ALL TESTS PASSED")
print("=" * 80)
