"""FastAPI Server for ATS Frontend"""
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path
import tempfile
import shutil
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.ml_enhanced_analyzer import MLEnhancedAnalyzer
from app.startup import initialize_app

app = FastAPI(title="ATS Intelligence Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize KB at startup
@app.on_event("startup")
async def startup():
    initialize_app()

analyzer = MLEnhancedAnalyzer()

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("templates/index.html", encoding='utf-8') as f:
        return f.read()

@app.post("/api/parse-jd")
async def parse_jd(jd_text: str = Form(...)):
    """Parse job description text"""
    try:
        # Simple JD parsing - extract key info
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
        import json
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(resume_file.filename).suffix) as tmp:
            shutil.copyfileobj(resume_file.file, tmp)
            tmp_path = tmp.name
        
        result = analyzer.analyze(tmp_path, jd_text)
        Path(tmp_path).unlink()
        
        if result['status'] != 'ok':
            return JSONResponse({"status": "error", "error": result.get('error')}, status_code=500)
        
        return JSONResponse({
            "status": "ok",
            "data": {
                "extraction": result['extraction'],
                "analysis": result['analysis'],
                "semantic_score": result['semantic_score'],
                "enhanced_feedback": result['enhanced_feedback'],
                "summary": result['summary']
            }
        })
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)}, status_code=500)

@app.post("/api/generate-report")
async def generate_report(data: str = Form(...)):
    """Generate detailed DOCX report using Ollama"""
    try:
        from report_generator import create_docx_report
        
        report_data = json.loads(data)
        resume_data = report_data.get('resume', {})
        analysis_data = report_data.get('analysis', {})
        
        output_path = tempfile.mktemp(suffix='.docx')
        create_docx_report(resume_data, analysis_data, output_path)
        
        return FileResponse(
            output_path,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            filename=f"ATS_Report_{resume_data.get('name', 'Resume').replace(' ', '_')}.docx"
        )
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    print("\n🌐 Server starting at http://localhost:8001")
    print("📊 Open browser to test the frontend\n")
    uvicorn.run(app, host="0.0.0.0", port=8001)
