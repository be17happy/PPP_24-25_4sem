from fastapi import APIRouter, Depends
from uuid import uuid4
from app.services.auth import get_current_user
from app.models.user import User
from app.api.tasks import solve_tsp  # ✅


router = APIRouter(prefix="/tsp")

@router.post("/solve/")
def start_tsp(user: User = Depends(get_current_user)):
    task_id = str(uuid4())
    solve_tsp.delay(user.email, task_id)
    return {"task_id": task_id}
@router.post("/solve/")
def solve(user: User = Depends(get_current_user)):
    task_id = str(uuid.uuid4())
    solve_tsp.delay(user.email, task_id)
    return {"task_id": task_id}
