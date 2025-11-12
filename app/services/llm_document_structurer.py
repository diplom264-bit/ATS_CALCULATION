"""
LLM-powered document structurer for production-grade JSON extraction
Uses Claude/GPT to extract structured data matching ground truth format
"""
import json
import os
from typing import Dict, Any
from .llm_cache import LLMCache

class LLMDocumentStructurer:
    """Production-grade document structuring using LLM with caching"""
    
    def __init__(self):
        self.cache = LLMCache(cache_dir="llm_cache", ttl_hours=24)
    
    RESUME_SCHEMA = {
        "personal_information": {
            "name": "string",
            "location": "string",
            "phone": "string",
            "email": "string",
            "linkedin": "string (optional)"
        },
        "summary": "string",
        "experience": [{
            "organization": "string",
            "title": "string",
            "location": "string",
            "period": {"start": "YYYY-MM", "end": "YYYY-MM or Present"},
            "projects": [{
                "client": "string (optional)",
                "achievements": ["string"]
            }]
        }],
        "technical_skills": {
            "category_name": ["skill1", "skill2"]
        },
        "education": [{
            "degree": "string",
            "institution": "string",
            "location": "string",
            "duration": "string"
        }],
        "certifications": [{
            "title": "string",
            "issuer": "string",
            "year": "int"
        }],
        "languages": ["string"],
        "availability": "string (optional)"
    }
    
    JD_SCHEMA = {
        "position": "string",
        "experience_required": "string",
        "education_required": "string",
        "location": "string",
        "responsibilities": ["string"],
        "required_skills": ["individual skill keywords like 'Power BI', 'SQL', 'Python'"],
        "preferred_skills": ["individual skill keywords"],
        "qualifications": ["string"],
        "soft_skills": ["individual soft skills like 'Communication', 'Problem Solving'"]
    }
    
    def structure_resume(self, text: str) -> Dict[str, Any]:
        """Extract structured resume data using LLM with caching"""
        
        # Check cache first
        cached = self.cache.get(text, "resume")
        if cached:
            print("✅ Using cached resume (0.1s)")
            return cached
        
        print("⏳ Parsing resume with LLM (~30s)...")
        prompt = f"""Extract structured information from this resume text and return ONLY valid JSON matching this exact schema:

{json.dumps(self.RESUME_SCHEMA, indent=2)}

Resume Text:
{text}

Requirements:
1. Extract ALL information accurately
2. Use exact field names from schema
3. Format dates as YYYY-MM
4. Categorize technical skills by type (business_intelligence, data_visualization, languages_expressions, etl_data_engineering, performance_security, platforms_systems)
5. Include all achievements and projects
6. Return ONLY the JSON, no explanations

JSON:"""
        
        # Call LLM API
        structured_data = self._call_llm(prompt)
        
        # Cache result
        if structured_data:
            self.cache.set(text, "resume", structured_data)
        
        return structured_data
    
    def structure_jd(self, text: str) -> Dict[str, Any]:
        """Extract structured JD data using LLM with caching"""
        
        # Check cache first
        cached = self.cache.get(text, "jd")
        if cached:
            print("✅ Using cached JD (0.1s)")
            return cached
        
        print("⏳ Parsing JD with LLM (~15s)...")
        prompt = f"""Extract structured information from this job description and return ONLY valid JSON matching this exact schema:

{json.dumps(self.JD_SCHEMA, indent=2)}

Job Description Text:
{text}

CRITICAL REQUIREMENTS:
1. Extract individual skill KEYWORDS only (e.g., "Power BI", "SQL", "Python", "Tableau")
2. DO NOT include full sentences in required_skills or preferred_skills
3. Extract atomic skills from sentences like "Experience with ETL tools" → ["ETL"]
4. For "BI tools such as Tableau, Qlik" → ["Tableau", "Qlik", "Power BI"]
5. Separate technical skills from soft skills
6. Use exact field names from schema
7. Return ONLY the JSON, no explanations

JSON:"""
        
        structured_data = self._call_llm(prompt)
        
        # Cache result
        if structured_data:
            self.cache.set(text, "jd", structured_data)
        
        return structured_data
    
    def _call_llm(self, prompt: str) -> Dict[str, Any]:
        """Call LLM API to extract structured data"""
        
        # Option 1: Use Ollama (Zero Cost)
        try:
            import requests
            
            print(f"Calling Ollama... (this may take 5-10 seconds)")
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'llama3:latest',
                    'prompt': prompt,
                    'stream': False
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('response', '{}')
                print(f"Ollama response length: {len(content)} chars")
                
                # Extract JSON from response
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    parsed = json.loads(json_str)
                    print(f"Successfully parsed JSON with {len(parsed)} fields")
                    return parsed
                else:
                    print(f"No JSON found in response: {content[:200]}")
            else:
                print(f"Ollama error: {response.status_code} - {response.text}")
            
        except Exception as e:
            print(f"Ollama error: {e}")
        
        # Fallback: Return empty structure
        print("Returning empty structure")
        return {}
