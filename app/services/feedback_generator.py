"""
Small LLM for Human-Like Feedback Generation
Model: Phi-3-mini-4k-instruct (3.8B parameters)
"""
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
from pathlib import Path
from typing import Dict, List

class FeedbackGenerator:
    """Small LLM for generating actionable feedback"""
    
    def __init__(self, model_cache_dir="models/feedback_llm"):
        self.device = 0 if torch.cuda.is_available() else -1
        self.model_cache_dir = Path(model_cache_dir)
        self.model_cache_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🔧 Loading Feedback LLM (device: {'cuda' if self.device == 0 else 'cpu'})...")
        
        model_name = "microsoft/Phi-3-mini-4k-instruct"
        if (self.model_cache_dir / "config.json").exists():
            print("✅ Using cached Feedback LLM")
            self.generator = pipeline(
                "text-generation",
                model=str(self.model_cache_dir),
                device=self.device,
                max_new_tokens=200,
                do_sample=True,
                temperature=0.7
            )
        else:
            print("📥 Downloading Feedback LLM (~7GB)...")
            tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
            model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)
            
            tokenizer.save_pretrained(str(self.model_cache_dir))
            model.save_pretrained(str(self.model_cache_dir))
            print(f"💾 Feedback LLM cached to {self.model_cache_dir}")
            
            self.generator = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                device=self.device,
                max_new_tokens=200,
                do_sample=True,
                temperature=0.7
            )
        
        print(f"✅ Feedback LLM ready (GPU: {torch.cuda.is_available()})")
    
    def generate_feedback(self, analysis: Dict) -> List[str]:
        """
        Generate 2-3 actionable feedback points
        
        Args:
            analysis: {
                "final_score": 78.5,
                "missing_skills": ["SQL", "Tableau"],
                "weak_factors": ["readability", "keyword_match"]
            }
        
        Returns:
            ["Tip 1", "Tip 2", "Tip 3"]
        """
        score = analysis.get("final_score", 0)
        missing = analysis.get("missing_skills", [])
        weak = analysis.get("weak_factors", [])
        
        prompt = f"""You are an expert resume coach. Based on this analysis, provide 2-3 specific, actionable tips to improve the resume.

Score: {score}/100
Missing Skills: {', '.join(missing[:5])}
Weak Areas: {', '.join(weak)}

Provide exactly 3 bullet points starting with "•". Be specific and actionable.

Tips:"""
        
        try:
            result = self.generator(prompt, max_new_tokens=200, do_sample=True, temperature=0.7)
            text = result[0]['generated_text'].split("Tips:")[1].strip()
            
            # Extract bullet points
            tips = [line.strip() for line in text.split("•") if line.strip()]
            return tips[:3]
        except:
            # Fallback to rule-based feedback
            return self._fallback_feedback(analysis)
    
    def _fallback_feedback(self, analysis: Dict) -> List[str]:
        """Rule-based fallback if LLM fails"""
        tips = []
        
        missing = analysis.get("missing_skills", [])
        if missing:
            tips.append(f"Add these {len(missing)} missing skills: {', '.join(missing[:3])}")
        
        weak = analysis.get("weak_factors", [])
        if "readability" in weak:
            tips.append("Simplify your language for better readability (target 8th-9th grade level)")
        if "ats_format" in weak:
            tips.append("Remove tables and special characters for better ATS compatibility")
        if "keyword_match" in weak:
            tips.append("Include more keywords from the job description throughout your resume")
        
        return tips[:3]
