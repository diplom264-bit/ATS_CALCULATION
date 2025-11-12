# GitHub Upload Guide

Step-by-step guide to upload ATS Resume Calculator to GitHub.

---

## 📋 Pre-Upload Checklist

Run preparation script:
```bash
python prepare_github.py
```

This will verify all essential files are present.

---

## 🚀 Upload Steps

### 1. Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `ats-resume-calculator`
3. Description: `AI-powered ATS resume analysis with role mismatch detection`
4. Visibility: Public or Private
5. **DO NOT** initialize with README (we have our own)
6. Click "Create repository"

### 2. Prepare Local Repository

```bash
# Navigate to project
cd D:\ATSsys\version_4

# Rename README for GitHub
move README_GITHUB.md README.md

# Initialize git
git init

# Add .gitignore first
git add .gitignore

# Add essential files
git add requirements_unified.txt
git add main.py download_models.py
git add README.md SETUP_GUIDE.md LICENSE
git add Dockerfile docker-compose.yml

# Add directories
git add app/
git add frontend_app/
git add knowledge_base/
git add utils/

# Commit
git commit -m "Initial commit: ATS Resume Calculator v4

Features:
- 15-dimensional scoring system
- Role mismatch detection with technical skill penalties
- Knowledge base with 18,168+ skills
- AI-powered semantic matching
- Technical vs soft skill categorization
- REST API with FastAPI
- Web interface with real-time analysis"
```

### 3. Push to GitHub

```bash
# Add remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/ats-resume-calculator.git

# Push to main branch
git branch -M main
git push -u origin main
```

---

## 📁 What Gets Uploaded

### ✅ Included Files
- `main.py` - Application entry point
- `requirements_unified.txt` - All dependencies
- `download_models.py` - ML model downloader
- `README.md` - Project documentation
- `SETUP_GUIDE.md` - Setup instructions
- `LICENSE` - MIT license
- `.gitignore` - Git ignore rules
- `Dockerfile` - Container configuration
- `docker-compose.yml` - Docker compose config
- `app/` - Core application code
- `frontend_app/` - Web interface
- `knowledge_base/` - Skills database (CSV/JSONL)
- `utils/` - Helper utilities

### ❌ Excluded Files (via .gitignore)
- `atsenv/`, `mvpenv/` - Virtual environments
- `models/` - ML models (too large, auto-download)
- `*.db` - Database files
- `*.log` - Log files
- `__pycache__/` - Python cache
- `test_*.py`, `debug_*.py` - Test/debug scripts
- `*.pyc`, `*.pyo` - Compiled Python

---

## 🔍 Verify Upload

After pushing, verify on GitHub:

1. **README displays correctly** with badges and formatting
2. **File structure is clean** - no test/debug files
3. **Requirements file is present** - `requirements_unified.txt`
4. **Setup guide is accessible** - `SETUP_GUIDE.md`
5. **License is visible** - `LICENSE`
6. **Docker files present** - `Dockerfile`, `docker-compose.yml`

---

## 📝 Update Repository Settings

### Add Topics (for discoverability)
Go to repository → About → Settings:
- `ats`
- `resume-parser`
- `nlp`
- `machine-learning`
- `fastapi`
- `python`
- `ai`
- `recruitment`
- `hiring`

### Add Description
```
AI-powered ATS resume analysis with role mismatch detection, semantic matching, and 15-dimensional scoring
```

### Add Website
```
https://your-deployment-url.com
```

---

## 🎯 Post-Upload Tasks

### 1. Create Release
```bash
git tag -a v1.0.0 -m "Release v1.0.0: Production-ready ATS Calculator"
git push origin v1.0.0
```

### 2. Add GitHub Actions (Optional)
Create `.github/workflows/test.yml` for CI/CD:
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements_unified.txt
      - run: python -m pytest tests/
```

### 3. Enable GitHub Pages (Optional)
For documentation hosting:
1. Settings → Pages
2. Source: Deploy from branch
3. Branch: main, folder: /docs

---

## 🐛 Troubleshooting

### Issue: Files too large
```bash
# Check file sizes
git ls-files -z | xargs -0 du -h | sort -h | tail -20

# Remove large files
git rm --cached large_file.bin
git commit -m "Remove large file"
```

### Issue: Wrong files committed
```bash
# Remove from git but keep locally
git rm --cached unwanted_file.py
git commit -m "Remove unwanted file"
```

### Issue: Need to update .gitignore
```bash
# After updating .gitignore
git rm -r --cached .
git add .
git commit -m "Update .gitignore"
```

---

## 📊 Repository Statistics

Expected repository size:
- **Code**: ~2-3 MB
- **Knowledge Base**: ~5-10 MB
- **Total**: ~10-15 MB

Models are NOT included (auto-download on first run).

---

## 🔐 Security Notes

Before uploading, ensure:
- [ ] No API keys or credentials in code
- [ ] No personal data in test files
- [ ] No sensitive configuration in .env files
- [ ] Database files excluded (.gitignore)
- [ ] Log files excluded (.gitignore)

---

## ✅ Final Checklist

- [ ] README.md displays correctly on GitHub
- [ ] SETUP_GUIDE.md is accessible
- [ ] requirements_unified.txt is present
- [ ] .gitignore excludes sensitive files
- [ ] No test/debug files in repository
- [ ] License file is present
- [ ] Docker files are included
- [ ] Repository description is set
- [ ] Topics are added
- [ ] First release is tagged

---

## 🎉 Success!

Your ATS Resume Calculator is now on GitHub!

Share the repository:
```
https://github.com/YOUR_USERNAME/ats-resume-calculator
```

Clone command for others:
```bash
git clone https://github.com/YOUR_USERNAME/ats-resume-calculator.git
cd ats-resume-calculator
```

---

**Need help?** Check [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed setup instructions.
