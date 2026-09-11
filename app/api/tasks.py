from fastapi import APIRouter, HTTPException
from ..schemas import TaskStatusResponse
from ..services.task_manager import task_manager

router = APIRouter(prefix="/tasks", tags=["Background Tasks"])

@router.get("/{task_id}", response_model=TaskStatusResponse)
def get_task_status(task_id: str):
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskStatusResponse(
        task_id=task["task_id"],
        status=task["status"],
        progress=task["progress"],
        message=task.get("message"),
        result=task.get("result"),
        error=task.get("error")
    )
