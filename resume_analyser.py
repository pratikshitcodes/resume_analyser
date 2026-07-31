import json
from parser import parse_resume,parse_jd
from matcher import compare_resume
from pathlib import Path
import csv
from datetime import datetime
def export_json(results):
    with open("outputs/results.json","w") as f:
        json.dump(results,f,indent=4)


def export_csv(results):
    with open("outputs/results.csv","w",newline='') as output_csv:
        fields=['Candidate_Name','Match_Score','Decision',"Matched_Skills_Count","Missing_Skills_Count"]

        output_writer=csv.DictWriter(output_csv,fieldnames=fields)

        output_writer.writeheader()

        for result in results:
            output_writer.writerow(result)

def main():
    jd=parse_jd("JD Full Stack Intern - 2026.pdf")
    jd_dict=jd.model_dump()
    folder=Path("resumes")
    results=[]
    shortlisted=0
    maybe=0
    rejected=0
    highest_score=0
    lowest_score=101
    accumulated_score=0
    total_candidates=0
    for resume_path in folder.iterdir():
        resume=parse_resume(resume_path)
        res=compare_resume(resume,jd)

        highest_score=max(highest_score,res.match_score)

        lowest_score=min(lowest_score,res.match_score)

        accumulated_score+=res.match_score
        if res.match_score>=80:
            res.decision="Shortlist"
            shortlisted+=1
        elif res.match_score>=60:
            res.decision="Maybe"
            maybe+=1
        else:
            res.decision="Reject"
            rejected+=1
        total_candidates+=1
        results.append(res)
    results.sort(key=lambda x:x.match_score,reverse=True)
    metadata={
        "company":jd_dict["company"],
        "role":jd_dict["role"],
        "total_candidates": total_candidates,
        "shortlisted": shortlisted,
        "maybe": maybe,
        "rejected": rejected,
        "highest_score": highest_score,
        "lowest_score": lowest_score,
        "average_score": accumulated_score/total_candidates,
        "generated_at":datetime.now().isoformat(),
        "generator":"Resume Evaluator v1.0"
    }
    json_data={
        "metadata":metadata,
        "results":[]
    }
    csv_data=[]
    print("\n============ Candidate Ranking ==========\n")
    for i,result in enumerate(results,start=1):
        print(
            f"{i}. {result.candidate_name} | "
            f"{result.match_score}% | "
            f"{result.decision}"
        )
        json_data["results"].append(result.model_dump())
        csv_data.append({
            "Candidate_Name":result.candidate_name,
            "Match_Score":result.match_score,
            "Decision":result.decision,
            "Matched_Skills_Count":len(result.matched_skills),
            "Missing_Skills_Count":len(result.missing_skills)
            })
    export_json(json_data)
    export_csv(csv_data)


if __name__ == "__main__":
    main()

