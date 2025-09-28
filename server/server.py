from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv
import logging
from action import Action
from gemini import Model
from db.db import TaskManager
from pydantic import BaseModel

load_dotenv()

logger = logging.getLogger(__name__)

app = FastAPI(title="Gemini API Backend", version="1.0.0")
logging.info('app started')

model = Model()

task_mgr = TaskManager()

@app.get("/")
async def root():
    return {"message": "hello world"}

class TaskRequest(BaseModel):
    description: str
    status: str
    progress: float

@app.post("/new")
async def start_task(request: TaskRequest):
    """
    Receives task, pings gemini, processes, commits to DB
    """
    logging.info(f"received task: {request.description}")
    resp: dict = model.query_action(request.description)
    logging.info(f"received gemini response: {resp}")

    action = Action(model_dump=resp)

    task_mgr.create_task(
        description=request.description,
        action={"action": action.to_dict()},
        status=request.status,
        progress=request.progress,
    )

    return {"status_code": 200, "message": "shit worked"}


if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "server:app", 
        host="127.0.0.1", 
        port=8000,
        reload=True  # Auto-reload on code changes during development
    )
