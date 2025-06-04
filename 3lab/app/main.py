from app.api import auth, ws, tasks,tsp
from fastapi import FastAPI

app = FastAPI()
app.include_router(auth.router)
app.include_router(ws.router)
app.include_router(tasks.router)
app.include_router(tsp.router)

