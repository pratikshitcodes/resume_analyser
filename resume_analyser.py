import json
from prompts import create_match_prompt
from pdf_reader import extract_text
from models import ResumeCompareModel
from llm import analyze_resume
from config import client, model


def main():
    schema = ResumeCompareModel.model_json_schema()
    response_format = {
        "type": "json_object"
    }

    resume_text = extract_text("Pratikshit_singh_resume (2).pdf")
    jd_text = extract_text("JD Full Stack Intern - 2026.pdf")
    prompt = create_match_prompt(resume_text, jd_text, json.dumps(schema))

    resume = analyze_resume(client, model, prompt, response_format)
    print(resume.model_dump_json(indent=4))


if __name__ == "__main__":
    main()

