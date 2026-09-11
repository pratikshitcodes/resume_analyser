from typing import Dict, Any
from .ai.factory import get_ai_provider

def analyze_resume_ats(profile: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
    ai = get_ai_provider()
    analysis = ai.analyze_ats(profile, raw_text)
    
    # Ensure all required fields are present
    return {
        "ats_score": int(analysis.get("ats_score", 75)),
        "strengths": analysis.get("strengths", ["Clear technical skills", "Relevant project experience"]),
        "weaknesses": analysis.get("weaknesses", ["Could add more quantifiable outcomes"]),
        "suggestions": analysis.get("suggestions", ["Add metrics and impact statements to projects"]),
        "best_project_analysis": analysis.get("best_project_analysis", "The primary technical project demonstrates solid architectural design and execution.")
    }
