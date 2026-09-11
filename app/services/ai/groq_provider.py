import json
import re
from typing import Dict, Any, List
from groq import Groq
from .base import AIProvider
from ...core.config import settings

class GroqProvider(AIProvider):
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.DEFAULT_MODEL
        if self.api_key:
            self.client = Groq(api_key=self.api_key)
        else:
            self.client = None

    def _call_llm_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        if not self.client:
            raise ValueError("Groq API Key is missing. Please set GROQ_API_KEY in .env.")
        
        messages = [
            {"role": "system", "content": system_prompt + "\nIMPORTANT: You must return pure, valid JSON ONLY. No markdown wrappers, no backticks."},
            {"role": "user", "content": user_prompt}
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.1
        )
        content = response.choices[0].message.content
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Fallback regex JSON extractor
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise ValueError(f"Failed to decode LLM JSON output: {content}")

    def _call_llm_text(self, system_prompt: str, messages_list: List[Dict[str, str]]) -> str:
        if not self.client:
            raise ValueError("Groq API Key is missing. Please set GROQ_API_KEY in .env.")
        
        messages = [{"role": "system", "content": system_prompt}] + messages_list
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3
        )
        return response.choices[0].message.content

    def extract_profile(self, raw_text: str) -> Dict[str, Any]:
        system_prompt = """You are an expert AI Resume Parser. Extract all structured information from the provided resume text into a strictly formatted JSON object.
Schema:
{
  "name": "Candidate Name",
  "contact_info": {"email": "...", "phone": "...", "linkedin": "...", "github": "...", "portfolio": "..."},
  "skills": ["Skill1", "Skill2", ...],
  "experience": [{"company": "...", "role": "...", "duration": "...", "description": "..."}],
  "education": [{"degree": "...", "university": "...", "cgpa": 3.8, "year": "..."}],
  "projects": [{"name": "...", "description": "...", "technologies": ["..."], "link": "...", "impact": "..."}],
  "certifications": ["..."],
  "achievements": ["..."],
  "total_experience_years": 2.5
}"""
        user_prompt = f"Resume Text:\n\n{raw_text[:12000]}"
        return self._call_llm_json(system_prompt, user_prompt)

    def analyze_ats(self, profile: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
        system_prompt = """You are an ATS (Applicant Tracking System) Evaluation Specialist.
Analyze the candidate's resume profile and raw text.
Calculate an ATS compatibility score (0-100) based on formatting clarity, keyword presence, quantifiable impact, and completeness.
Identify strengths, weaknesses, actionable suggestions, and a deep-dive "best project" analysis detailing which project demonstrates the highest technical rigor and business impact.
Schema:
{
  "ats_score": 85,
  "strengths": ["Strong quantifiable metrics in project X", "Clear modern tech stack"],
  "weaknesses": ["Missing summary section", "Action verbs could be stronger"],
  "suggestions": ["Add metrics to role Y", "Include certifications in cloud"],
  "best_project_analysis": "Project 'E-commerce Microservices' is the strongest because it demonstrates distributed systems architecture, Docker containerization, and measured a 40% latency reduction."
}"""
        user_prompt = f"Parsed Profile:\n{json.dumps(profile, indent=2)}\n\nRaw Resume Sample:\n{raw_text[:4000]}"
        return self._call_llm_json(system_prompt, user_prompt)

    def chat_candidate(self, message: str, profile: Dict[str, Any], ats: Dict[str, Any], history: List[Dict[str, str]]) -> Dict[str, Any]:
        system_prompt = f"""You are Antigravity Career AI, a personalized career advisor for this candidate.
Every answer you give MUST be strictly grounded in the candidate's parsed resume and ATS analysis data.
Cite specific projects, skills, or metrics from their background.

Candidate Resume Data:
{json.dumps(profile, indent=2)}

ATS Analysis:
{json.dumps(ats, indent=2)}

Return a JSON object with:
{{
  "reply": "Your helpful grounded response here...",
  "context_sources": ["Project: Name", "Skill: Python", "ATS Weakness: Missing metrics"]
}}"""
        user_prompt = f"Chat History: {json.dumps(history[-4:]) if history else 'None'}\n\nCandidate Question: {message}"
        return self._call_llm_json(system_prompt, user_prompt)

    def parse_job_description(self, raw_text: str) -> Dict[str, Any]:
        system_prompt = """You are an AI Technical Recruiter. Extract structured specifications from the Job Description text.
Schema:
{
  "title": "Job Title",
  "company": "Company Name",
  "required_skills": ["Skill1", "Skill2"],
  "nice_to_have_skills": ["Skill3", "Skill4"],
  "qualifications": ["Bachelor's in CS or equivalent", ...],
  "responsibilities": ["Build scalable APIs", ...],
  "experience_required": "3+ years"
}"""
        user_prompt = f"Job Description:\n\n{raw_text[:8000]}"
        return self._call_llm_json(system_prompt, user_prompt)

    def evaluate_jd_fit(self, profile: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        system_prompt = """You are an expert Talent Matcher. Compare the candidate profile against the Job Description.
Calculate a match score (0-100), classify into 'shortlist' (>=75), 'maybe' (50-74), or 'reject' (<50), list matched skills, missing skills, provide a ranking explanation, and cite 2-4 exact evidence quotes or reasons from the candidate profile.
Schema:
{
  "match_score": 88,
  "classification": "shortlist",
  "matched_skills": ["FastAPI", "PostgreSQL", "Docker"],
  "missing_skills": ["Kubernetes"],
  "ranking_explanation": "Candidate has strong backend experience matching 85% of core requirements with direct project evidence in FastAPI.",
  "evidence_quotes": [
    "Built high-throughput FastAPI microservice with PostgreSQL",
    "3+ years experience with relational database design"
  ]
}"""
        user_prompt = f"Candidate Profile:\n{json.dumps(profile, indent=2)}\n\nJob Posting:\n{json.dumps(job, indent=2)}"
        return self._call_llm_json(system_prompt, user_prompt)

    def generate_interview_questions(self, profile: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        system_prompt = """You are a Principal Engineer and Hiring Bar Raiser.
Generate a tailored interview question set for this candidate applying for this job.
Generate:
- 3 deep Technical Questions
- 3 Project-Specific Questions referencing their actual projects
- 2 Behavioral Questions
- 2 Probing Follow-Up Questions
Schema:
{
  "technical": ["...", "...", "..."],
  "project": ["...", "...", "..."],
  "behavioral": ["...", "..."],
  "follow_up": ["...", "..."]
}"""
        user_prompt = f"Candidate Profile:\n{json.dumps(profile, indent=2)}\n\nTarget Job:\n{json.dumps(job, indent=2)}"
        return self._call_llm_json(system_prompt, user_prompt)

    def evaluate_interview_step(self, question: str, answer: str, context: Dict[str, Any]) -> Dict[str, Any]:
        system_prompt = """You are an AI Technical Interviewer evaluating a candidate's answer in real-time.
Evaluate the candidate's answer for technical accuracy, clarity, and depth.
Provide concise feedback and a step score (0-100).
Schema:
{
  "score": 85,
  "feedback": "Great explanation of connection pooling. Next time also mention idle timeout handling.",
  "strengths": ["Clear architectural understanding", "Mentioned indexing strategies"],
  "improvements": ["Could elaborate on error handling"]
}"""
        user_prompt = f"Question: {question}\nCandidate Answer: {answer}"
        return self._call_llm_json(system_prompt, user_prompt)

    def summarize_mock_interview(self, transcript: List[Dict[str, Any]], profile: Dict[str, Any]) -> Dict[str, Any]:
        system_prompt = """You are an AI Technical Interview Board.
Review the complete mock interview transcript.
Compute category scores (0-100) for: technical, communication, projects, and problem_solving.
Compute an overall interview readiness score (0-100) and actionable summary feedback.
Schema:
{
  "scores": {
    "technical": 85,
    "communication": 90,
    "projects": 80,
    "problem_solving": 88
  },
  "readiness_score": 86,
  "feedback": "Overall strong performance. Candidate articulated system design tradeoffs clearly and showed solid database knowledge."
}"""
        user_prompt = f"Candidate Profile:\n{json.dumps(profile, indent=2)}\n\nInterview Transcript:\n{json.dumps(transcript, indent=2)}"
        return self._call_llm_json(system_prompt, user_prompt)

    def rank_candidates_with_evidence(self, candidates: List[Dict[str, Any]], job: Dict[str, Any]) -> List[Dict[str, Any]]:
        system_prompt = """You are an Executive Talent Screener.
Review the candidate pool for the given job.
Rank candidates from best to worst.
For each candidate, provide a relative ranking explanation citing specific evidence (e.g. why candidate A ranks above candidate B).
Schema:
{
  "rankings": [
    {
      "candidate_id": "...",
      "rank": 1,
      "match_score": 92,
      "classification": "shortlist",
      "ranking_explanation": "Ranked #1 because candidate has 4+ years of direct FastAPI and PostgreSQL experience plus production deployment of an AI agent platform.",
      "evidence_quotes": ["Architected distributed task queue in Celery", "Optimized SQL queries by 60%"]
    }
  ]
}"""
        user_prompt = f"Job Details:\n{json.dumps(job, indent=2)}\n\nCandidate Pool:\n{json.dumps(candidates, indent=2)}"
        result = self._call_llm_json(system_prompt, user_prompt)
        return result.get("rankings", [])

    def chat_recruiter(self, message: str, candidates: List[Dict[str, Any]], job: Dict[str, Any], history: List[Dict[str, str]]) -> Dict[str, Any]:
        system_prompt = f"""You are an AI Recruitment Copilot assisting a recruiter.
Translate natural language queries into candidate insights based on the available candidate pool and job requirements.
Provide specific candidate names, scores, and evidence in your answer.

Job Details:
{json.dumps(job, indent=2) if job else 'General Pool'}

Candidate Database:
{json.dumps(candidates[:15], indent=2)}

Return a JSON object:
{{
  "reply": "Summary answer citing specific candidates...",
  "matching_candidate_ids": ["uuid1", "uuid2"],
  "context_sources": ["Candidate: Alice (4 yrs Python)", "Candidate: Bob (React/TS)"]
}}"""
        user_prompt = f"Chat History: {json.dumps(history[-4:]) if history else 'None'}\n\nRecruiter Query: {message}"
        return self._call_llm_json(system_prompt, user_prompt)
