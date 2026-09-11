import asyncio
import uuid
from typing import Dict, Any, Callable, Coroutine
from datetime import datetime, timezone

class BackgroundTaskManager:
    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}

    def create_task(self, name: str = "batch_job") -> str:
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {
            "task_id": task_id,
            "name": name,
            "status": "pending",
            "progress": 0,
            "message": "Task queued",
            "result": None,
            "error": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        return task_id

    def update_task(self, task_id: str, progress: int, message: str = "", status: str = "processing", result: Any = None, error: str = None):
        if task_id in self.tasks:
            self.tasks[task_id]["progress"] = progress
            self.tasks[task_id]["status"] = status
            if message:
                self.tasks[task_id]["message"] = message
            if result is not None:
                self.tasks[task_id]["result"] = result
            if error is not None:
                self.tasks[task_id]["error"] = error
            self.tasks[task_id]["updated_at"] = datetime.now(timezone.utc).isoformat()

    def get_task(self, task_id: str) -> Dict[str, Any] | None:
        return self.tasks.get(task_id)

    def run_async(self, coro_func: Callable[..., Coroutine], *args, **kwargs) -> str:
        task_id = self.create_task()
        asyncio.create_task(self._wrapper(task_id, coro_func, *args, **kwargs))
        return task_id

    async def _wrapper(self, task_id: str, coro_func: Callable[..., Coroutine], *args, **kwargs):
        self.update_task(task_id, progress=5, message="Starting task", status="processing")
        try:
            result = await coro_func(task_id, *args, **kwargs)
            self.update_task(task_id, progress=100, message="Task completed successfully", status="completed", result=result)
        except Exception as e:
            self.update_task(task_id, progress=100, message="Task failed", status="failed", error=str(e))

task_manager = BackgroundTaskManager()
