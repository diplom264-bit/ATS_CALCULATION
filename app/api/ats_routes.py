"""
ATS Analysis API Routes
Complete resume analysis with scoring
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import tempfile
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from services.ats_analyzer import ATSAnalyzer
from services.file_parser import FileParser

router = APIRouter(prefix="/api/v1/ats", tags=["ATS Analysis"])

analyzer = ATSAnalyzer()

@router.post("/analyze-resume")
async def analyze_resume(
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(None)
):
    """
    Complete ATS resume analysis
    
    - Extracts entities (name, email, phone, skills, etc.)
    - Calculates ATS compatibility score
    - Provides job-fit matching if JD provided
    - Returns actionable recommendations
    """
    try:
        # Save and parse file
        temp_path = os.path.join(tempfile.gettempdir(), file.filename)
        with open(temp_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        # Extract text
        parse_result = FileParser.parse(temp_path)
        resume_text = parse_result.get('text', '')
        
        os.remove(temp_path)
        
        if not resume_text or len(resume_text) < 50:
            raise HTTPException(
                status_code=400, 
                detail="Could not extract text from resume. File may be corrupted or empty."
            )
        
        # Analyze
        result = analyzer.analyze_resume(temp_path, resume_text, job_description)
        
        return {
            "status": "success",
            "data": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/quick-score")
async def quick_score(file: UploadFile = File(...)):
    """
    Quick ATS score without job description
    Returns basic compatibility score
    """
    try:
        temp_path = os.path.join(tempfile.gettempdir(), file.filename)
        with open(temp_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        parse_result = FileParser.parse(temp_path)
        resume_text = parse_result.get('text', '')
        os.remove(temp_path)
        
        if not resume_text or len(resume_text) < 50:
            raise HTTPException(status_code=400, detail="Could not extract text from resume")
        
        result = analyzer.analyze_resume(temp_path, resume_text)
        
        return {
            "status": "success",
            "score": result["score"],
            "grade": result["grade"],
            "analysis": result["analysis"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring failed: {str(e)}")

@router.get("/health")
async def health_check():
    """Check if ATS analyzer is ready"""
    ml_scorer = analyzer.analyzer.ml_scorer
    return {
        "status": "healthy",
        "analyzer": "MLEnhancedAnalyzer",
        "ml_components": {
            "cross_encoder": ml_scorer.cross_encoder is not None,
            "sbert": ml_scorer.embedder is not None,
            "lightgbm": ml_scorer.rank_model is not None
        },
        "scoring": "70% rule-based + 30% ML fusion"
    }
