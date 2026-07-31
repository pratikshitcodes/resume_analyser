matcher_system_prompt="""You are an expert ATS  resume evaluator.

        Your task is to compare a structured resume against a structured job description and produce an accurate evaluation.

        Be objective.
        Do not hallucinate.
        Return only valid JSON."""
parse_system_prompt="""
You are an information extraction assistant.
"""
def create_resume_prompt(text: str, schema_str:str) -> str:
    prompt = f"""
        Below is the extracted text from a resume.

        <resume>

        {text}

        </resume>

        Extract the essential information from the resume about the candidate according to this schema.{schema_str}
        Return ONLY valid JSON.
        Do not include markdown.
    """
    return prompt

def create_jd_prompt(text: str, schema_str:str) -> str:
    prompt = f"""
        Below is the extracted text from a job_description.

        <job_description>

        {text}

        </job_description>

        The response MUST follow this schema:
        {schema_str}
        Return ONLY valid JSON.
        Do not include markdown.
    """
    return prompt


def create_match_prompt(resume_text: str, job_description: str, schema_str: str) -> str:
    return f"""
        You are an expert ATS Resume Evaluator.

        You are given:

        1. A structured resume.
        2. A structured job description.

        Your task:
        -Dont be too strict while giving the ATS score.
        - Compare the resume against the job description.
        - Calculate a realistic ATS match score from 0-100.
        - Dont fill the decision field.
        - List all matching skills.
        - List all missing skills.
        - Identify the candidate's strengths.
        - Identify weaknesses relative to the job.
        - Give practical suggestions to improve the resume for this role.
        - Select the strongest project relevant to the job.

        Do NOT leave any field empty unless the information truly does not exist.

        Resume:
        {resume_text}

        Job Description:
        {job_description}

        Return ONLY valid JSON.

        The JSON MUST follow this schema:

        {schema_str}
        """