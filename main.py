import os
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv
from search import find_company_sources
from crawler import _crawl_all  # Code 2 relies on this async worker
from extract import extract_profile
from report import build_pdf
import logging

logger = logging.getLogger("uvicorn.error")

load_dotenv()

app = FastAPI(title="Company Research API")

# ---- CORS Middleware Configuration ----
# This allows your frontend JS application to interact with your FastAPI endpoints
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ai-powered-company-researcher.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = "reports"
os.makedirs(OUTPUT_DIR, exist_ok=True)

JOBS: dict[str, dict] = {}
 
class ResearchRequest(BaseModel):
    query: str
 
def slugify(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "", text).strip().lower()
 
 
async def run_research_job(job_id: str, query: str):
    """Runs the full crawl -> extract -> PDF pipeline in the background."""
    try:
        JOBS[job_id]["status"] = "crawling"
 
        sources = find_company_sources(query)
        if not sources:
            JOBS[job_id] = {"status": "error", "error": "No sources found"}
            return
 
        urls = [s["url"] for s in sources[:8]]
        pages = await _crawl_all(urls)
 
        JOBS[job_id]["status"] = "extracting"
        profile = extract_profile(query, pages)
 
        JOBS[job_id]["status"] = "building_pdf"
        safe_name = slugify(query)
        pdf_path = os.path.join(OUTPUT_DIR, f"{safe_name}_report.pdf")
        build_pdf(profile, pdf_path)
 
        JOBS[job_id] = {
            "status": "done",
            "profile": profile.model_dump(),
            "pdf_url": f"/research/{safe_name}/pdf",
        }
    except Exception as e:
        logger.exception(f"Error during background research job {job_id}")
        JOBS[job_id] = {"status": "error", "error": str(e)}
 
 
@app.post("/research")
async def start_research(payload: ResearchRequest, background_tasks: BackgroundTasks):
    query = payload.query.strip()
    if not query:
        raise HTTPException(400, "Query cannot be empty")
 
    job_id = uuid.uuid4().hex
    JOBS[job_id] = {"status": "queued"}
 
    # Kick off the long-running work in the background; return immediately.
    background_tasks.add_task(run_research_job, job_id, query)
 
    return {"job_id": job_id, "status": "queued"}
 
 
@app.get("/research/{job_id}/status")
def get_status(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return job
 
 
@app.get("/research/{safe_name}/pdf")
def get_pdf(safe_name: str):
    path = os.path.join(OUTPUT_DIR, f"{safe_name}_report.pdf")
    if not os.path.exists(path):
        raise HTTPException(404, "Report not generated yet")
    return FileResponse(
        path,
        media_type="application/pdf",
        filename=f"{safe_name}_report.pdf"
    )
 
app.mount("/", StaticFiles(directory="template", html=True), name="static")
