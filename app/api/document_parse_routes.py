"""
Document parsing API - Convert PDF/images to structured JSON
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
import sys
import tempfile
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from services.file_parser import FileParser
from services.llm_document_structurer import LLMDocumentStructurer
from services.ocr_client import OCRClient

router = APIRouter(prefix="/api/v1/document", tags=["Document Parsing"])

structurer = LLMDocumentStructurer()
ocr_client = OCRClient()

@router.post("/parse-resume")
async def parse_resume(file: UploadFile = File(...)):
    """Parse resume file to structured JSON"""
    try:
        # Save uploaded file temporarily
        temp_path = os.path.join(tempfile.gettempdir(), file.filename)
        with open(temp_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        # Extract text
        result = FileParser.parse(temp_path)
        text = result.get('text', '')
        
        # If text extraction failed or too short, try OCR
        if len(text) < 100:
            await file.seek(0)
            ocr_result = await ocr_client.extract_text(file)
            if ocr_result['status'] == 'ok':
                text = ocr_result['text']
                layout_regions = ocr_result['layout']['regions']
            else:
                layout_regions = None
        else:
            layout_regions = None
        
        # Structure the document
        structured = structurer.structure_resume(text)
        
        os.remove(temp_path)
        
        return {
            "status": "ok",
            "data": structured,
            "text_length": len(text)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/parse-jd")
async def parse_jd(file: UploadFile = File(...)):
    """Parse job description file to structured JSON"""
    try:
        # Save uploaded file temporarily
        temp_path = os.path.join(tempfile.gettempdir(), file.filename)
        with open(temp_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        # Extract text
        result = FileParser.parse(temp_path)
        text = result.get('text', '')
        
        # If text extraction failed, try OCR
        if len(text) < 100:
            await file.seek(0)
            ocr_result = await ocr_client.extract_text(file)
            if ocr_result['status'] == 'ok':
                text = ocr_result['text']
                layout_regions = ocr_result['layout']['regions']
            else:
                layout_regions = None
        else:
            layout_regions = None
        
        # Structure the document
        structured = structurer.structure_jd(text)
        
        os.remove(temp_path)
        
        return {
            "status": "ok",
            "data": structured,
            "text_length": len(text)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/parse-and-analyze")
async def parse_and_analyze(
    resume_file: UploadFile = File(...),
    jd_file: UploadFile = File(...)
):
    """Parse both files and return structured data ready for analysis"""
    try:
        # Parse resume
        resume_temp = os.path.join(tempfile.gettempdir(), resume_file.filename)
        with open(resume_temp, 'wb') as f:
            f.write(await resume_file.read())
        
        resume_result = FileParser.parse(resume_temp)
        resume_text = resume_result.get('text', '')
        resume_data = structurer.structure_resume(resume_text)
        os.remove(resume_temp)
        
        # Parse JD
        jd_temp = os.path.join(tempfile.gettempdir(), jd_file.filename)
        with open(jd_temp, 'wb') as f:
            f.write(await jd_file.read())
        
        jd_result = FileParser.parse(jd_temp)
        jd_text = jd_result.get('text', '')
        jd_data = structurer.structure_jd(jd_text)
        os.remove(jd_temp)
        
        return {
            "status": "ok",
            "resume": resume_data,
            "job_description": jd_data,
            "ready_for_analysis": True
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
