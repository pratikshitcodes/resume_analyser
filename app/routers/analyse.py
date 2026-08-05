from fastapi import FastAPI,APIRouter,UploadFile,File
from app.services.analyse import analyse_resume

router=APIRouter(
    prefix="/analyse",
    tags=["Analysis"]
)

@router.post("/")
async def analysis(file:UploadFile=File()):
    return await analyse_resume(file)