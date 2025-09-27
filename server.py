import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import google.generativeai as genai
from typing import Optional
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Gemini API Backend", version="1.0.0")

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the model
try:
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    print(f"Warning: Could not initialize Gemini model: {e}")
    model = None

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Gemini API Backend is running"}

@app.get("/query")
async def query_gemini(q: str = Query(..., description="Query string to send to Gemini")):
    """
    Relay a query to Google Gemini and return the response
    
    Args:
        q: Query string to send to Gemini
    
    Returns:
        JSON response with Gemini's output
    """
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=500, 
            detail="GEMINI_API_KEY not configured"
        )
    
    if not model:
        raise HTTPException(
            status_code=500, 
            detail="Gemini model not initialized"
        )
    
    try:
        # Send query to Gemini
        response = model.generate_content(q)
        
        return JSONResponse(content={
            "query": q,
            "response": response.text,
            "status": "success"
        })
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error querying Gemini: {str(e)}"
        )

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "server:app", 
        host="127.0.0.1", 
        port=8000,
        reload=True  # Auto-reload on code changes during development
    )