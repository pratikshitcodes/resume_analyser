import re
from typing import Dict, Any, List
from .base import AIProvider

class MockProvider(AIProvider):
    """Heuristic and pattern-matching provider used for unit testing, offline development, or fallbacks."""

    def extract_profile(self, raw_text: str) -> Dict[str, Any]:
        lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
        name = lines[0] if lines else "Candidate Name"
        
        # Heuristic emails
        emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', raw_text)
        email = emails[0] if emails else "candidate@example.com"
        
        # Skill extraction
        common_skills = [
            "Python", "FastAPI", "React", "TypeScript", "JavaScript", "SQL", "PostgreSQL",
            "Docker", "Kubernetes", "AWS", "Git", "Node.js", "Redis", "Machine Learning",
            "Tailwind CSS", "GraphQL", "Java", "C++", "HTML", "CSS", "REST API", "Celery",
            "LangChain", "LLM", "Pydantic", "PyTorch", "Pandas"
        ]
        found_skills = [s for s in common_skills if re.search(r'\b' + re.escape(s) + r'\b', raw_text, re.IGNORECASE)]
        if not found_skills:
            found_skills = ["Python", "FastAPI", "PostgreSQL", "React", "Git"]

        # Projects heuristic
        projects = []
        project_keywords = ["platform", "engine", "system", "app", "api", "dashboard", "service", "evaluator"]
        for line in lines:
            if any(k in line.lower() for k in project_keywords) and len(line) < 60:
                projects.append({
                    "name": line,
                    "description": "Full-stack cloud application featuring automated pipelines and modern UI architecture.",
                    "technologies": found_skills[:3],
                    "link": "https://github.com/project",
                    "impact": "Boosted throughput by 35% and cut processing time in half."
                })
                if len(projects) >= 2:
                    break
        if not projects:
            projects = [{
                "name": "AI Recruitment Platform",
                "description": "Engineered full-stack recruitment platform with ATS scoring, interview simulation, and candidate ranking.",
                "technologies": ["FastAPI", "React", "PostgreSQL", "Tailwind CSS"],
                "link": "https://github.com/example/recruitment-platform",
                "impact": "Processed 100+ resumes in under 60 seconds with 90% parsing precision."
            }]

        return {
            "name": name,
            "contact_info": {
                "email": email,
                "phone": "+1 (555) 019-2834",
                "linkedin": "https://linkedin.com/in/candidate",
                "github": "https://github.com/candidate",
                "portfolio": "https://candidate.dev"
            },
            "skills": found_skills,
            "experience": [
                {
                    "company": "Tech Innovations Inc.",
                    "role": "Software Engineer",
                    "duration": "2023 - Present",
                    "description": "Designed and deployed resilient microservices, optimized database queries, and collaborated in cross-functional agile teams."
                }
            ],
            "education": [
                {
                    "degree": "B.S. in Computer Science",
                    "university": "State University",
                    "cgpa": 3.8,
                    "year": "2023"
                }
            ],
            "projects": projects,
            "certifications": ["AWS Certified Solutions Architect", "Certified Kubernetes Application Developer"],
            "achievements": ["Dean's List 2021-2023", "1st Place University Hackathon"],
            "total_experience_years": 2.5
        }

    def analyze_ats(self, profile: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
        skills = profile.get("skills", [])
        projects = profile.get("projects", [])
        
        # Calculate dynamic score based on profile fullness
        score = 70
        if len(skills) >= 5: score += 10
        if len(projects) >= 2: score += 10
        if "github" in str(profile.get("contact_info", {})): score += 5
        score = min(score, 96)

        best_proj = projects[0]["name"] if projects else "Main Technical Project"

        return {
            "ats_score": score,
            "strengths": [
                f"Strong technical skill diversity across {len(skills)} modern technologies",
                "Quantifiable impact metrics present across project descriptions",
                "Clean structural format easily parsed by enterprise ATS engines"
            ],
            "weaknesses": [
                "Could include more specific domain keywords for targeted roles",
                "Summary section could highlight leadership or cross-team collaboration"
            ],
            "suggestions": [
                "Incorporate more action verbs (e.g. 'Architected', 'Spearheaded', 'Optimized')",
                "Add cloud infrastructure and automated CI/CD pipeline details to project sections"
            ],
            "best_project_analysis": f"Project '{best_proj}' demonstrates exceptional technical depth, clear business impact, and modern architectural design patterns."
        }

    def chat_candidate(self, message: str, profile: Dict[str, Any], ats: Dict[str, Any], history: List[Dict[str, str]]) -> Dict[str, Any]:
        name = profile.get("name", "Candidate")
        skills = ", ".join(profile.get("skills", ["FastAPI", "React"])[:4])
        ats_score = ats.get("ats_score", 85)
        
        return {
            "reply": f"Hi {name}! Based on your resume (ATS Score: {ats_score}/100) and your strong background in {skills}, I can help you target roles matching your strengths. In your projects, you demonstrated high impact. You can improve your profile further by emphasizing system scalability and CI/CD pipelines.",
            "context_sources": [
                f"Candidate Name: {name}",
                f"ATS Score: {ats_score}",
                f"Key Skills: {skills}"
            ]
        }

    def parse_job_description(self, raw_text: str) -> Dict[str, Any]:
        return {
            "title": "Full Stack Software Engineer",
            "company": "Innovation Labs",
            "required_skills": ["Python", "FastAPI", "React", "PostgreSQL", "Docker"],
            "nice_to_have_skills": ["Kubernetes", "Redis", "Celery", "Tailwind CSS"],
            "qualifications": [
                "Bachelor's degree in Computer Science or related field",
                "2+ years of full-stack web application development experience"
            ],
            "responsibilities": [
                "Design and maintain scalable REST APIs with FastAPI",
                "Build responsive, modern UI components with React & Tailwind CSS",
                "Participate in code reviews and architectural planning"
            ],
            "experience_required": "2+ years"
        }

    def evaluate_jd_fit(self, profile: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        candidate_skills = set(s.lower() for s in profile.get("skills", []))
        req_skills = job.get("required_skills", ["Python", "FastAPI", "React"])
        
        matched = [s for s in req_skills if s.lower() in candidate_skills]
        missing = [s for s in req_skills if s.lower() not in candidate_skills]
        
        match_pct = int((len(matched) / max(len(req_skills), 1)) * 100)
        classification = "shortlist" if match_pct >= 70 else ("maybe" if match_pct >= 40 else "reject")

        return {
            "match_score": max(match_pct, 60),
            "classification": classification,
            "matched_skills": matched if matched else req_skills[:2],
            "missing_skills": missing,
            "ranking_explanation": f"Candidate matches {len(matched)} of {len(req_skills)} required core skills with proven hands-on experience.",
            "evidence_quotes": [
                f"Demonstrated proficiency in {', '.join(matched[:3]) if matched else 'core technologies'}",
                f"Total professional experience: {profile.get('total_experience_years', 2)} years"
            ]
        }

    def generate_interview_questions(self, profile: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        skills = profile.get("skills", ["Python", "FastAPI"])
        top_skill = skills[0] if skills else "Python"
        proj = profile.get("projects", [{}])[0].get("name", "Key Project")

        return {
            "technical": [
                f"How would you design a scalable asynchronous API using {top_skill} to handle 10,000 concurrent requests?",
                "Can you explain the differences between relational database transactions (ACID) and eventual consistency in distributed systems?",
                "How do you profile and optimize memory leaks and database query bottlenecks?"
            ],
            "project": [
                f"In your project '{proj}', what were the most challenging architectural decisions and how did you measure success?",
                f"How did you implement security, authentication, and error handling in '{proj}'?",
                "If you had to re-architect that system for 10x scale today, what would you change?"
            ],
            "behavioral": [
                "Describe a situation where you had a disagreement with a team member regarding system architecture. How did you resolve it?",
                "Tell me about a time a production issue occurred under your watch. How did you triage and resolve it?"
            ],
            "follow_up": [
                "What specific monitoring or observability metrics would you check first?",
                "How did you ensure test coverage and regression prevention for that feature?"
            ]
        }

    def evaluate_interview_step(self, question: str, answer: str, context: Dict[str, Any]) -> Dict[str, Any]:
        length = len(answer.split())
        score = min(max(length * 2 + 50, 65), 95)
        
        return {
            "score": score,
            "feedback": "Strong structured explanation highlighting core technical principles and practical engineering tradeoffs.",
            "strengths": ["Clear communication", "Practical engineering examples"],
            "improvements": ["Consider quantifying latency or scalability metrics"]
        }

    def summarize_mock_interview(self, transcript: List[Dict[str, Any]], profile: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "scores": {
                "technical": 88,
                "communication": 90,
                "projects": 85,
                "problem_solving": 87
            },
            "readiness_score": 88,
            "feedback": "Outstanding performance. Demonstrated deep domain knowledge, articulate technical communication, and sound problem-solving intuition."
        }

    def rank_candidates_with_evidence(self, candidates: List[Dict[str, Any]], job: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Sort candidates by match_score descending
        sorted_candidates = sorted(candidates, key=lambda c: c.get("match_score", 0), reverse=True)
        rankings = []
        for rank, cand in enumerate(sorted_candidates, start=1):
            cand_id = cand.get("candidate_id") or cand.get("id")
            score = cand.get("match_score", 85)
            skills = cand.get("matched_skills", ["Python", "FastAPI"])
            rankings.append({
                "candidate_id": cand_id,
                "rank": rank,
                "match_score": score,
                "classification": "shortlist" if score >= 75 else ("maybe" if score >= 50 else "reject"),
                "ranking_explanation": f"Rank #{rank}: Strong alignment with {len(skills)} verified core skills ({', '.join(skills[:3])}) and solid project deliverables.",
                "evidence_quotes": [
                    f"Direct hands-on experience in {skills[0] if skills else 'core stack'}",
                    f"Verified project track record with high ATS scoring profile"
                ]
            })
        return rankings

    def chat_recruiter(self, message: str, candidates: List[Dict[str, Any]], job: Dict[str, Any], history: List[Dict[str, str]]) -> Dict[str, Any]:
        count = len(candidates)
        top_cands = candidates[:3]
        names = [c.get("name") or c.get("candidate_name") or "Candidate" for c in top_cands]
        
        return {
            "reply": f"Found {count} candidate(s) in your pool. The top ranked candidates are {', '.join(names)}. They demonstrate strong relevant skills matching your job requirements.",
            "matching_candidate_ids": [c.get("id") or c.get("candidate_id") for c in top_cands if c.get("id") or c.get("candidate_id")],
            "context_sources": [f"Candidate: {n}" for n in names]
        }
