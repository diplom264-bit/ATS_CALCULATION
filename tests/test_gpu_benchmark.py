"""Benchmark CPU vs GPU performance"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
import time
from app.services.qa_extractor import QAExtractor

print("=" * 80)
print("GPU BENCHMARK TEST")
print("=" * 80)

# Check CUDA
cuda_available = torch.cuda.is_available()
print(f"\n🔧 CUDA Available: {cuda_available}")
if cuda_available:
    print(f"   GPU: {torch.cuda.get_device_name(0)}")
    print(f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
else:
    print("   ⚠️ Running on CPU only")

# Sample resume text
sample_text = """
Ritik Sharma
Delhi | +918109617693 | sharmaritik.1807@gmail.com

SUMMARY
Detail-oriented Power BI Developer with 2+ years of experience in designing 
scalable dashboards, optimizing ETL pipelines, and delivering actionable insights.

EXPERIENCE
Power BI Developer
Trident Information Systems Pvt. Ltd., Delhi
Feb 2023 - Present

- Built real-time dashboards in Power BI Service
- Developed SQL and DAX-based financial dashboards
- Implemented Row-Level Security (RLS)

EDUCATION
PGDM – Business Analytics & Marketing
Lloyd Business School, Greater Noida
2021 – 2023

SKILLS
Power BI Desktop, SQL (T-SQL), ETL Automation, Data Modeling, DAX
"""

# Initialize extractor
print("\n" + "=" * 80)
print("INITIALIZING QA EXTRACTOR")
print("=" * 80)

start = time.time()
qa = QAExtractor()
init_time = time.time() - start
print(f"⏱️ Initialization time: {init_time:.2f}s")

# Warm-up (first run is slower due to compilation)
print("\n" + "=" * 80)
print("WARM-UP RUN")
print("=" * 80)
start = time.time()
_ = qa.extract_resume(sample_text)
warmup_time = time.time() - start
print(f"⏱️ Warm-up time: {warmup_time:.2f}s")

# Benchmark: Single extraction
print("\n" + "=" * 80)
print("SINGLE EXTRACTION BENCHMARK")
print("=" * 80)

times = []
for i in range(5):
    start = time.time()
    result = qa.extract_resume(sample_text)
    elapsed = time.time() - start
    times.append(elapsed)
    print(f"Run {i+1}: {elapsed:.2f}s")

avg_time = sum(times) / len(times)
print(f"\n📊 Average time: {avg_time:.2f}s")
print(f"📊 Min time: {min(times):.2f}s")
print(f"📊 Max time: {max(times):.2f}s")

# Benchmark: Batch processing
print("\n" + "=" * 80)
print("BATCH PROCESSING BENCHMARK (10 resumes)")
print("=" * 80)

start = time.time()
for i in range(10):
    _ = qa.extract_resume(sample_text)
batch_time = time.time() - start
per_resume = batch_time / 10

print(f"⏱️ Total time: {batch_time:.2f}s")
print(f"⏱️ Per resume: {per_resume:.2f}s")
print(f"📊 Throughput: {3600 / per_resume:.0f} resumes/hour")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print(f"\n🔧 Device: {'GPU (CUDA)' if cuda_available else 'CPU'}")
print(f"⏱️ Average extraction time: {avg_time:.2f}s")
print(f"📊 Throughput: {3600 / avg_time:.0f} resumes/hour")
print(f"💾 Daily capacity (24/7): {86400 / avg_time:.0f} resumes")

if cuda_available:
    print(f"\n✅ GPU acceleration enabled")
    print(f"   Expected speedup: 2.5-3x vs CPU")
else:
    print(f"\n⚠️ GPU not available")
    print(f"   Install CUDA PyTorch for 2.5-3x speedup:")
    print(f"   pip install torch --index-url https://download.pytorch.org/whl/cu118")

print("\n" + "=" * 80)
