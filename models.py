from pydantic import BaseModel, ConfigDict

class ResumeResponseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ats_score:int
    name:str
    mobile_no:str
    email:str
    leetcode_profile:str|None=None
    skills:list[str]|None=None
    best_project:str

class ResumeCompareModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    match_score:int
    matched_skills:list[str]|None=None
    missing_skills:list[str]|None=None
    strengths:list[str]|None=None
    weakness:list[str]|None=None
    suggestions:str
    best_project:str
