"""M.Y. Business Hotel HR & Payroll System — Version 2 entry point."""
from __future__ import annotations

from pathlib import Path

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.csrf import get_csrf_token, validate_csrf_token
from app.dependencies import get_current_admin
from app.models import AdminAccount
from app.ai_gateway import prepare_command, approve_command, reject_command
from app.ai_assistant import local_model_status
from app.auth import authenticate
from app.db import SessionLocal

app = FastAPI(title=settings.app_name, docs_url=None, redoc_url=None)
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret, same_site="lax", https_only=False)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0", "app": settings.app_name}


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    if request.session.get("admin_username"):
        return RedirectResponse("/dashboard", status_code=302)
    return RedirectResponse("/login", status_code=302)


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    csrf = get_csrf_token(request)
    return templates.TemplateResponse("login.html", {"request": request, "csrf_token": csrf, "error": None})


@app.post("/login")
def login_submit(request: Request, username: str = Form(...), password: str = Form(...), csrf_token: str = Form(...)):
    validate_csrf_token(request, csrf_token)
    with SessionLocal() as db:
        admin = authenticate(db, username, password)
        if admin is None:
            csrf = get_csrf_token(request)
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "csrf_token": csrf, "error": "بيانات الدخول غير صحيحة."},
                status_code=401,
            )
        request.session["admin_username"] = admin.username
        request.session["admin_session_version"] = admin.session_version
    return RedirectResponse("/dashboard", status_code=302)


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, admin: AdminAccount = Depends(get_current_admin)):
    csrf = get_csrf_token(request)
    ai_status = local_model_status()
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "admin": admin,
            "csrf_token": csrf,
            "ai_status": ai_status,
        },
    )


@app.get("/ai", response_class=HTMLResponse)
def ai_page(request: Request, admin: AdminAccount = Depends(get_current_admin)):
    csrf = get_csrf_token(request)
    ai_status = local_model_status()
    return templates.TemplateResponse(
        "ai.html",
        {
            "request": request,
            "admin": admin,
            "csrf_token": csrf,
            "ai_status": ai_status,
            "result": None,
            "confirmation": None,
        },
    )


@app.post("/ai/prepare")
def ai_prepare(
    request: Request,
    question: str = Form(...),
    csrf_token: str = Form(...),
    admin: AdminAccount = Depends(get_current_admin),
):
    validate_csrf_token(request, csrf_token)
    csrf = get_csrf_token(request)
    ai_status = local_model_status()
    try:
        confirmation = prepare_command(question, actor=admin.username)
        return templates.TemplateResponse(
            "ai.html",
            {
                "request": request,
                "admin": admin,
                "csrf_token": csrf,
                "ai_status": ai_status,
                "result": None,
                "confirmation": confirmation,
                "question": question,
            },
        )
    except Exception as exc:
        return templates.TemplateResponse(
            "ai.html",
            {
                "request": request,
                "admin": admin,
                "csrf_token": csrf,
                "ai_status": ai_status,
                "result": {"error": str(exc)},
                "confirmation": None,
                "question": question,
            },
        )


@app.post("/ai/confirm")
def ai_confirm(
    request: Request,
    confirmation_token: str = Form(...),
    csrf_token: str = Form(...),
    admin: AdminAccount = Depends(get_current_admin),
):
    validate_csrf_token(request, csrf_token)
    csrf = get_csrf_token(request)
    ai_status = local_model_status()
    try:
        message = approve_command(confirmation_token, actor=admin.username)
        return templates.TemplateResponse(
            "ai.html",
            {
                "request": request,
                "admin": admin,
                "csrf_token": csrf,
                "ai_status": ai_status,
                "result": {"success": message},
                "confirmation": None,
            },
        )
    except Exception as exc:
        return templates.TemplateResponse(
            "ai.html",
            {
                "request": request,
                "admin": admin,
                "csrf_token": csrf,
                "ai_status": ai_status,
                "result": {"error": str(exc)},
                "confirmation": None,
            },
        )


@app.post("/ai/reject")
def ai_reject(
    request: Request,
    confirmation_token: str = Form(...),
    csrf_token: str = Form(...),
    admin: AdminAccount = Depends(get_current_admin),
):
    validate_csrf_token(request, csrf_token)
    csrf = get_csrf_token(request)
    ai_status = local_model_status()
    try:
        message = reject_command(confirmation_token, actor=admin.username)
        return templates.TemplateResponse(
            "ai.html",
            {
                "request": request,
                "admin": admin,
                "csrf_token": csrf,
                "ai_status": ai_status,
                "result": {"info": message},
                "confirmation": None,
            },
        )
    except Exception as exc:
        return templates.TemplateResponse(
            "ai.html",
            {
                "request": request,
                "admin": admin,
                "csrf_token": csrf,
                "ai_status": ai_status,
                "result": {"error": str(exc)},
                "confirmation": None,
            },
        )
