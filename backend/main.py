from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from models import LoginRequest, LoginResponse, ScrapeRequest, ScrapeResponse
from auth_service import auth_service
from scraper_service import scraper_service
from scrapers.odoo_scraper import scrape_odoo
from scrapers.prompting_guide_scraper import scrape_prompting_guide
from scrapers.isams_developer_scraper import scrape_isams_developer
from scrapers.toddle_scraper import scrape_toddle

app = FastAPI(title="iSAMS Documentation Scraper")

# CORS Configuration
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PublicScrapeRequest(BaseModel):
    url: str

class PublicScrapeResponse(BaseModel):
    success: bool
    markdown_content: str
    message: str

@app.get("/")
def read_root():
    return {"status": "ok", "message": "iSAMS Scraper Backend Ready"}

@app.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    # Deprecated: Automated login
    success, message = auth_service.login(request.username, request.password)
    if not success:
        raise HTTPException(status_code=401, detail=message)
    return LoginResponse(success=True, message=message)

@app.post("/launch-login")
def launch_login():
    success, message = auth_service.launch_login()
    return {"success": success, "message": message}

@app.get("/check-auth")
def check_auth():
    success, message = auth_service.check_authentication()
    return {"success": success, "message": message}

@app.post("/scrape", response_model=ScrapeResponse)
def scrape(request: ScrapeRequest):
    success, message, articles, markdown = scraper_service.scrape_category(request.category_url)
    if not success:
        raise HTTPException(status_code=500, detail=message)
    return ScrapeResponse(
        success=True, 
        message=message, 
        articles=articles, 
        markdown_content=markdown
    )

@app.post("/scrape-odoo", response_model=PublicScrapeResponse)
def api_scrape_odoo(request: PublicScrapeRequest):
    try:
        markdown = scrape_odoo(request.url)
        return PublicScrapeResponse(success=True, markdown_content=markdown, message="Successfully scraped Odoo docs")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrape-prompting-guide", response_model=PublicScrapeResponse)
def api_scrape_prompting_guide(request: PublicScrapeRequest):
    try:
        markdown = scrape_prompting_guide(request.url)
        return PublicScrapeResponse(success=True, markdown_content=markdown, message="Successfully scraped Prompting Guide")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrape-isams-developer", response_model=PublicScrapeResponse)
def api_scrape_isams_developer(request: PublicScrapeRequest):
    try:
        driver = auth_service.get_driver()
        markdown = scrape_isams_developer(request.url, driver)
        return PublicScrapeResponse(success=True, markdown_content=markdown, message="Successfully scraped iSAMS Developer Docs")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrape-toddle", response_model=PublicScrapeResponse)
def api_scrape_toddle(request: PublicScrapeRequest):
    try:
        driver = auth_service.get_driver()
        articles_list, markdown = scrape_toddle(request.url, driver)
        return PublicScrapeResponse(success=True, markdown_content=markdown, message="Successfully scraped Toddle Documentation")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=False)
