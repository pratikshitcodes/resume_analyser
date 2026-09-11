from pypdf import PdfReader
from pathlib import Path
from docx import Document
import fitz
from fastapi import UploadFile

def read_pdf(path:str)-> tuple[str,list[str]]:
    text=""
    links = []

    try:
        with fitz.open(path) as doc:
            for page in doc:
                text += page.get_text() + "\n\n"
                for link in page.get_links():
                    if "uri" in link:
                        links.append(link["uri"])
    except Exception as e:
        print(f"PyMuPDF error: {e}")
    
    if not text.strip():
        try:
            reader=PdfReader(path)
            for page in reader.pages:
                text+=(page.extract_text() or "")+"\n\n"
        except Exception as e:
            print(f"pypdf error: {e}")

    return text,links

def read_docx(path:str)->tuple[str,list[str]]:
    doc=Document(path)
    text=[]
    links = []
    
    rels = doc.part.rels
    for rel in rels.values():
        if "hyperlink" in rel.reltype:
            links.append(rel.target_ref)
    for para in doc.paragraphs:
        text.append(para.text)
    return "\n".join(text),links

def extract_text(path:str)->tuple[str,list[str]]:
    path_obj=Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"{path} does not exist")
    
    suffix=Path(path).suffix.lower()

    if path.endswith(".pdf"):
        return read_pdf(path)
    elif path.endswith(".docx"):
        return read_docx(path)
    elif path.endswith(".txt"):
        with open(path, "r", encoding="utf-8") as f:
            return f.read(), []
    else:
        raise ValueError(f"Unsupported file format for {path}")