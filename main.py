from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import tempfile
import shutil
import json
import sys
from uuid import uuid4
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

app = FastAPI(
    title="ATS Resume Calculator - ML Enhanced",
    description="AI/ML-powered resume analysis with 7-layer architecture",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="frontend_app/static"), name="static")
except:
    pass

# Initialize ML analyzer and database
from app.services.ml_enhanced_analyzer import MLEnhancedAnalyzer
from app.database.db_manager import DatabaseManager

analyzer = MLEnhancedAnalyzer()
db = DatabaseManager()

# Include ATS Analysis API (ML-Enhanced)
from app.api.ats_routes import router as ats_router
app.include_router(ats_router)
print("✅ ATS Analysis API loaded (ML-Enhanced)")

# Include JSON Analysis Engine
try:
    from app.api.json_analysis_routes import router as json_analysis_router
    app.include_router(json_analysis_router)
    print("✅ JSON Analysis Engine loaded")
except Exception as e:
    print(f"⚠️  JSON Analysis not available: {e}")

# Include Document Parsing API
try:
    from app.api.document_parse_routes import router as document_parse_router
    app.include_router(document_parse_router)
    print("✅ Document Parsing API loaded")
except Exception as e:
    print(f"⚠️  Document Parsing not available: {e}")

# Frontend routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve main frontend"""
    from fastapi.responses import Response
    try:
        with open("frontend_app/templates/index.html", encoding='utf-8') as f:
            content = f.read()
        return Response(
            content=content,
            media_type="text/html",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    except:
        return HTMLResponse("""
        <html><body>
        <h1>ATS Resume Calculator - ML Enhanced</h1>
        <p>API Documentation: <a href="/docs">/docs</a></p>
        <p>Health Check: <a href="/health">/health</a></p>
        </body></html>
        """)

@app.post("/api/parse-jd")
async def parse_jd(jd_text: str = Form(...)):
    """Parse job description"""
    try:
        lines = [l.strip() for l in jd_text.split('\n') if l.strip()]
        return JSONResponse({
            "status": "ok",
            "data": {
                "title": lines[0] if lines else "Job Title",
                "description": jd_text,
                "requirements": [l for l in lines if any(k in l.lower() for k in ['required', 'must', 'experience', 'skill'])],
                "raw_text": jd_text
            }
        })
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)}, status_code=500)

@app.post("/api/parse-resume")
async def parse_resume(file: UploadFile = File(...)):
    """Parse resume file"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        
        result = analyzer.parser.parse(tmp_path)
        Path(tmp_path).unlink()
        
        if result['status'] != 'ok':
            return JSONResponse({"status": "error", "error": result.get('error')}, status_code=500)
        
        return JSONResponse({
            "status": "ok",
            "data": {
                "name": result['name'],
                "email": result['email'],
                "phone": result['phone'],
                "linkedin": result['linkedin'],
                "skills": result['skills'],
                "companies": result['companies'],
                "job_titles": result['job_titles'],
                "degrees": result['degrees']
            }
        })
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)}, status_code=500)

@app.post("/api/parse-jd-file")
async def parse_jd_file(file: UploadFile = File(...)):
    """Parse JD from file"""
    try:
        import fitz
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        
        doc = fitz.open(tmp_path)
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        Path(tmp_path).unlink()
        
        return JSONResponse({"status": "ok", "text": text})
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)}, status_code=500)

@app.post("/api/analyze")
async def analyze(
    resume_file: UploadFile = File(...),
    jd_text: str = Form(...),
    resume_data: str = Form(...)
):
    """Analyze resume against JD"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(resume_file.filename).suffix) as tmp:
            shutil.copyfileobj(resume_file.file, tmp)
            tmp_path = tmp.name
        
        result = analyzer.analyze(tmp_path, jd_text)
        Path(tmp_path).unlink()
        
        if result['status'] != 'ok':
            return JSONResponse({"status": "error", "error": result.get('error')}, status_code=500)
        
        # Extract skill matching details
        analysis = result.get('analysis', {})
        skill_details = analysis.get('skill_match_details', {})
        
        return JSONResponse({
            "status": "ok",
            "data": {
                "extraction": result['extraction'],
                "analysis": result['analysis'],
                "semantic_score": result.get('semantic_score'),
                "ml_score": result.get('ml_score'),
                "ml_explanation": result.get('ml_explanation'),
                "enhanced_feedback": [],  # Disabled - too generic
                "summary": result.get('summary', ''),
                "skill_match_details": skill_details
            }
        })
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)}, status_code=500)

@app.post("/api/generate-report")
async def generate_report(
    data: str = Form(...),
    resume_text: str = Form(None),
    jd_text: str = Form(None)
):
    """Generate personalized DOCX report"""
    try:
        from frontend_app.report_generator import create_docx_report
        
        report_data = json.loads(data)
        resume_data = report_data.get('resume', {})
        analysis_data = report_data.get('analysis', {})
        
        # Add context for AI generation
        analysis_data['_resume_text'] = resume_text or ''
        analysis_data['_jd_text'] = jd_text or ''
        
        output_path = tempfile.mktemp(suffix='.docx')
        create_docx_report(resume_data, analysis_data, output_path)
        
        return FileResponse(
            output_path,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            filename=f"ATS_Report_{resume_data.get('name', 'Resume').replace(' ', '_')}.docx"
        )
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)}, status_code=500)

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "analyzer_loaded": analyzer is not None,
        "scoring": "Hybrid rule-based + ML fusion"
    }

@app.post("/api/upload-jd")
async def upload_jd(file: UploadFile = File(None), jd_text: str = Form(None)):
    """Upload JD and create session"""
    try:
        # Parse JD from file or text
        if file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
                shutil.copyfileobj(file.file, tmp)
                tmp_path = tmp.name
            
            if file.filename.endswith('.docx'):
                from docx import Document
                doc = Document(tmp_path)
                text = '\n'.join([p.text for p in doc.paragraphs if p.text.strip()])
            else:
                with open(tmp_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            Path(tmp_path).unlink()
        else:
            text = jd_text
        
        # Generate IDs
        jd_id = str(uuid4())
        session_id = str(uuid4())
        
        # Save to database
        db.save_jd({
            'jd_id': jd_id,
            'session_id': session_id,
            'text': text,
            'title': text.split('\n')[0][:100] if text else 'Job Opening'
        })
        
        return JSONResponse({
            "status": "ok",
            "jd_id": jd_id,
            "session_id": session_id,
            "message": "JD uploaded successfully"
        })
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)}, status_code=500)

@app.post("/api/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    jd_id: str = Form(...),
    session_id: str = Form(...),
    jd_text: str = Form(None)
):
    """Upload resume and link to JD session"""
    try:
        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        
        # Parse resume
        parsed = analyzer.parser.parse(tmp_path)
        if parsed['status'] != 'ok':
            Path(tmp_path).unlink()
            return JSONResponse({"status": "error", "error": parsed.get('error')}, status_code=500)
        
        # Get JD text if not provided
        if not jd_text:
            jd_data = db.get_jd(jd_id)
            jd_text = jd_data['text'] if jd_data else ''
        
        # Analyze
        preprocessed = analyzer.parser.preprocessor.process(tmp_path)
        resume_text = preprocessed.get('clean_text', '')
        result = analyzer.analyze(tmp_path, jd_text)
        Path(tmp_path).unlink()
        
        if result['status'] != 'ok':
            return JSONResponse({"status": "error", "error": result.get('error')}, status_code=500)
        
        # Generate resume ID
        resume_id = str(uuid4())
        
        # Save resume
        db.save_resume({
            'resume_id': resume_id,
            'jd_id': jd_id,
            'session_id': session_id,
            'name': parsed['name'],
            'email': parsed['email'],
            'phone': parsed['phone'],
            'skills': parsed['skills'],
            'experience_years': 0,
            'roles': parsed['job_titles'],
            'education': parsed['degrees'],
            'text': resume_text
        })
        
        # Save match result
        analysis = result['analysis']
        db.save_match(jd_id, resume_id, {
            'session_id': session_id,
            'match_score': analysis['final_score'],
            'grade': analysis['grade'],
            'breakdown': analysis['breakdown'],
            'semantic_score': result.get('semantic_score'),
            'ml_score': result.get('ml_score'),
            'matched_skills': result.get('skill_match_details', {}).get('matched', []),
            'missing_skills': result.get('skill_match_details', {}).get('missing', [])
        })
        
        return JSONResponse({
            "status": "ok",
            "resume_id": resume_id,
            "score": analysis['final_score'],
            "grade": analysis['grade'],
            "name": parsed['name']
        })
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)}, status_code=500)

@app.get("/api/batch-results/{jd_id}")
async def batch_results(jd_id: str):
    """Get all results for a JD"""
    try:
        results = db.get_batch_results(jd_id)
        
        # Parse match_data JSON
        for r in results:
            if 'match_data' in r and isinstance(r['match_data'], str):
                r['match_data'] = json.loads(r['match_data'])
        
        return JSONResponse({
            "status": "ok",
            "jd_id": jd_id,
            "total": len(results),
            "results": results
        })
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)}, status_code=500)

@app.get("/api/batch-results/session/{session_id}")
async def batch_results_by_session(session_id: str):
    """Get all results for a session"""
    try:
        results = db.get_batch_results_by_session(session_id)
        
        # Parse match_data JSON
        for r in results:
            if 'match_data' in r and isinstance(r['match_data'], str):
                r['match_data'] = json.loads(r['match_data'])
        
        return JSONResponse({
            "status": "ok",
            "session_id": session_id,
            "total": len(results),
            "results": results
        })
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)}, status_code=500)

@app.get("/api")
async def api_info():
    return {
        "message": "ATS Resume Calculator - ML Enhanced",
        "version": "2.0.0",
        "features": [
            "ML-Enhanced Scoring (Cross-Encoder + LightGBM)",
            "7-Layer Analysis Architecture",
            "Knowledge Base Integration (17,326 skills)",
            "Adaptive Context-Aware Scoring",
            "Role Mismatch Detection",
            "Batch Processing with Session Tracking"
        ],
        "endpoints": {
            "frontend": "/",
            "analyze": "/api/analyze",
            "upload_jd": "/api/upload-jd",
            "upload_resume": "/api/upload-resume",
            "batch_results": "/api/batch-results/{jd_id}",
            "batch_results_session": "/api/batch-results/session/{session_id}",
            "parse_resume": "/api/parse-resume",
            "parse_jd": "/api/parse-jd",
            "generate_report": "/api/generate-report",
            "health": "/health",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*80)
    print("🚀 ATS Resume Calculator - ML Enhanced")
    print("="*80)
    print("🌐 Frontend: http://127.0.0.1:8008/")
    print("📊 Features: 7-layer ML architecture, 395D feature space")
    print("🤖 ML Models: Cross-Encoder + LightGBM + SBERT")
    print("📚 Knowledge Base: 17,326 skills")
    print("🔗 API Docs: http://127.0.0.1:8008/docs")
    print("💚 Health: http://127.0.0.1:8008/health")
    print("="*80 + "\n")
    uvicorn.run(app, host="127.0.0.1", port=8008)
