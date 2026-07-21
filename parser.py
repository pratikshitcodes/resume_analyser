from models import ResumeModel,JobDescriptionModel
from readers import extract_text
from prompts import create_resume_prompt,create_jd_prompt,parse_system_prompt
from llm import generate_with_llm
from config import client,model,response_format
import json


def parse_resume(path:str):
    schema_resume = ResumeModel.model_json_schema()
    schema_resume_str=json.dumps(schema_resume,indent=2)
    resume_text=extract_text(path)

    resume_prompt=create_resume_prompt(resume_text,schema_resume_str)
    resume_response=generate_with_llm(client,model,resume_prompt,parse_system_prompt,response_format,ResumeModel)

    return resume_response

def parse_jd(path:str):

    schema_jd=JobDescriptionModel.model_json_schema()
    schema_jd_str=json.dumps(schema_jd,indent=2)

    jd_text=extract_text(path)

    jd_prompt=create_jd_prompt(jd_text,schema_jd_str)

    jd_response=generate_with_llm(client,model,jd_prompt,parse_system_prompt,response_format,JobDescriptionModel)

    return jd_response    


