"""
Rotas PÚBLICAS de instituições: listar (com busca e filtros) e ver
detalhes. Criar, editar, excluir e gerenciar imagens vivem em
routers/admin.py, protegidas por login (veja app/dependencies.py).

IMPORTANTE (segurança/design): estas rotas e seus templates NÃO recebem
nem exibem nenhuma informação sobre o status de administrador de quem
está navegando. Ações administrativas só existem dentro de /admin — isso
evita misturar controles de gerenciamento com páginas públicas.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import DonationType, Institution
from app.services import institution_service
from app.templating import templates

router = APIRouter(prefix="/instituicoes", tags=["institutions"])


@router.get("")
def list_institutions(
    request: Request,
    db: Session = Depends(get_db),
    q: str = "",
    city: str = "",
    donation_type_id: str = "",
):
    """Lista pública de instituições ativas, com busca por nome/cidade e filtro por tipo de doação."""
    query = db.query(Institution).filter(Institution.is_active.is_(True))

    if q:
        like_pattern = f"%{q.strip()}%"
        query = query.filter(Institution.name.ilike(like_pattern))

    if city:
        query = query.filter(Institution.city.ilike(f"%{city.strip()}%"))

    # O <select> do formulário manda uma string vazia quando "Todos os tipos"
    # está selecionado — por isso o parâmetro é recebido como texto e só
    # convertido para número aqui, com segurança, em vez de deixar o FastAPI
    # tentar converter automaticamente (o que quebraria com string vazia).
    donation_type_id_int: Optional[int] = None
    if donation_type_id.strip():
        try:
            donation_type_id_int = int(donation_type_id)
        except ValueError:
            donation_type_id_int = None

    if donation_type_id_int:
        query = query.filter(Institution.donation_types.any(DonationType.id == donation_type_id_int))

    institutions = query.order_by(Institution.created_at.desc()).all()

    all_cities = institution_service.get_distinct_cities(db)
    donation_types = institution_service.get_all_donation_types(db)

    return templates.TemplateResponse(
        "institutions/list.html",
        {
            "request": request,
            "institutions": institutions,
            "filters": {"q": q, "city": city, "donation_type_id": donation_type_id_int},
            "all_cities": all_cities,
            "donation_types": donation_types,
        },
    )


@router.get("/{institution_id}")
def institution_detail(institution_id: int, request: Request, db: Session = Depends(get_db)):
    institution = institution_service.get_institution_or_404(db, institution_id)
    return templates.TemplateResponse(
        "institutions/detail.html",
        {"request": request, "institution": institution},
    )
