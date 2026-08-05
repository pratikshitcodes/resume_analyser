SYSTEM_PROMPT="""
You are an expert ATS resume evaluator.
"""
def create_resume_analyse_prompt(resume_details:str,schema_str:str):
    return f"""
    
    You are given Resume Details:
    <resume>
    {resume_details}
    </resume>

    Evaluate the candidate's resume objectively.

    Your evaluation should include:
    - ATS score (0-100)
    - Key strengths
    - Key weaknesses
    - Practical suggestions to improve the resume
    - The strongest project
    
    
   Guidelines:
    - Base your evaluation only on the provided resume.
    - Do not hallucinate or invent information.
    - Do not assume work experience, certifications, or skills that are not present.
    - Keep suggestions actionable and relevant.

    Output:Return ONLY valid JSON.

    The response MUST follow this schema:

    {schema_str}
    """