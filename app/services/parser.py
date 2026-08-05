from app.schemas.models import ResumeModel,JobDescriptionModel
from app.utils.readers import extract_text
from app.prompts.compare_prompts import create_resume_prompt,create_jd_prompt,parse_system_prompt
from app.services.llm import generate_with_llm
from app.config import client,model,response_format
import json
from typing import Type
from pydantic import BaseModel


def parse_resume(path:str):
    schema_resume = ResumeModel.model_json_schema()
    schema_resume_str=json.dumps(schema_resume,indent=2)
    resume_text,links=extract_text(path)

    resume_prompt=create_resume_prompt(resume_text,schema_resume_str)

    resume_response=generate_with_llm(client,model,resume_prompt,parse_system_prompt,response_format,ResumeModel)

    return resume_response,links

def parse_jd(path:str):

    schema_jd=JobDescriptionModel.model_json_schema()
    schema_jd_str=json.dumps(schema_jd,indent=2)

    jd_text,links=extract_text(path)

    jd_prompt=create_jd_prompt(jd_text,schema_jd_str)

    jd_response=generate_with_llm(client,model,jd_prompt,parse_system_prompt,response_format,JobDescriptionModel)

    return jd_response,links


