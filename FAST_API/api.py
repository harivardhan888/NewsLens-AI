from fastapi import FastAPI, BackgroundTasks, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import JSONResponse
import os
import json
import sys
from dotenv import load_dotenv

# Load environments
load_dotenv()

# API Key Configuration
API_KEY = os.getenv("NEWSLENS_API_KEY", "default_secret_key_change_me")
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(header_value: str = Depends(api_key_header)):
    if header_value == API_KEY:
        return header_value
    raise HTTPException(status_code=403, detail="Could not validate API Key")

# Ensure root directory is in path so we can import local modules
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from Preprocessing.preprocessing import fetch_and_process_data
from Mail_SMTP import mail
import app

api = FastAPI(
    title="NewsLens AI Controller",
    description="API to control the NewsLens AI pipeline",
    version="1.0.0"
)

@api.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Welcome to NewsLens AI API. Go to /docs for the interactive control panel."
    }

@api.get("/news/raw")
def get_raw_news(api_key: str = Depends(get_api_key)):
    """Fetches news from BBC, CNN, and YouTube without summarizing."""
    try:
        data = fetch_and_process_data()
        return {"count": len(data), "articles": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api.get("/news/summaries")
def get_latest_summaries(api_key: str = Depends(get_api_key)):
    """Returns the most recent summarized news from the local JSON file."""
    if os.path.exists("summarized_news.json"):
        with open("summarized_news.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"message": "No summaries found. Run /pipeline/run first."}

@api.post("/pipeline/run")
def run_full_pipeline(background_tasks: BackgroundTasks, send_email: bool = True, api_key: str = Depends(get_api_key)):
    """
    Triggers the full pipeline: Fetch -> Summarize -> Email.
    It runs in the background so you don't have to wait.
    """
    def task():
        print("Starting background pipeline...")
        # 1. Run the app logic (Fetch & Summarize)
        app.main()
        # 2. Run the mailer if requested
        if send_email:
            mail.main()
            print("Background pipeline complete: News sent!")
    
    background_tasks.add_task(task)
    
    return {
        "status": "started",
        "message": "The news pipeline is running in the background. You'll receive an email shortly if successful."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api, host="127.0.0.1", port=8000)
