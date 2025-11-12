# Frontend Testing Guide - Role Validation

## What Was Fixed

### 1. **Double Normalization Issue** ✅
- **Problem**: Scores were being normalized twice, flattening differences
- **Fix**: Keep original weighted scores from PerfectAnalysisEngine
- **Result**: Good resumes score high (80-90), bad resumes score low (30-50)

### 2. **Role Mismatch Detection** ✅
- **Problem**: .NET developer could pass for Power BI role
- **Fix**: Added critical keyword validation with TF-IDF
- **Result**: Mismatched roles score <5/20 on semantic fit

## How to Test

### Start Server
```bash
cd D:\ATSsys\version_4\frontend_app
python api_server.py
```
Open browser: http://localhost:8001

### Test Scenarios

#### Scenario 1: Role Mismatch (Should FAIL)
**JD**: Power BI Developer
```
Power BI Developer needed
Skills: Power BI Desktop, DAX, Power Query, SQL Server, SSAS
Experience with data modeling and ETL
```

**Resume**: .NET Developer
- Upload any .NET developer resume
- **Expected Score**: <30/100 (Grade F)
- **Semantic Fit**: <5/20
- **Feedback**: "Critical mismatch - missing: power bi, dax, power query"

#### Scenario 2: Good Match (Should PASS)
**JD**: Python Developer
```
Python Developer with Django experience
Skills: Python, Django, REST APIs, PostgreSQL, Docker
```

**Resume**: Python Developer
- Upload Python developer resume with matching skills
- **Expected Score**: 70-90/100 (Grade B-A)
- **Semantic Fit**: 15-20/20
- **Feedback**: "Strong match"

#### Scenario 3: Partial Match (Should be MODERATE)
**JD**: Senior Full Stack Developer
```
Full Stack Developer
Frontend: React, TypeScript, CSS
Backend: Node.js, Express, MongoDB
```

**Resume**: Frontend Developer (only React/TypeScript)
- **Expected Score**: 50-65/100 (Grade D-C)
- **Semantic Fit**: 8-12/20
- **Feedback**: "Moderate match - missing backend skills"

## Key Metrics to Verify

### Score Breakdown Display
- **File Layout**: 0-100 (normalized for display)
- **Semantic Fit**: 0-100 (most important - 25% weight)
- **Keyword Alignment**: 0-100 (15% weight)
- **Quantified Impact**: 0-100 (15% weight)

### Final Score Calculation
- Uses original weighted score from PerfectAnalysisEngine
- NOT recalculated by AdaptiveScorer
- Properly discriminates between good/bad fits

### Grade Distribution
- **A (90-100)**: Perfect match, all criteria met
- **B (80-89)**: Strong match, minor improvements needed
- **C (70-79)**: Good match, some gaps
- **D (60-69)**: Moderate match, significant gaps
- **F (<60)**: Poor match or wrong role

## Expected Behavior

✅ **Correct**:
- .NET dev → Power BI JD = F (20-30/100)
- Power BI dev → Power BI JD = A-B (85-95/100)
- Python dev → Python JD = B (75-85/100)

❌ **Incorrect** (old behavior):
- Everything scoring D (60-65/100)
- No discrimination between roles
- Mismatched roles passing

## Report Generation

After analysis, click "Download Report" to get:
- Detailed score breakdown with point deductions
- AI-generated insights (via Ollama if running)
- Personalized recommendations based on weaknesses
- Score impact summary

## Troubleshooting

### Port Already in Use
- Change port in `api_server.py` line 172: `port=8001` → `port=8002`

### Ollama Not Running
- Report generation falls back to template-based recommendations
- No error, just less personalized feedback

### KB Loading Slow
- First load takes ~2-3 seconds (loads 17,326 skills)
- Subsequent requests are instant (singleton pattern)

## Success Criteria

✅ Different roles get different scores
✅ Mismatched roles score <40/100
✅ Good matches score >75/100
✅ Semantic fit properly discriminates
✅ Keyword alignment catches missing terms
✅ Report downloads successfully
