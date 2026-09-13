"""
Dependências reutilizáveis de autenticação, usadas com Depends() nas rotas
que exigem um administrador logado.

Como esta é uma aplicação com páginas HTML (não uma API JSON pura), quando
o usuário não está autenticado nós o REDIRECIONAMOS para a tela de login,
em vez de simplesmente devolver um erro 401/403. Isso é feito lançando uma
HTTPException com status 303 e um cabeçalho "Location" — o navegador
interpreta isso como um redirecionamento normal.
"""

from urllib.parse import quote

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User


def _redirect_to_login(request: Request) -> HTTPException:
    next_path = quote(request.url.path)
    return HTTPException(status_code=303, headers={"Location": f"/admin/login?next={next_path}"})


def get_current_admin(request: Request, db: Session = Depends(get_db)) -> User:
    """
    Usada em rotas que EXIGEM um administrador logado. Se não houver
    sessão válida, redireciona para /admin/login.
    """
    user_id = request.session.get("user_id")
    if user_id:
        user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
        if user:
            return user
        # Sessão aponta para um usuário que não existe mais (ou foi
        # desativado) — limpa a sessão por segurança.
        request.session.clear()

    raise _redirect_to_login(request)


def get_optional_admin(request: Request, db: Session = Depends(get_db)):
    """
    Usada em rotas PÚBLICAS que querem saber se quem está navegando também
    é um administrador logado (por exemplo, para mostrar um botão extra de
    "editar"), mas que não exigem login para funcionar.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
