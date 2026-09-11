from typing import Dict, Any, List
from .ai.factory import get_ai_provider

def generate_questions(profile: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
    ai = get_ai_provider()
    return ai.generate_interview_questions(profile, job)

def evaluate_interview_answer(question: str, answer: str, context: Dict[str, Any]) -> Dict[str, Any]:
    ai = get_ai_provider()
    return ai.evaluate_interview_step(question, answer, context)

def finalize_mock_interview(transcript: List[Dict[str, Any]], profile: Dict[str, Any]) -> Dict[str, Any]:
    ai = get_ai_provider()
    return ai.summarize_mock_interview(transcript, profile)
