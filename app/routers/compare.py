from fastapi import FastAPI,APIRouter,UploadFile,File
from typing import List
from ..services.compare import compare_resume
router=APIRouter(
    prefix="/compare",
    tags=["Compare Resume Against JD"]
)
@router.post("/")
async def post(resume_zip:UploadFile=File(),JD_file:UploadFile=File()):
    return await compare_resume(resume_zip,JD_file)