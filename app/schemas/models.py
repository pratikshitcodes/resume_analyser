from pydantic import BaseModel, ConfigDict,Field
class Experience(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company:str
    duration:str|None=None
    role:str
    description:str|None=None

class Education(BaseModel):
    model_config = ConfigDict(extra="forbid")

    degree:str
    university:str|None=None
    cgpa:float|None=None

class Project(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name:str
    description:str|None=None
    technologies:list[str]=[]
    link:str|None=None

class ResumeModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name:str
    email:str|None=None

    linkedin:str|None=None
    leetcode:str|None=None
    github:str|None=None

    skills:list[str]=[]
    education:list[Education]=[]
    experience:list[Experience]=[]
    projects:list[Project]=[]

    achievements:list[str]=[]

class JobDescriptionModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company:str
    role:str

    required_skills: list[str] = Field(min_length=1) 
    preferred_skills: list[str]
    qualifications: list[str]
    responsibilities: list[str]

    experience_required:str|None=None

class Profiles(BaseModel):
    email:str|None=None
    linkedin:str|None=None
    github:str|None=None
    leetcode:str|None=None
    geeksforgeeks:str|None=None
    project_links:list[str]=[]

class ResumeCompareModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_name:str

    profiles:Profiles | None = None
    
    match_score:int

    decision:str | None = None

    matched_skills:list[str]

    missing_skills:list[str]

    strengths:list[str]
    
    weakness:list[str]
    
    suggestions:str
    
    best_project:str
