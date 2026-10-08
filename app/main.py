from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

import app.models  # noqa: F401  # register SQLAlchemy models before creating tables
from app.db import Base, SessionLocal, engine
from app.migrations import ensure_columns
from app.seed import seed_data
from app.services.content_service import (
    get_education,
    get_experiences,
    get_project_by_slug,
    get_projects,
    get_skills_by_category,
)
from app.services.profile_service import get_public_profile

app = FastAPI(title="Career Platform")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.exception_handler(StarletteHTTPException)
async def not_found_page(request: Request, exc: StarletteHTTPException):
    if exc.status_code != 404 or request.url.path.startswith("/api/"):
        return await http_exception_handler(request, exc)
    return templates.TemplateResponse(
        "404.html",
        {"request": request, "profile": get_public_profile()},
        status_code=404,
    )


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    ensure_columns(engine)
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    profile = get_public_profile()
    projects = get_projects() or profile.get("featured_projects", [])
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "profile": profile, "projects": projects[:3]},
    )


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    profile = get_public_profile()
    return templates.TemplateResponse("about.html", {"request": request, "profile": profile})


@app.get("/experience", response_class=HTMLResponse)
async def experience(request: Request):
    profile = get_public_profile()
    experiences = get_experiences()
    return templates.TemplateResponse(
        "experience.html",
        {"request": request, "profile": profile, "experiences": experiences},
    )


@app.get("/projects", response_class=HTMLResponse)
async def projects(request: Request):
    profile = get_public_profile()
    projects = get_projects()
    return templates.TemplateResponse(
        "projects.html",
        {"request": request, "profile": profile, "projects": projects},
    )


@app.get("/projects/{slug}", response_class=HTMLResponse)
async def project_detail(request: Request, slug: str):
    profile = get_public_profile()
    project = get_project_by_slug(slug)
    if project is None:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(
        "project_detail.html",
        {"request": request, "profile": profile, "project": project},
    )


@app.get("/resume", response_class=HTMLResponse)
async def resume(request: Request):
    profile = get_public_profile()
    experiences = get_experiences()
    return templates.TemplateResponse(
        "resume.html",
        {
            "request": request,
            "profile": profile,
            "experiences": experiences,
            "education": get_education(),
            "skills": get_skills_by_category(),
        },
    )


@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    profile = get_public_profile()
    return templates.TemplateResponse("contact.html", {"request": request, "profile": profile})


@app.get("/api/profile")
async def api_profile():
    return get_public_profile()
