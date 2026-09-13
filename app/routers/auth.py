"""
Rotas de login e logout do administrador.

Ficam sob /admin, mas de propósito FORA da proteção de autenticação
(afinal, é aqui que o login acontece — não faria sentido exigir login
para acessar a tela de login).
"""

from urllib.parse import quote, urlparse

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth_service import authenticate_user
from app.templating import templates

router = APIRouter(prefix="/admin", tags=["auth"])


def _safe_next_path(next_path: str) -> str:
    """
    Só permite redirecionar para caminhos internos do próprio site
    (começando com "/"), nunca para outro domínio. Isso evita que alguém
    manipule o link de login para redirecionar a vítima para um site
    malicioso depois de autenticar.
    """
    if not next_path:
        return "/admin"
    parsed = urlparse(next_path)
    if parsed.scheme or parsed.netloc or not next_path.startswith("/"):
        return "/admin"
    return next_path


@router.get("/login")
def login_form(request: Request, next: str = "/admin", erro: str = ""):
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request, "next": _safe_next_path(next), "erro": erro},
    )


@router.post("/login")
def login_submit(
    request: Request,
    db: Session = Depends(get_db),
    username: str = Form(...),
    password: str = Form(...),
    next: str = Form("/admin"),
):
    user = authenticate_user(db, username.strip(), password)
    safe_next = _safe_next_path(next)

    if user is None:
        error_message = quote("Usuário ou senha inválidos.")
        return RedirectResponse(
            url=f"/admin/login?erro={error_message}&next={quote(safe_next)}",
            status_code=303,
        )

    request.session["user_id"] = user.id
    request.session["username"] = user.username
    return RedirectResponse(url=safe_next, status_code=303)


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/admin/login", status_code=303)
