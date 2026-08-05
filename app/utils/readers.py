from pypdf import PdfReader
from pathlib import Path
from docx import Document
import fitz
from fastapi import UploadFile

def read_pdf(path:str)-> tuple[str,list[str]]:
    reader=PdfReader(path)
    text=""
    doc = fitz.open(path)
    links = []

    for page in doc:
        for link in page.get_links():
            if "uri" in link:
                links.append(link["uri"])

    for page in reader.pages:
        text+=(page.extract_text() or "")+"\n\n"
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

    READERS = {
        ".pdf": read_pdf,
        ".docx": read_docx,
    }
    if suffix not in READERS:
        raise ValueError(f"{suffix} is Invalid file type for resume.Only PDF and DOCX are supported.")
    return READERS[suffix](path)