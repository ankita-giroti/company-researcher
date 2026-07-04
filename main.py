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

class ResearchRequest(BaseModel):
    query: str

def slugify(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "", text).strip().lower()

@app.post("/research")
async def research_company(payload: ResearchRequest):
    query = payload.query.strip()
    if not query:
        raise HTTPException(400, "Query cannot be empty")
    
    try:
        # 1. Discover online endpoints
        sources = find_company_sources(query)
        if not sources:
            raise HTTPException(404, "No sources found")
        
        # 2. Slice sources down and call your fast concurrent crawler
        urls = [s["url"] for s in sources[:3]]
        pages = await _crawl_all(urls) # Concurrent processing from crawler.py
        
        # 3. Analyze text with LLM structure
        profile = extract_profile(query, pages)
        
        # 4. Compile into an output PDF document
        safe_name = slugify(query)
        pdf_path = os.path.join(OUTPUT_DIR, f"{safe_name}_report.pdf")
        build_pdf(profile, pdf_path)
        
        return {
            "status": "done",
            "profile": profile.model_dump(),
            "pdf_url": f"/research/{safe_name}/pdf",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error during /research")   # <-- logs full traceback to Render logs
        raise HTTPException(500, str(e))

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
