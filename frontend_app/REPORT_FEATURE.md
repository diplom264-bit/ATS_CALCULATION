# AI-Powered Report Generation Feature

## Overview
Standalone feature that generates personalized DOCX reports using Ollama (8b model).

## Features

### 1. AI-Generated Content
- Uses Ollama `llama3.2:3b` model
- Generates personalized analysis based on:
  - Resume data (name, skills, experience)
  - Analysis scores and breakdown
  - Recommendations

### 2. Report Sections
- **Candidate Information**: Name, email, date
- **Score Summary**: Overall score and grade
- **Detailed Breakdown**: All 12 checker scores
- **AI Analysis**: 
  - Executive Summary
  - Strengths
  - Areas for Improvement
  - Next Steps
- **Key Recommendations**: Top 5 actionable items

### 3. Fallback Mechanism
- If Ollama unavailable, uses template-based report
- Ensures feature always works
- No impact on core functionality

## Setup

### Install Ollama
```bash
# Download from https://ollama.ai
ollama pull llama3.2:3b
ollama serve
```

### Install Dependencies
```bash
pip install python-docx requests
```

## Usage

1. Complete resume analysis
2. Click "Download Detailed Report (DOCX)"
3. Report generates with AI insights
4. Downloads automatically

## Architecture

```
User clicks download
    ↓
Frontend sends resume + analysis data
    ↓
Backend calls report_generator.py
    ↓
Ollama generates personalized content
    ↓
DOCX created with formatting
    ↓
File downloaded to user
```

## Files

- `report_generator.py` - Standalone module
- `api_server.py` - Added `/api/generate-report` endpoint
- `templates/index.html` - Added download button

## Standalone Design

✅ **No core dependencies**: Works independently
✅ **Graceful degradation**: Fallback if Ollama down
✅ **Optional feature**: Core app works without it
✅ **Error isolation**: Failures don't affect analysis

## Example Report

```
ATS RESUME ANALYSIS REPORT

Candidate Information
Name: John Doe
Email: john@example.com
Analysis Date: 2024-01-15

Score Summary
Overall Score: 75/100
Grade: C

Detailed Breakdown
• File Layout: 85.0/100
• Semantic Fit: 65.0/100
...

AI-Generated Analysis
EXECUTIVE SUMMARY
Your resume shows strong technical skills but needs quantifiable achievements...

STRENGTHS
• Clear professional formatting
• Relevant technical skills
• Consistent work history

AREAS FOR IMPROVEMENT
• Add metrics to achievements (%, $, numbers)
• Include more job-specific keywords
• Enhance action verbs

NEXT STEPS
1. Review recommendations
2. Tailor for each application
3. Add measurable results
```

## Performance

- Report generation: 5-10 seconds (with Ollama)
- Fallback: <1 second
- File size: ~50KB typical

## Production Notes

- Ensure Ollama running: `ollama serve`
- Model loaded: `ollama pull llama3.2:3b`
- Timeout: 30 seconds for AI generation
- Falls back gracefully if unavailable
