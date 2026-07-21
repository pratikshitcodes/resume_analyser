from models import ResumeCompareModel,ResumeModel,JobDescriptionModel
from prompts import create_match_prompt,matcher_system_prompt
import json
from llm import generate_with_llm
from config import client,model,response_format

def compare_resume(resume:ResumeModel,jd:JobDescriptionModel)->ResumeCompareModel:
    schema=ResumeCompareModel.model_json_schema()
    schema_str=json.dumps(schema,indent=2)

    matcher_prompt=create_match_prompt(json.dumps(resume.model_dump(),indent=2),json.dumps(jd.model_dump(),indent=2),schema_str)

    matcher_response=generate_with_llm(client,model,matcher_prompt,matcher_system_prompt,response_format,ResumeCompareModel)

    return matcher_response