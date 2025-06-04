from fastapi import APIRouter, Depends, HTTPException
from app.services.auth import get_current_user
import uuid
import asyncio
import random
from app.websocket.manager import manager
from app.celery.celery_app import celery_app

router = APIRouter()

@router.post("/tasks/run")
def run_task(current_user: dict = Depends(get_current_user)):
    try:
        task_id = str(uuid.uuid4())
        solve_tsp.delay(current_user["email"], task_id)  # ✅ работает, потому что функция ниже
        return {"status": "accepted", "task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка запуска задачи: {str(e)}")

@celery_app.task
def solve_tsp(email: str, task_id: str):
    print(f"✅ Задача началась для {email}, task_id: {task_id}")
    asyncio.run(manager.send_to_user(email, {
        "status": "STARTED",
        "task_id": task_id,
        "message": "Задача запущена"
    }))

    for i in range(1, 6):
        asyncio.run(manager.send_to_user(email, {
            "status": "PROGRESS",
            "task_id": task_id,
            "progress": i * 20
        }))
        import time; time.sleep(0.5)

    asyncio.run(manager.send_to_user(email, {
        "status": "COMPLETED",
        "task_id": task_id,
        "path": [0, 1, 2, 3, 4, 0],
        "total_distance": 123
    }))
