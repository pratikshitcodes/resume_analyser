def create_resume_prompt(text:str,schema:dict)->str:
    prompt=f"""
        You are an ATS resume evaluator Out of 100.

        Below is the extracted text from a resume.

        <resume>

        {text}

        </resume>

        Analyze it according to the schema.
        Select the strongest project based on industry relevance and technical depth.
        Summarize it in one sentence.
        Explain why it is the strongest project in 1 line. 
        Return ONLY valid JSON.
        Do not include markdown.
        The response MUST follow this schema:
        {schema}
    """
    return prompt
def create_match_prompt(resume_text: str, job_description: str, schema: dict) -> str:
    import json

    schema_json = json.dumps(schema, indent=2)

    return f"""
        You are a JSON API.

        Compare the following resume with the given job description.

        <resume>
        {resume_text}
        </resume>

        <job_description>
        {job_description}
        </job_description>

        Return ONLY ONE valid JSON object.

        Do not use markdown.
        Do not use code fences.
        Do not explain anything.

        The JSON must conform to this schema:
        Return exactly this JSON structure.

        {{
            "match_score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "strengths": [],
            "weakness": [],
            "suggestions": "",
            "best_project": ""
        }}
    """