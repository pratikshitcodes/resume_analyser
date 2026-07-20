from prompts import create_resume_prompt,create_match_prompt
from pdf_reader import extract_text
from models import ResumeResponseModel,ResumeCompareModel
from llm import analyze_resume
from config import client,model

schema=ResumeResponseModel.model_json_schema()
response_format={
    "type":"json_object"
}

resume_text=extract_text("Pratikshit_singh_resume (2).pdf")

prompt=create_resume_prompt(resume_text,schema)

resume=analyze_resume(client,model,prompt,response_format)

