from ..services.parser import parse_resume
from ..schemas.analysis import ResumeAnalysisResponse 
from fastapi import UploadFile
from pathlib import Path
import tempfile
from ..services.llm import generate_with_llm
from ..prompts.analyse import create_resume_analyse_prompt,SYSTEM_PROMPT
from ..schemas.analysis import ResumeAnalysisResponse
import json,os
from ..config import client,model,response_format
async def analyse_resume(file:UploadFile):
    schema=ResumeAnalysisResponse.model_json_schema()
    schema_str=json.dumps(schema,indent=2)
    suffix = Path(file.filename).suffix

    try:

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:

            temp_file.write(await file.read())

            temp_path = temp_file.name
        resume_response,links=parse_resume(temp_path)

        resume_prompt=create_resume_analyse_prompt(json.dumps(resume_response.model_dump(), indent=2),schema_str)
        result=generate_with_llm(client,model,resume_prompt,SYSTEM_PROMPT,response_format,ResumeAnalysisResponse)
        return result
    finally:
        os.remove(temp_path)
