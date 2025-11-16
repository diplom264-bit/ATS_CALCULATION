# 🎯 ATS Resume Calculator

AI-powered resume analysis tool that evaluates ATS compatibility, job-fit relevance, and provides actionable feedback for resume improvement.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Features

### 🔍 Comprehensive Analysis
- **15-dimensional scoring system** covering layout, content, keywords, and semantic fit
- **Role mismatch detection** prevents wrong-role candidates from scoring high
- **Technical vs Soft skill categorization** with separate match analysis
- **AI-powered semantic matching** using transformer models
- **Knowledge base** with 18,168+ skills from ONET/ESCO taxonomies

### 📊 Smart Scoring
- **Keyword Alignment** (15 pts) - Matches resume against job description with technical skill penalties
- **Semantic Fit** (20 pts) - Deep learning-based job relevance scoring
- **Quantified Impact** (10 pts) - Detects metrics and achievements
- **ATS Compatibility** (20 pts) - File format, structure, readability
- **Career Quality** (35 pts) - Progression, gaps, education, certifications

### 🎨 User-Friendly Interface
- Clean web interface with drag-and-drop resume upload
- Real-time analysis with detailed score breakdown
- Separate display for technical and soft skills (matched/missing)
- Personalized recommendations based on individual gaps
- **AI-powered DOCX reports** with Llama 2 3B (optional)
- Export-ready reports

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or 3.11
- 8GB RAM (16GB recommended)
- 5GB disk space

### Installation

```bash
# 1. Clone repository
git clone https://github.com/diplom264-bit/ATS_CALCULATION.git
cd ATS_CALCULATION

# 2. Create virtual environment
python -m venv atsenv
atsenv\Scripts\activate  # Windows
# source atsenv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements_unified.txt

# 4. Download NLP models
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"

# 5. Download ML models
python download_models.py

# 6. (Optional) Setup AI report generation
# Install Ollama from https://ollama.ai/download
# ollama pull llama2:3b
# ollama serve
# See OLLAMA_SETUP.md for details

# 7. Start server
python main.py
```

### Access Application
- **Frontend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 📖 Usage

### Web Interface
1. Open http://localhost:8000
2. Upload resume (PDF/DOCX/TXT)
3. Paste job description (optional)
4. Click "Analyze Resume"
5. View detailed score breakdown and recommendations

### API
```python
import requests

# Analyze resume
with open('resume.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/analyze-resume',
        files={'file': f},
        data={'job_description': 'Python Developer with AWS, Docker...'}
    )

result = response.json()
print(f"Score: {result['ats_score']}/100")
print(f"Grade: {result['grade']}")
print(f"Matched Skills: {result['skill_match_details']['matched_technical']}")
```

---

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend      │  HTML/JS interface
└────────┬────────┘
         │
┌────────▼────────┐
│   FastAPI       │  REST API layer
└────────┬────────┘
         │
┌────────▼────────────────────────────┐
│   ATS Analyzer                      │
│   ├── 15 Scoring Modules            │
│   ├── Knowledge Base Engine         │
│   ├── Semantic Matcher              │
│   └── Feedback Generator            │
└────────┬────────────────────────────┘
         │
┌────────▼────────────────────────────┐
│   ML Models                         │
│   ├── Sentence Transformer (768D)  │
│   ├── NER (Entity Extraction)      │
│   └── QA (Information Extraction)  │
└─────────────────────────────────────┘
```

---

## 🎯 Key Innovation: Role Mismatch Detection

Traditional ATS systems fail to detect role mismatches. Our system:

1. **Extracts 100+ technical terms** from job description using TF-IDF
2. **Categorizes skills** into technical vs soft using 150+ tech patterns
3. **Applies strict penalties**:
   - <40% tech match → 0.2x multiplier (severe penalty)
   - <60% tech match → 0.4x multiplier (heavy penalty)
   - <80% tech match → 0.7x multiplier (moderate penalty)

**Example**: .NET developer applying for BI Developer role
- Without penalty: 60/100 (misleading)
- With penalty: 32/100 (accurate - missing Tableau, Power BI, SSAS, ETL)

---

## 📊 Scoring Breakdown

| Category | Points | Description |
|----------|--------|-------------|
| File Layout | 5 | PDF format, clean structure |
| Font Consistency | 5 | Professional typography |
| Readability | 5 | Clear, concise language |
| Professional Language | 5 | Action verbs, formal tone |
| Date Consistency | 5 | Uniform date formats |
| Employment Gaps | 5 | Career continuity |
| Career Progression | 5 | Growth trajectory |
| **Keyword Alignment** | **15** | **JD match + role detection** |
| Skill Context | 5 | Skills in experience |
| **Semantic Fit** | **20** | **AI job relevance** |
| **Quantified Impact** | **10** | **Metrics & achievements** |
| Online Presence | 5 | LinkedIn, GitHub |
| Education | 5 | Degrees & institutions |
| Certifications | 5 | Professional credentials |
| Fairness Check | 5 | Bias detection |
| **Total** | **100** | |

---

## 🧪 Testing

```bash
# Test single resume
python test_one_resume.py

# Test with job description
python test_real_jd_resume.py

# Test role mismatch detection
python test_role_mismatch.py

# Run full test suite
python quick_test_all.py
```

---

## 🐳 Docker Deployment

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements_unified.txt .
RUN pip install -r requirements_unified.txt && \
    python -m spacy download en_core_web_sm
COPY . .
CMD ["python", "main.py"]
```

```bash
docker build -t ats-calculator .
docker run -p 8000:8000 ats-calculator
```

---

## 📁 Project Structure

```
ATS_CALCULATION/
├── app/
│   ├── api/                           # FastAPI routes (3 files)
│   │   ├── ats_routes.py             # Main ATS endpoints
│   │   ├── document_parse_routes.py  # Document parsing
│   │   └── json_analysis_routes.py   # JSON analysis
│   ├── services/                      # Business logic (60+ files)
│   │   ├── checkers/                 # 15 scoring modules
│   │   ├── ml_core/                  # ML components
│   │   ├── ml_enhanced_analyzer.py   # ML-powered analysis
│   │   ├── smart_skill_matcher.py    # KB skill matching
│   │   └── knowledge_base_engine.py  # KB integration
│   └── database/                      # Database management
│       ├── db_manager.py             # SQLite operations
│       └── resumes/                  # 13 stored resume samples
├── frontend_app/                      # Frontend application
│   ├── templates/                    # HTML interface
│   │   └── index.html               # Main UI
│   ├── static/                       # Assets
│   ├── report_generator.py           # Report generation
│   └── api_server.py                 # Frontend API
├── knowledge_base/                    # 17,326 skills
│   ├── kb_extension.csv
│   └── kb_extension.jsonl
├── tests/                             # 60+ test files
├── utils/                             # Utility functions
├── main.py                            # Entry point
├── requirements_unified.txt           # Dependencies
├── README.md                          # This file
├── CACHING_SYSTEM.md                  # Caching docs
├── SETUP_GUIDE.md                     # Setup guide
└── .gitignore                         # Git ignore rules

Total: 140+ tracked files
```

---

## 🔧 Configuration

Create `.env` file (optional):
```env
HOST=0.0.0.0
PORT=8000
DEBUG=False
USE_GPU=False
DATABASE_URL=sqlite:///./app/database/ats.db
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

- **ONET/ESCO** for skills taxonomy
- **Hugging Face** for transformer models
- **Sentence Transformers** for semantic embeddings
- **FastAPI** for modern web framework

---

## 📧 Support

- **Repository**: https://github.com/diplom264-bit/ATS_CALCULATION
- **Documentation**: [SETUP_GUIDE.md](SETUP_GUIDE.md), [CACHING_SYSTEM.md](CACHING_SYSTEM.md)
- **API Reference**: http://localhost:8000/docs
- **Issues**: https://github.com/diplom264-bit/ATS_CALCULATION/issues

## 📦 Repository Contents

**Included in Git:**
- ✅ 140+ Python files with complete implementation
- ✅ 13 sample resume PDFs for testing
- ✅ 60+ comprehensive test files
- ✅ Complete documentation (README, guides, specs)
- ✅ Knowledge base with 17,326 skills
- ✅ Docker configuration
- ✅ Frontend application with report generation

**Excluded (auto-generated or sensitive):**
- ❌ Virtual environments (mvpenv/, venv/)
- ❌ API keys and secrets
- ❌ Database files (*.db, *.sqlite)
- ❌ Large ML model binaries (auto-downloaded on setup)
- ❌ Python cache (__pycache__/)
- ❌ IDE configs (.vscode/, .idea/)

---

## 🎓 Research & Development

This system implements cutting-edge NLP techniques:
- **Transformer-based semantic matching** (all-MiniLM-L6-v2)
- **Named Entity Recognition** for information extraction
- **TF-IDF with custom tokenization** for technical term extraction
- **Graph-based knowledge representation** with 14 avg relations per skill
- **Multi-dimensional scoring** with adaptive penalties

---

**Built  for better hiring decisions**
