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
from scrapers.flexischools_scraper import scrape_flexischools_category
from scrapers.toddle_scraper import scrape_toddle
from scrapers.powerschool_scraper import scrape_powerschool
from scrapers.freshservice_scraper import scrape_freshservice
from scrapers.canvas_scraper import scrape_canvas
from scrapers.seqta_scraper import scrape_seqta
from scrapers.salesforce_scraper import scrape_salesforce
from scrapers.jira_scraper import scrape_jira

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
    role: Optional[str] = "Admin"
    headless: Optional[bool] = True
    topic: Optional[str] = "General"
    category: Optional[str] = ""
    module: Optional[str] = ""

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

@app.post("/scrape-flexischools", response_model=PublicScrapeResponse)
def api_scrape_flexischools(request: PublicScrapeRequest):
    try:
        # Note: Scrape might take some time as it crawls sequentially
        markdown = scrape_flexischools_category(request.url)
        if markdown.startswith("Error") or markdown.startswith("No sections"):
            return PublicScrapeResponse(success=False, markdown_content="", message=markdown)
        return PublicScrapeResponse(success=True, markdown_content=markdown, message="Successfully scraped Flexischools docs")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scrape-powerschool", response_model=PublicScrapeResponse)
def api_scrape_powerschool(request: PublicScrapeRequest):
    try:
        # Default to True but allow override if provided in query or future UI update
        headless = request.headless if hasattr(request, 'headless') else True
        driver = auth_service.get_driver(headless=headless)
        if not driver:
            return PublicScrapeResponse(success=False, markdown_content="", message="Failed to initialize browser (likely profile lock)")
            
        markdown = scrape_powerschool(request.url, request.role, driver)
        if markdown.startswith("Error"):
             return PublicScrapeResponse(success=False, markdown_content="", message=markdown)
        return PublicScrapeResponse(success=True, markdown_content=markdown, message="Successfully scraped PowerSchool Docs")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scrape-freshservice", response_model=PublicScrapeResponse)
def api_scrape_freshservice(request: PublicScrapeRequest):
    try:
        markdown = scrape_freshservice(request.url, request.topic)
        if markdown.startswith("Error"):
             return PublicScrapeResponse(success=False, markdown_content="", message=markdown)
        return PublicScrapeResponse(success=True, markdown_content=markdown, message="Successfully scraped FreshService Docs")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scrape-classlink", response_model=PublicScrapeResponse)
def api_scrape_classlink(request: PublicScrapeRequest):
    try:
        from scrapers.classlink_scraper import scrape_classlink
        driver = auth_service.get_driver()
        if not driver:
            return PublicScrapeResponse(success=False, markdown_content="", message="Browser not initialized.")
        articles_list, markdown = scrape_classlink(request.url, request.topic, driver)
        return PublicScrapeResponse(success=True, markdown_content=markdown, message="Successfully scraped ClassLink Documentation")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scrape-jamf", response_model=PublicScrapeResponse)
def api_scrape_jamf(request: PublicScrapeRequest):
    try:
        from scrapers.jamf_scraper import JamfScraper
        scraper = JamfScraper(auth_service)
        # Use scrape_category: auto-detects children from TOC tree.
        # Falls back to single article if the node is a leaf.
        success, message, result = scraper.scrape_category(request.url)
        if not success:
            return PublicScrapeResponse(success=False, markdown_content="", message=message)
        
        md_content = f"---\nProduct: {result['product']}\nGroup: {result['group']}\nArticle Name: {result['article_name']}\nArticle Link: {result['article_link']}\n---\n\n{result['content']}"
        return PublicScrapeResponse(success=True, markdown_content=md_content, message=message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrape-canvas", response_model=PublicScrapeResponse)
def api_scrape_canvas(request: PublicScrapeRequest):
    try:
        markdown = scrape_canvas(request.url, request.category)
        if markdown.startswith("Error"):
             return PublicScrapeResponse(success=False, markdown_content="", message=markdown)
        return PublicScrapeResponse(success=True, markdown_content=markdown, message="Successfully scraped Canvas LMS Docs")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrape-seqta", response_model=PublicScrapeResponse)
def api_scrape_seqta(request: PublicScrapeRequest):
    try:
        driver = auth_service.get_driver(headless=request.headless)
        if not driver:
            return PublicScrapeResponse(success=False, markdown_content="", message="Browser not initialized.")
        articles_list, markdown = scrape_seqta(request.url, request.category, driver)
        return PublicScrapeResponse(success=True, markdown_content=markdown, message="Successfully scraped SEQTA Resources")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrape-salesforce", response_model=PublicScrapeResponse)
def api_scrape_salesforce(request: PublicScrapeRequest):
    try:
        markdown = scrape_salesforce(request.url, request.module)
        if markdown.startswith("Error"):
             return PublicScrapeResponse(success=False, markdown_content="", message=markdown)
        return PublicScrapeResponse(success=True, markdown_content=markdown, message="Successfully scraped Salesforce Guideline")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrape-jira", response_model=PublicScrapeResponse)
def api_scrape_jira(request: PublicScrapeRequest):
    try:
        driver = auth_service.get_driver(headless=request.headless)
        if not driver:
            return PublicScrapeResponse(success=False, markdown_content="", message="Browser not initialized.")
        markdown = scrape_jira(request.url, request.topic, driver, request.headless)
        if markdown.startswith("Error"):
             return PublicScrapeResponse(success=False, markdown_content="", message=markdown)
        return PublicScrapeResponse(success=True, markdown_content=markdown, message="Successfully scraped Jira Scrum guidelines")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("Starting server on http://localhost:8002")
    uvicorn.run(app, host="0.0.0.0", port=8002)

