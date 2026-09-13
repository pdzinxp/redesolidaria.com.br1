"""
Serviço de solicitações de ajuda.

AVISO ÉTICO (leia também o comentário em app/models/help_request.py):
A função `_calculate_organization_score` calcula um número simples,
baseado apenas nos dados informados no formulário, para ajudar o
administrador a ORGANIZAR a lista de solicitações (por exemplo, ver
primeiro os casos com indicadores de maior vulnerabilidade). Esse número
NUNCA deve ser tratado como uma decisão automática sobre quem "merece"
ajuda — é só uma ferramenta de organização. A avaliação de cada caso é
sempre feita por uma pessoa responsável.
"""

from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models import HelpRequest
from app.models.help_request import STATUS_ATENDIDA, STATUS_PENDENTE
from app.schemas.help_request import HelpRequestIn


def _calculate_organization_score(data: HelpRequestIn) -> int:
    """
    Calcula uma pontuação simples (0 a 6) só para ordenação da lista no
    painel administrativo. Considera renda por pessoa na residência e o
    número de pessoas no domicílio — nada além disso, e nada aqui decide
    se alguém vai ou não receber ajuda.
    """
    score = 0

    if data.family_income is not None and data.household_size:
        income_per_person = data.family_income / data.household_size
        if income_per_person < 200:
            score += 3
        elif income_per_person < 500:
            score += 2
        elif income_per_person < 1000:
            score += 1

    if data.household_size and data.household_size >= 5:
        score += 1

    if data.age is not None and (data.age < 18 or data.age >= 60):
        score += 1

    return score


def create_help_request(db: Session, data: HelpRequestIn) -> HelpRequest:
    help_request = HelpRequest(
        name=data.name,
        age=data.age,
        household_size=data.household_size,
        family_income=data.family_income,
        city=data.city,
        neighborhood=data.neighborhood,
        help_type_id=data.help_type_id,
        description=data.description,
        contact=data.contact,
        organization_score=_calculate_organization_score(data),
    )
    db.add(help_request)
    db.commit()
    db.refresh(help_request)
    return help_request


def list_help_requests(
    db: Session, order_by_score: bool = False, status: Optional[str] = None
) -> List[HelpRequest]:
    query = db.query(HelpRequest).options(joinedload(HelpRequest.help_type))
    if status:
        query = query.filter(HelpRequest.status == status)
    if order_by_score:
        query = query.order_by(HelpRequest.organization_score.desc(), HelpRequest.created_at.desc())
    else:
        query = query.order_by(HelpRequest.created_at.desc())
    return query.all()


def count_help_requests(db: Session, status: Optional[str] = None) -> int:
    query = db.query(HelpRequest)
    if status:
        query = query.filter(HelpRequest.status == status)
    return query.count()


def get_help_request_or_404(db: Session, help_request_id: int) -> HelpRequest:
    help_request = db.query(HelpRequest).filter(HelpRequest.id == help_request_id).first()
    if help_request is None:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada.")
    return help_request


def mark_as_attended(db: Session, help_request: HelpRequest) -> None:
    help_request.status = STATUS_ATENDIDA
    db.commit()


def mark_as_pending(db: Session, help_request: HelpRequest) -> None:
    help_request.status = STATUS_PENDENTE
    db.commit()
