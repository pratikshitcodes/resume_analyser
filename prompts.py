def create_resume_prompt(text: str, schema: dict) -> str:
    prompt = f"""
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


def create_match_prompt(resume_text: str, job_description: str, schema_str: str) -> str:
    return f"""
        You are an ATS Resume Matching API.

        Given the resume of the candidate.
        <resume>
        {resume_text}
        </resume>

        Given the job description for the position.
        {job_description}

        Compare the resume against the job description.

        Return ONLY valid JSON.
        Do not explain.
        Do not use markdown.
        Do not wrap in ```.

        The response MUST follow this schema:
        {schema_str}
    """
