from fastapi import UploadFile, File
from ..services.parser import parse_resume, parse_jd
from ..services.matcher import compare_resume as match_resume
from pathlib import Path
import json, csv, tempfile, os, zipfile
from datetime import datetime
from ..utils.profiles import extract_links


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def export_json(results):
    with open(OUTPUT_DIR / "results.json", "w") as f:
        json.dump(results, f, indent=4)


def export_csv(results):
    with open(OUTPUT_DIR / "results.csv", "w", newline='') as output_csv:
        fields = ['Candidate_Name', 'Match_Score', 'Decision',
                  "Matched_Skills_Count", "Missing_Skills_Count"]

        output_writer = csv.DictWriter(output_csv, fieldnames=fields)

        output_writer.writeheader()

        for result in results:
            output_writer.writerow(result)


async def compare_resume(resumes_zip: UploadFile, jd: UploadFile):
    results = []
    suffix = Path(jd.filename).suffix

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
        temp.write(await jd.read())
        jd_path = temp.name

    try:
        jd_model, links = parse_jd(jd_path)
        jd_dict = jd_model.model_dump()
    finally:
        os.remove(jd_path)

    shortlisted = 0
    maybe = 0
    rejected = 0
    highest_score = 0
    lowest_score = 101
    accumulated_score = 0
    total_candidates = 0

    suffix = Path(resumes_zip.filename).suffix

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
        temp.write(await resumes_zip.read())
        zip_path = temp.name

    with tempfile.TemporaryDirectory() as temp_dir:
        # extract zip
        extract_folder = Path(temp_dir) / "resumes"

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_folder)

        for resume_path in extract_folder.rglob("*"):
            if resume_path.suffix.lower() not in [".pdf", ".docx"]:
                continue

            resume_model, links = parse_resume(str(resume_path))

            result = match_resume(resume_model, jd_model)

            highest_score = max(highest_score, result.match_score)
            lowest_score = min(lowest_score, result.match_score)
            accumulated_score += result.match_score

            if result.match_score >= 80:
                result.decision = "Shortlist"
                shortlisted += 1
            elif result.match_score >= 60:
                result.decision = "Maybe"
                maybe += 1
            else:
                result.decision = "Reject"
                rejected += 1
            total_candidates += 1

            result.profiles = extract_links(links)

            results.append(result)

    os.remove(zip_path)

    results.sort(key=lambda x: x.match_score, reverse=True)

    metadata = {
        "company": jd_dict["company"],
        "role": jd_dict["role"],
        "total_candidates": total_candidates,
        "shortlisted": shortlisted,
        "maybe": maybe,
        "rejected": rejected,
        "highest_score": highest_score,
        "lowest_score": lowest_score,
        "average_score": (accumulated_score / total_candidates) if total_candidates else 0,
        "generated_at": datetime.now().isoformat(),
        "generator": "Resume Evaluator v1.0"
    }

    json_data = {
        "metadata": metadata,
        "results": []
    }
    csv_data = []

    print("\n============ Candidate Ranking ==========\n")
    for i, result in enumerate(results, start=1):
        print(
            f"{i}. {result.candidate_name} | "
            f"{result.match_score}% | "
            f"{result.decision}"
        )
        json_data["results"].append(result.model_dump())
        csv_data.append({
            "Candidate_Name": result.candidate_name,
            "Match_Score": result.match_score,
            "Decision": result.decision,
            "Matched_Skills_Count": len(result.matched_skills),
            "Missing_Skills_Count": len(result.missing_skills)
        })

    export_csv(csv_data)
    export_json(json_data)
    return results
