from pydantic import BaseModel,Field

class ResumeAnalysisResponse(BaseModel):
    ats_score:int=Field(ge=0,le=100)

    strengths:list[str]=Field(default_factory=list)

    weaknesses:list[str]=Field(default_factory=list)

    suggestions:list[str]=Field(default_factory=list)

    best_project:str|None=None
    
