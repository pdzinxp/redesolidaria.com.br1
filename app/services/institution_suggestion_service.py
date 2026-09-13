"""
Serviço de sugestões de instituição.

Fluxo completo:
1. Um visitante do site preenche o formulário público (/instituicoes/sugerir).
2. A sugestão fica com status "pendente", visível só para o admin.
3. O admin revisa em /admin/sugestoes e decide:
   - Aprovar: é redirecionado para o formulário de nova instituição, já
     preenchido com os dados da sugestão (mas ainda precisa completar
     latitude/longitude, fotos e tipos de doação antes de salvar).
   - Rejeitar: a sugestão é marcada como rejeitada, com um motivo opcional.
"""

from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Institution
from app.models.institution_suggestion import (
    STATUS_APROVADA,
    STATUS_PENDENTE,
    STATUS_REJEITADA,
    InstitutionSuggestion,
)
from app.schemas.institution_suggestion import InstitutionSuggestionIn


def create_suggestion(db: Session, data: InstitutionSuggestionIn) -> InstitutionSuggestion:
    suggestion = InstitutionSuggestion(**data.model_dump(), status=STATUS_PENDENTE)
    db.add(suggestion)
    db.commit()
    db.refresh(suggestion)
    return suggestion


def list_suggestions(db: Session, status: Optional[str] = None) -> List[InstitutionSuggestion]:
    query = db.query(InstitutionSuggestion)
    if status:
        query = query.filter(InstitutionSuggestion.status == status)
    return query.order_by(InstitutionSuggestion.created_at.desc()).all()


def count_pending_suggestions(db: Session) -> int:
    return db.query(InstitutionSuggestion).filter(InstitutionSuggestion.status == STATUS_PENDENTE).count()


def get_suggestion_or_404(db: Session, suggestion_id: int) -> InstitutionSuggestion:
    suggestion = db.query(InstitutionSuggestion).filter(InstitutionSuggestion.id == suggestion_id).first()
    if suggestion is None:
        raise HTTPException(status_code=404, detail="Sugestão não encontrada.")
    return suggestion


def approve_suggestion(db: Session, suggestion: InstitutionSuggestion) -> None:
    suggestion.status = STATUS_APROVADA
    db.commit()


def reject_suggestion(db: Session, suggestion: InstitutionSuggestion, notes: str = "") -> None:
    suggestion.status = STATUS_REJEITADA
    suggestion.admin_notes = notes or None
    db.commit()


def link_institution(db: Session, suggestion: InstitutionSuggestion, institution: Institution) -> None:
    """Chamado depois que o admin efetivamente cria a instituição a partir da sugestão."""
    suggestion.linked_institution_id = institution.id
    suggestion.status = STATUS_APROVADA
    db.commit()
