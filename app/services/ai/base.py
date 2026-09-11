from abc import ABC, abstractmethod
from typing import Dict, Any, List

class AIProvider(ABC):
    @abstractmethod
    def extract_profile(self, raw_text: str) -> Dict[str, Any]:
        """Extract structured resume profile from raw text"""
        pass

    @abstractmethod
    def analyze_ats(self, profile: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
        """Compute ATS score, strengths, weaknesses, suggestions, and best project analysis"""
        pass

    @abstractmethod
    def chat_candidate(self, message: str, profile: Dict[str, Any], ats: Dict[str, Any], history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Grounded candidate RAG chat based on resume and ATS data"""
        pass

    @abstractmethod
    def parse_job_description(self, raw_text: str) -> Dict[str, Any]:
        """Extract required/nice-to-have skills, qualifications, responsibilities from JD"""
        pass

    @abstractmethod
    def evaluate_jd_fit(self, profile: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate resume to JD fit, compute score, matched/missing skills, and classification"""
        pass

    @abstractmethod
    def generate_interview_questions(self, profile: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        """Generate tailored technical, project, behavioral, and follow-up questions"""
        pass

    @abstractmethod
    def evaluate_interview_step(self, question: str, answer: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single answer in mock interview and generate real-time feedback"""
        pass

    @abstractmethod
    def summarize_mock_interview(self, transcript: List[Dict[str, Any]], profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final scores, readiness score, and overall interview feedback"""
        pass

    @abstractmethod
    def rank_candidates_with_evidence(self, candidates: List[Dict[str, Any]], job: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Rank candidates with evidence-backed citations and explanations"""
        pass

    @abstractmethod
    def chat_recruiter(self, message: str, candidates: List[Dict[str, Any]], job: Dict[str, Any], history: List[Dict[str, str]]) -> Dict[str, Any]:
        """NLQ chat for recruiters over candidate database"""
        pass
