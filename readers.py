from pypdf import PdfReader
from pathlib import Path
from docx import Document

def read_pdf(path:str)-> str:
    reader=PdfReader(path)
    text=""
    for page in reader.pages:
        text+=(page.extract_text() or "")+"\n\n"
    return text

def read_docx(path:str)->str:
    doc=Document(path)
    text=[]

    for para in doc.paragraphs:
        text.append(para.text)
    return "\n".join(text)

def extract_text(path:str)->str:
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