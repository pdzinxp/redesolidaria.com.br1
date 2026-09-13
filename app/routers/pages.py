"""
Rotas de páginas públicas "institucionais" do site: por enquanto, a página
inicial. As rotas de instituições ficam em institutions.py; mapa e
solicitações de ajuda terão seus próprios arquivos nas próximas etapas.
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import institution_service, site_settings_service
from app.templating import templates

router = APIRouter()


@router.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    """
    Página inicial do Rede Solidária. Estatísticas e instituições em
    destaque vêm de consultas reais ao banco de dados.
    """
    stats = institution_service.get_public_stats(db)
    site_settings = site_settings_service.get_settings(db)
    featured_institutions = institution_service.list_featured_institutions(db, limit=3)

    context = {
        "request": request,
        "stats": stats,
        "site_settings": site_settings,
        "featured_institutions": featured_institutions,
    }
    return templates.TemplateResponse("index.html", context)
