import json
from parser import parse_resume,parse_jd
from matcher import compare_resume

def main():
    resume=parse_resume("Pratikshit_singh_resume (2).pdf")
    jd=parse_jd("JD Full Stack Intern - 2026.pdf")
    print(resume)
    print(jd)
    result=compare_resume(resume,jd)
    print(result.model_dump_json(indent=4))

if __name__ == "__main__":
    main()

