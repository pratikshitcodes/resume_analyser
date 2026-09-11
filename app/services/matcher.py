from typing import Dict, Any, List
from .ai.factory import get_ai_provider
from ..schemas.models import ResumeCompareModel, ResumeModel, JobDescriptionModel

def match_candidate_to_job(profile: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
    ai = get_ai_provider()
    return ai.evaluate_jd_fit(profile, job)

def rank_candidates_for_job(candidates_data: List[Dict[str, Any]], job: Dict[str, Any]) -> List[Dict[str, Any]]:
    ai = get_ai_provider()
    return ai.rank_candidates_with_evidence(candidates_data, job)

# Backward-compatible function for legacy compare.py
def compare_resume(resume_model: ResumeModel, jd_model: JobDescriptionModel) -> ResumeCompareModel:
    ai = get_ai_provider()
    profile_dict = resume_model.model_dump()
    jd_dict = jd_model.model_dump()
    fit = ai.evaluate_jd_fit(profile_dict, jd_dict)
    
    return ResumeCompareModel(
        candidate_name=resume_model.name or "Candidate",
        profiles=None,
        match_score=int(fit.get("match_score", 75)),
        decision=fit.get("classification", "Shortlist").capitalize(),
        matched_skills=fit.get("matched_skills", []),
        missing_skills=fit.get("missing_skills", []),
        strengths=fit.get("evidence_quotes", ["Solid technical alignment"]),
        weakness=fit.get("missing_skills", ["None"]),
        suggestions="Continue building projects matching the target stack.",
        best_project="Primary technical project."
    )