from fastapi import FastAPI
from .routers import analyse,compare
app=FastAPI(title="Resume Evaluator API")

@app.get("/")
def check():
    return {"message":"Resume Evaluator API"}
app.include_router(analyse.router)
app.include_router(compare.router)