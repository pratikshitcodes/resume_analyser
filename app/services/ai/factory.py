import logging
from .base import AIProvider
from .groq_provider import GroqProvider
from .mock_provider import MockProvider
from ...core.config import settings

logger = logging.getLogger(__name__)

class FallbackResilientProvider(AIProvider):
    def __init__(self, primary: AIProvider, fallback: AIProvider):
        self.primary = primary
        self.fallback = fallback

    def _execute(self, method_name: str, *args, **kwargs):
        try:
            method = getattr(self.primary, method_name)
            return method(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Primary AI Provider failed on {method_name} ({e}). Using resilient fallback provider.")
            fallback_method = getattr(self.fallback, method_name)
            return fallback_method(*args, **kwargs)

    def extract_profile(self, raw_text: str):
        return self._execute("extract_profile", raw_text)

    def analyze_ats(self, profile: dict, raw_text: str):
        return self._execute("analyze_ats", profile, raw_text)

    def chat_candidate(self, message: str, profile: dict, ats: dict, history: list):
        return self._execute("chat_candidate", message, profile, ats, history)

    def parse_job_description(self, raw_text: str):
        return self._execute("parse_job_description", raw_text)

    def evaluate_jd_fit(self, profile: dict, job: dict):
        return self._execute("evaluate_jd_fit", profile, job)

    def generate_interview_questions(self, profile: dict, job: dict):
        return self._execute("generate_interview_questions", profile, job)

    def evaluate_interview_step(self, question: str, answer: str, context: dict):
        return self._execute("evaluate_interview_step", question, answer, context)

    def summarize_mock_interview(self, transcript: list, profile: dict):
        return self._execute("summarize_mock_interview", transcript, profile)

    def rank_candidates_with_evidence(self, candidates: list, job: dict):
        return self._execute("rank_candidates_with_evidence", candidates, job)

    def chat_recruiter(self, message: str, candidates: list, job: dict, history: list):
        return self._execute("chat_recruiter", message, candidates, job, history)

def get_ai_provider() -> AIProvider:
    mock = MockProvider()
    if settings.GROQ_API_KEY:
        try:
            groq = GroqProvider(api_key=settings.GROQ_API_KEY)
            return FallbackResilientProvider(primary=groq, fallback=mock)
        except Exception as e:
            logger.error(f"Failed to initialize Groq provider: {e}")
            return mock
    return mock
