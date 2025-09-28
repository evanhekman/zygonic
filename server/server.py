from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
async def create_task(request: TaskRequest):
    """
    Receives task, pings gemini, processes, commits to DB
    """
    logging.info(f"/new: {request.description}")
    resp: dict = model.query_action(request.description)
    logging.info(f"received gemini response: {resp}")

    action = Action(model_dump=resp)

    task_id = task_mgr.create_task(
        description=request.description,
        action=action.to_dict(),
        status=request.status,
        progress=request.progress,
    )

    return {"status_code": 200, "content": task_id}


@app.post("/start")
async def start_task(task_id: int):
    logging.info(f"/start_task: {task_id}")
    # Get the task first to check if it exists
    task = task_mgr.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    updated = task_mgr.update_task(task_id, status="STARTED")
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update task status")
    
    logger.info(task)
    action = Action.from_dict(task["action"])
    action.call()
    
    return {"message": f"Task {task_id} started", "task_id": task_id}


@app.delete("/delete")
async def delete_task(task_id: int):
    logging.info(f"/delete_task: {task_id}")
    deleted = task_mgr.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    return {"message": f"Task {task_id} deleted"}


@app.post("/update")
async def update_task(task_id: int, request: TaskRequest):
    logging.info(f"/update_task: {task_id}, {request.description}")
    # Check if task exists first
    existing_task = task_mgr.get_task(task_id)
    if not existing_task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    # Update the task
    updated = task_mgr.update_task(
        task_id,
        description=request.description,
        status=request.status,
        progress=request.progress
    )
    
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update task")
    
    return {"message": f"Task {task_id} updated", "task_id": task_id}


@app.get("/all")
async def get_all_tasks():
    """
    Returns all tasks from the database
    """
    logging.info("/all: fetching all tasks")
    try:
        tasks = task_mgr.get_all_tasks()
        return {"status_code": 200, "content": tasks}
    except Exception as e:
        logging.error(f"Failed to fetch all tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve tasks")


if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "server:app", 
        host="127.0.0.1", 
        port=8000,
        reload=True  # Auto-reload on code changes during development
    )
