import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from google import generativeai as genai
from typing import Optional
import uvicorn
from dotenv import load_dotenv

load_dotenv()

# fastapi config
app = FastAPI(title="Gemini API Backend", version="1.0.0")

# api config
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
with open("prompts/backbone.txt") as f:
    model = genai.GenerativeModel(
        'gemini-2.5-flash',
        system_instruction=f.read()
    )
    
def query_gemini(query: str):
    """
    queries gemini, checking for basic error cases.
    """
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=500, 
            detail="GEMINI_API_KEY not configured"
        )
    if not model:
        raise HTTPException(
            status_code=500, 
            detail="model not initialized"
        )
    
    try:
        return model.generate_content(query)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"error during query: {str(e)}"
        )

@app.get("/")
async def root():
    return {"message": "hello world"}

@app.get("/task")
async def start_task(task: str):
    """
    function that queries multiple times to define a plan and needed integrations for the first step of the task
    """
    response = query_gemini(task).text
    print(response)
    if "<integrations>" not in response:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to return integrations: {response}"
        )
    return JSONResponse(content={
        "response": response,
        "status": "success"
    })
        



if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "server:app", 
        host="127.0.0.1", 
        port=8000,
        reload=True  # Auto-reload on code changes during development
    )
