from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import datetime
import threading
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from backend.pipeline import run_pipeline, PipelineResult
from backend.config import load_config
from backend.init_supabase import initialize_schema

app = FastAPI(title="TheLobby Backend API")

# Enable CORS so the Expo web app can call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory status tracking
pipeline_status = {
    "status": "idle",
    "last_run": None,
    "last_result": None,
    "error": None
}

class SyncRequest(BaseModel):
    date: Optional[str] = None

@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.datetime.now().isoformat()}

@app.get("/status")
def get_status():
    return pipeline_status

def run_sync_task(date: Optional[str]):
    global pipeline_status
    pipeline_status["status"] = "running"
    pipeline_status["error"] = None
    try:
        config = load_config()
        result = run_pipeline(config, date)
        pipeline_status["status"] = "completed"
        pipeline_status["last_run"] = datetime.datetime.now().isoformat()
        pipeline_status["last_result"] = {
            "bills": result.bills,
            "legislators": result.legislators,
            "former_legislators": result.former_legislators,
            "bill_sponsors": result.bill_sponsors,
            "committee_members": result.committee_members,
            "vote_records": result.vote_records,
            "districts": result.districts,
            "validation_issues": result.validation_issues
        }
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        pipeline_status["status"] = "failed"
        pipeline_status["error"] = "An internal error occurred during data synchronization."
        pipeline_status["last_run"] = datetime.datetime.now().isoformat()

@app.post("/sync")
async def trigger_sync(request: SyncRequest, background_tasks: BackgroundTasks):
    global pipeline_status
    if pipeline_status["status"] == "running":
        return {"message": "Pipeline is already running", "status": pipeline_status}

    background_tasks.add_task(run_sync_task, request.date)
    return {"message": "Pipeline triggered successfully", "status": "initiated"}

@app.post("/init")
async def init_db():
    try:
        config = load_config()
        if not config.supabase_db_url:
            raise HTTPException(status_code=400, detail="SUPABASE_DB_URL is not configured")

        initialize_schema(config.supabase_db_url)
        return {"message": "Database schema initialized successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred during database initialization."
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
