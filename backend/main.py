import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from backend.database import Base, engine
from backend.models.user import User
from backend.models.profile import Profile
from backend.models.skill import Skill
from backend.models.certificate import Certificate
from backend.models.document import Document
from backend.models.association import (
    skill_documents,
    certificate_documents
)
from backend.routers.auth import router as auth_router
from backend.routers.profile import router as profile_router
from backend.routers.skill import router as skill_router
from backend.routers.certificate import router as certificate_router
from backend.routers.document import router as document_router
from backend.routers.review import router as review_router
from backend.routers.resume import router as resume_router
from backend.dependencies.auth import get_page_access_mode
from backend.models.reviewer_account import ReviewerAccount
from backend.models.resume_submission import ResumeSubmission
from backend.routers.reviewer import router as reviewer_router
from backend.routers.submission import router as submission_router

load_dotenv()

SESSION_SECRET = os.getenv(
    "SESSION_SECRET"
)

if not SESSION_SECRET:
    raise RuntimeError(
        "SESSION_SECRET is not configured"
    )

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    same_site="lax",
    https_only=False
)

Base.metadata.create_all(
    bind=engine
)

app.include_router(
    auth_router
)

app.include_router(
    profile_router
)

app.include_router(
    skill_router
)

app.include_router(
    certificate_router
)

app.include_router(
    document_router
)

app.include_router(
    review_router
)

app.include_router(
    resume_router
)

app.mount(
    "/static",
    StaticFiles(
        directory="frontend"
    ),
    name="static"
)


app.include_router(
    reviewer_router
)

app.include_router(
    submission_router
)

@app.get("/")
def root():
    return FileResponse(
        "frontend/index.html"
    )

@app.get("/register")
def register_page():
    return FileResponse(
        "frontend/register.html"
    )

@app.get("/login")
def login_page():
    return FileResponse(
        "frontend/login.html"
    )

@app.get("/dashboard")
def dashboard_page(
    request: Request
):
    access_mode = get_page_access_mode(
        request
    )

    if access_mode is None:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    if access_mode == "review":
        return RedirectResponse(
            url="/resume",
            status_code=303
        )

    return FileResponse(
        "frontend/dashboard.html"
    )

@app.get("/profile")
def profile_page(
    request: Request
):
    access_mode = get_page_access_mode(
        request
    )

    if access_mode is None:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    if access_mode == "review":
        return RedirectResponse(
            url="/resume",
            status_code=303
        )

    return FileResponse(
        "frontend/profile.html"
    )

@app.get("/skills")
def skills_page(
    request: Request
):
    access_mode = get_page_access_mode(
        request
    )

    if access_mode is None:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    if access_mode == "review":
        return RedirectResponse(
            url="/resume",
            status_code=303
        )

    return FileResponse(
        "frontend/skills.html"
    )

@app.get("/documents")
def documents_page(
    request: Request
):
    access_mode = get_page_access_mode(
        request
    )

    if access_mode is None:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    if access_mode == "review":
        return RedirectResponse(
            url="/resume",
            status_code=303
        )

    return FileResponse(
        "frontend/documents.html"
    )

@app.get("/resume")
def resume_page(
    request: Request
):
    access_mode = get_page_access_mode(
        request
    )

    if access_mode is None:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    return FileResponse(
        "frontend/resume.html"
    )

@app.get("/api")
def api_root():
    return {
        "message": "ResumeSystem API is running"
    }

@app.get("/reviewer")
def reviewer_page():
    return FileResponse(
        "frontend/reviewer.html"
    )

@app.get("/reviewer/login")
def reviewer_login_page():
    return FileResponse(
        "frontend/reviewer-login.html"
    )

@app.get("/reviewer/register")
def reviewer_register_page():
    return FileResponse(
        "frontend/reviewer-register.html"
    )

@app.get("/reviewer/dashboard")
def reviewer_dashboard_page(
    request: Request
):
    reviewer_id = request.session.get(
        "reviewer_id"
    )

    access_mode = request.session.get(
        "access_mode"
    )

    if (
        reviewer_id is None
        or access_mode != "company_reviewer"
    ):
        return RedirectResponse(
            url="/reviewer/login",
            status_code=303
        )

    return FileResponse(
        "frontend/reviewer-dashboard.html"
    )
@app.get("/reviewer/submission/{submission_id}")
def reviewer_submission_page(
    submission_id: int,
    request: Request
):
    reviewer_id = request.session.get(
        "reviewer_id"
    )

    access_mode = request.session.get(
        "access_mode"
    )

    if (
        reviewer_id is None
        or access_mode != "company_reviewer"
    ):
        return RedirectResponse(
            url="/reviewer/login",
            status_code=303
        )

    return FileResponse(
        "frontend/reviewer-submission.html"
    )
@app.get("/submit-resume")
def submit_resume_page(
    request: Request
):
    access_mode = get_page_access_mode(
        request
    )

    if access_mode is None:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    if access_mode != "owner":
        return RedirectResponse(
            url="/resume",
            status_code=303
        )

    return FileResponse(
        "frontend/submit-resume.html"
    )


os.makedirs("storage/uploads/avatars", exist_ok=True)
app.mount("/uploads/avatars", StaticFiles(directory="storage/uploads/avatars"), name="avatars")
