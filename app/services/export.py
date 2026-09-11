import io
import csv
import json
from typing import List, Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_csv_export(candidates: List[Dict[str, Any]]) -> str:
    output = io.StringIO()
    fieldnames = [
        "rank", "candidate_name", "candidate_email", "match_score",
        "classification", "matched_skills", "missing_skills",
        "total_experience_years", "ranking_explanation"
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for cand in candidates:
        writer.writerow({
            "rank": cand.get("rank", 1),
            "candidate_name": cand.get("candidate_name", "N/A"),
            "candidate_email": cand.get("candidate_email", "N/A"),
            "match_score": cand.get("match_score", 0),
            "classification": cand.get("classification", "N/A"),
            "matched_skills": ", ".join(cand.get("matched_skills", [])),
            "missing_skills": ", ".join(cand.get("missing_skills", [])),
            "total_experience_years": cand.get("total_experience_years", 0),
            "ranking_explanation": cand.get("ranking_explanation", "")
        })
    return output.getvalue()

def generate_json_export(candidates: List[Dict[str, Any]], job: Dict[str, Any] = None) -> str:
    export_payload = {
        "job": job or {},
        "total_candidates": len(candidates),
        "candidates": candidates
    }
    return json.dumps(export_payload, indent=2)

def generate_pdf_report(job_title: str, candidates: List[Dict[str, Any]]) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1E293B")
    )
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#64748B")
    )
    heading2_style = ParagraphStyle(
        'Heading2Style',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0F172A")
    )
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#334155")
    )
    bold_body_style = ParagraphStyle(
        'BoldBodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1E293B")
    )

    elements = []

    # Header
    elements.append(Paragraph("AI Recruitment Platform — Candidate Ranking Report", title_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(f"Target Role: <b>{job_title}</b> | Total Candidates Analyzed: <b>{len(candidates)}</b>", subtitle_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#4F46E5"), spaceAfter=15))

    # Candidate Summary Table
    table_data = [
        [
            Paragraph("<b>Rank</b>", bold_body_style),
            Paragraph("<b>Candidate</b>", bold_body_style),
            Paragraph("<b>Score</b>", bold_body_style),
            Paragraph("<b>Status</b>", bold_body_style),
            Paragraph("<b>Matched Skills</b>", bold_body_style),
            Paragraph("<b>Exp (Yrs)</b>", bold_body_style)
        ]
    ]

    for cand in candidates:
        classification = cand.get("classification", "maybe").upper()
        status_color = "#10B981" if classification == "SHORTLIST" else ("#F59E0B" if classification == "MAYBE" else "#EF4444")
        
        status_p = Paragraph(f"<font color='{status_color}'><b>{classification}</b></font>", body_style)
        matched_str = ", ".join(cand.get("matched_skills", [])[:4])
        
        table_data.append([
            Paragraph(f"#{cand.get('rank', 1)}", bold_body_style),
            Paragraph(f"<b>{cand.get('candidate_name', 'N/A')}</b><br/>{cand.get('candidate_email', '')}", body_style),
            Paragraph(f"<b>{cand.get('match_score', 0)}%</b>", bold_body_style),
            status_p,
            Paragraph(matched_str or "None", body_style),
            Paragraph(str(cand.get("total_experience_years", 0)), body_style)
        ])

    table = Table(table_data, colWidths=[40, 140, 50, 75, 180, 55])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    # Evidence Deep-Dive Section
    elements.append(Paragraph("Evidence-Based Candidate Evaluations", heading2_style))
    elements.append(Spacer(1, 8))

    for cand in candidates[:5]: # Detailed top 5
        rank = cand.get("rank", 1)
        name = cand.get("candidate_name", "Candidate")
        explanation = cand.get("ranking_explanation", "Strong fit for the position.")
        quotes = cand.get("evidence_quotes", [])

        elements.append(Paragraph(f"<b>Rank #{rank}: {name}</b> (Score: {cand.get('match_score', 0)}% — {cand.get('classification', '').upper()})", bold_body_style))
        elements.append(Paragraph(f"<i>Justification:</i> {explanation}", body_style))
        if quotes:
            for q in quotes:
                elements.append(Paragraph(f"• <i>Evidence:</i> \"{q}\"", body_style))
        elements.append(Spacer(1, 8))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
