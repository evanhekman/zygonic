import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from google import generativeai as genai
from typing import Optional
import uvicorn
from dotenv import load_dotenv
import integrations
import logging
import json

load_dotenv()

logger = logging.getLogger(__name__)

# fastapi config
app = FastAPI(title="Gemini API Backend", version="1.0.0")
logging.info('app started')

# api config
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
with open("server/backbone.txt") as f:
    model = genai.GenerativeModel(
        'gemini-2.5-flash',
        system_instruction=f.read()
    )
logging.info('model configured')


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
        model_response = model.generate_content(query)
        logging.info(model_response.text)
        return model_response.text

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
    Receives a task, gets a tool call from Gemini, and executes it.
    """
    logging.info(f"Received task: {task}")
    
    ai_response_str = query_gemini(task)
    logging.info(f"response from gemini: {ai_response_str}")

    try:
        if ai_response_str.startswith("```json"):
            ai_response_str = ai_response_str.strip("```json\n").strip("`")

        tool_call_data = json.loads(ai_response_str)
        tool_name = tool_call_data.get("tool_name")
        parameters = tool_call_data.get("parameters")

        if not tool_name or not parameters:
            raise ValueError("Missing 'tool_name' or 'parameters' in AI response.")

    except (json.JSONDecodeError, ValueError) as e:
        logging.error(f"Failed to parse AI response as JSON: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Could not understand AI response. Expected JSON. Got: {ai_response_str}"
        )

    logging.info(f"executing tool '{tool_name}' with parameters: {parameters}")    
    result = integrations.execute_tool(
        tool_name=tool_name, 
        parameters=parameters
    )

    if result is None:
         raise HTTPException(
            status_code=500,
            detail=f"Webhook call for tool '{tool_name}' failed."
        )

    return {"status": "Tool executed successfully", "result": result}


if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "server:app", 
        host="127.0.0.1", 
        port=8000,
        reload=True  # Auto-reload on code changes during development
    )
