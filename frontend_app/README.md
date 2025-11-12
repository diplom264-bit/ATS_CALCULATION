# ATS Intelligence Engine - Frontend

## Quick Start

### 1. Start Server
```bash
# Windows
START_SERVER.bat

# Or manually
python api_server.py
```

### 2. Open Browser
```
http://localhost:8000
```

## Features

### Step 1: Job Description
- Paste or upload JD text
- Auto-parse key requirements
- Edit and validate before publishing

### Step 2: Resume Upload
- Upload PDF/DOCX resume
- Auto-extract: name, email, phone, skills, experience
- Edit extracted data before analysis

### Step 3: Analysis
- 12 comprehensive checks
- Real-time scoring
- Detailed breakdown by category
- Actionable recommendations

## Tech Stack

**Backend**: FastAPI + Python
**Frontend**: Vanilla JS (no framework needed)
**ML Engine**: Existing ML-Enhanced Analyzer
**Design**: Minimal, gradient-based UI matching logo

## API Endpoints

- `GET /` - Main interface
- `POST /api/parse-jd` - Parse job description
- `POST /api/parse-resume` - Extract resume data
- `POST /api/analyze` - Full analysis

## Workflow

```
1. User pastes JD → Parse → Review → Publish
2. User uploads resume → Parse → Review → Publish
3. System analyzes → Display results
```

## Performance

- KB preloaded at startup (2s one-time)
- Analysis: <1s per resume
- Real-time UI updates
- No page reloads

## Design

- Gradient purple theme matching AR logo
- Clean, minimal interface
- Step-by-step progress indicator
- Editable forms for validation
- Visual score cards and breakdowns
