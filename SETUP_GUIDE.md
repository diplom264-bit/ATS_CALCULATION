# ATS Resume Calculator - Setup Guide

Complete guide to set up and run the ATS Resume Calculator on any machine.

---

## 📋 Prerequisites

- **Python 3.10 or 3.11** (3.12+ not tested)
- **8GB RAM minimum** (16GB recommended for ML models)
- **5GB disk space** (for models and dependencies)
- **Git** (for cloning repository)

---

## 🚀 Quick Start (5 Minutes)

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd version_4
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv atsenv
atsenv\Scripts\activate

# Linux/Mac
python3 -m venv atsenv
source atsenv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements_unified.txt
```

### 4. Download NLP Models
```bash
# Spacy model
python -m spacy download en_core_web_sm

# NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('averaged_perceptron_tagger')"
```

### 5. Download ML Models (Automatic on First Run)
```bash
python download_models.py
```

### 6. Start Server
```bash
# Windows
python main.py

# Linux/Mac
python3 main.py
```

### 7. Access Application
- **Frontend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 📁 Project Structure

```
version_4/
├── app/
│   ├── api/                    # API routes
│   ├── services/               # Business logic
│   │   ├── checkers/          # 15 scoring modules
│   │   ├── knowledge_base_engine.py
│   │   └── kb_singleton.py
│   └── database/              # SQLite database
├── frontend_app/
│   ├── templates/             # HTML frontend
│   └── static/                # Assets
├── models/                    # Pre-trained ML models
│   ├── ner_model/            # Named Entity Recognition
│   ├── qa_model/             # Question Answering
│   └── sentence_transformer/ # Embeddings
├── knowledge_base/           # ONET/ESCO skills KB
│   ├── kb_extension.csv
│   └── kb_extension.jsonl
├── main.py                   # Application entry point
├── requirements_unified.txt  # All dependencies
└── download_models.py        # Model downloader
```

---

## 🔧 Configuration

### Environment Variables (Optional)
Create `.env` file in project root:
```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Database
DATABASE_URL=sqlite:///./app/database/ats.db

# ML Models
USE_GPU=False
MODEL_CACHE_DIR=./models
```

### GPU Support (Optional)
For faster processing with NVIDIA GPU:
```bash
# Uninstall CPU torch
pip uninstall torch

# Install GPU torch
pip install torch==2.1.2+cu118 --index-url https://download.pytorch.org/whl/cu118
```

### AI Report Generation (Optional)
For AI-powered personalized reports using Llama 2 3B:
```bash
# Install Ollama from https://ollama.ai/download
# Then pull the model
ollama pull llama2:3b
ollama serve
```

**Note**: This is completely optional. The core ATS analysis works perfectly without it.
See [OLLAMA_SETUP.md](OLLAMA_SETUP.md) for detailed instructions.

---

## 🧪 Testing

### Test Single Resume
```bash
python test_one_resume.py
```

### Test with Job Description
```bash
python test_real_jd_resume.py
```

### Run Full Test Suite
```bash
python quick_test_all.py
```

---

## 📊 API Usage

### Analyze Resume
```bash
curl -X POST "http://localhost:8000/api/v1/analyze-resume" \
  -F "file=@resume.pdf" \
  -F "job_description=Software Engineer with Python, AWS, Docker..."
```

### Response Format
```json
{
  "ats_score": 75.5,
  "grade": "B",
  "category_scores": {
    "file_layout": 80.0,
    "keyword_alignment": 85.0,
    "semantic_fit": 70.0
  },
  "skill_match_details": {
    "matched_technical": ["Python", "AWS", "Docker"],
    "missing_technical": ["Kubernetes", "Terraform"],
    "matched_soft": ["Leadership", "Communication"],
    "missing_soft": []
  },
  "recommendations": [
    "Add missing technical skills: Kubernetes, Terraform",
    "Quantify achievements with metrics"
  ]
}
```

---

## 🎯 Key Features

### 15-Dimensional Scoring System
1. **File Layout** (5 pts) - PDF format, clean structure
2. **Font Consistency** (5 pts) - Professional typography
3. **Readability** (5 pts) - Clear, concise language
4. **Professional Language** (5 pts) - Action verbs, formal tone
5. **Date Consistency** (5 pts) - Uniform date formats
6. **Employment Gaps** (5 pts) - Career continuity
7. **Career Progression** (5 pts) - Growth trajectory
8. **Keyword Alignment** (15 pts) - JD keyword match with role mismatch detection
9. **Skill Context** (5 pts) - Skills demonstrated in experience
10. **Semantic Fit** (20 pts) - AI-powered job relevance
11. **Quantified Impact** (10 pts) - Metrics and achievements
12. **Online Presence** (5 pts) - LinkedIn, GitHub, portfolio
13. **Education Quality** (5 pts) - Degrees and institutions
14. **Certifications** (5 pts) - Professional credentials
15. **Fairness Check** (5 pts) - Bias detection

### Role Mismatch Detection
- Extracts 100+ technical skills from JD using TF-IDF
- Categorizes skills: Technical vs Soft
- Applies penalties:
  - **<40% tech match**: 0.2x multiplier (severe penalty)
  - **<60% tech match**: 0.4x multiplier (heavy penalty)
  - **<80% tech match**: 0.7x multiplier (moderate penalty)
- Prevents wrong-role candidates from scoring high

### Knowledge Base
- **18,168 skills** from ONET/ESCO taxonomies
- **768-dimensional embeddings** for semantic matching
- **14 avg relations per skill** for graph connectivity
- **83.9% embedding quality** validated by audit framework

---

## 🐛 Troubleshooting

### Issue: Models not downloading
```bash
# Manual download
python download_models.py

# Or download specific models
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Issue: Port 8000 already in use
```bash
# Change port in main.py or use environment variable
PORT=8080 python main.py
```

### Issue: Out of memory
```bash
# Reduce batch size in kb_singleton.py
# Or use CPU instead of GPU
USE_GPU=False python main.py
```

### Issue: Spacy model not found
```bash
python -m spacy download en_core_web_sm
```

---

## 🚢 Production Deployment

### Docker (Recommended)
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements_unified.txt .
RUN pip install -r requirements_unified.txt
RUN python -m spacy download en_core_web_sm
COPY . .
CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t ats-calculator .
docker run -p 8000:8000 ats-calculator
```

### Cloud Deployment
- **AWS EC2**: t3.large or larger (2 vCPU, 8GB RAM)
- **Google Cloud Run**: 2 CPU, 8GB memory
- **Azure App Service**: P2v2 tier or higher

---

## 📝 Development

### Add New Scoring Module
1. Create checker in `app/services/checkers/`
2. Implement `check_*()` method returning `(score, feedback)`
3. Register in `ats_analyzer.py`

### Extend Knowledge Base
1. Add skills to `knowledge_base/kb_extension.csv`
2. Run `scripts/build_kb_extension.py`
3. Restart server

---

## 📄 License

MIT License - See LICENSE file

---

## 🤝 Support

- **Issues**: GitHub Issues
- **Documentation**: `/docs` endpoint
- **API Reference**: http://localhost:8000/docs

---

## ✅ Verification Checklist

After setup, verify:
- [ ] Server starts without errors
- [ ] Frontend loads at http://localhost:8000
- [ ] Can upload and analyze a PDF resume
- [ ] Skill match displays technical/soft skills separately
- [ ] Role mismatch detection works (test .NET dev vs BI JD)
- [ ] API documentation accessible at /docs
- [ ] Database created at `app/database/ats.db`
- [ ] Models downloaded in `models/` directory

---

**Setup Time**: ~10 minutes (excluding model downloads)
**First Run**: May take 2-3 minutes to load ML models into memory
