"""
Serviço de instituições.

Concentra a lógica de acesso ao banco de dados relacionada a instituições,
mantendo os routers "magros" (só cuidam de request/response) e o código
reutilizável entre diferentes rotas.
"""

from typing import List, Optional, Tuple

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session, joinedload

from app.models import DonationType, HelpRequest, Institution
from app.schemas.institution import InstitutionIn


def list_institutions(db: Session, only_active: bool = False) -> List[Institution]:
    query = db.query(Institution).options(joinedload(Institution.donation_types))
    if only_active:
        query = query.filter(Institution.is_active.is_(True))
    return query.order_by(Institution.created_at.desc()).all()


def list_featured_institutions(db: Session, limit: Optional[int] = None) -> List[Institution]:
    """
    Usado na home (seção "Pontos de doação em destaque"): instituições
    ativas mais recentes. Sem limite, traz todas — o carrossel na home é
    quem decide quantas mostrar de cada vez, com os cards rolando
    horizontalmente.
    """
    query = (
        db.query(Institution)
        .filter(Institution.is_active.is_(True))
        .order_by(Institution.created_at.desc())
    )
    if limit:
        query = query.limit(limit)
    return query.all()


def get_distinct_cities(db: Session) -> List[str]:
    """
    Lista de cidades únicas para o filtro de busca.

    Usamos Python (em vez de só `.distinct()` no SQL) de propósito: o
    `DISTINCT` do banco compara os textos exatamente como estão salvos, então
    "São Paulo", "são paulo" e " São Paulo " contam como três cidades
    diferentes se foram digitadas de formas diferentes no cadastro. Aqui
    agrupamos ignorando maiúsculas/minúsculas e espaços nas pontas, mantendo
    a primeira grafia encontrada para exibição — sem alterar nada no banco.
    """
    raw_cities = [row[0] for row in db.query(Institution.city).all() if row[0] and row[0].strip()]

    seen: dict = {}
    for raw_city in raw_cities:
        cleaned = raw_city.strip()
        key = cleaned.lower()
        if key not in seen:
            seen[key] = cleaned

    return sorted(seen.values(), key=lambda c: c.lower())


def get_institution_or_404(db: Session, institution_id: int) -> Institution:
    institution = (
        db.query(Institution)
        .options(joinedload(Institution.donation_types), joinedload(Institution.images))
        .filter(Institution.id == institution_id)
        .first()
    )
    if institution is None:
        raise HTTPException(status_code=404, detail="Instituição não encontrada.")
    return institution


def get_all_donation_types(db: Session) -> List[DonationType]:
    return db.query(DonationType).order_by(DonationType.name).all()


def _get_donation_types_by_ids(db: Session, ids: List[int]) -> List[DonationType]:
    if not ids:
        return []
    return db.query(DonationType).filter(DonationType.id.in_(ids)).all()


def create_institution(
    db: Session, data: InstitutionIn, donation_type_ids: List[int]
) -> Institution:
    institution = Institution(**data.model_dump())
    institution.donation_types = _get_donation_types_by_ids(db, donation_type_ids)
    db.add(institution)
    db.commit()
    db.refresh(institution)
    return institution


def update_institution(
    db: Session,
    institution: Institution,
    data: InstitutionIn,
    donation_type_ids: List[int],
) -> Institution:
    for field, value in data.model_dump().items():
        setattr(institution, field, value)
    institution.donation_types = _get_donation_types_by_ids(db, donation_type_ids)
    db.commit()
    db.refresh(institution)
    return institution


def delete_institution(db: Session, institution: Institution) -> None:
    db.delete(institution)
    db.commit()


# ---------- Validação de formulário (criação/edição) ----------

def _parse_coordinate(raw_value: str) -> Optional[float]:
    """Converte um texto em número decimal, aceitando vírgula ou ponto."""
    try:
        return float(raw_value.strip().replace(",", "."))
    except (AttributeError, ValueError):
        return None


def _validate_required_fields(name: str, address: str, city: str, state: str) -> List[str]:
    """Validações simples de campos obrigatórios, com mensagens em português."""
    errors = []
    if not name.strip():
        errors.append("O nome da instituição é obrigatório.")
    if not address.strip():
        errors.append("O endereço é obrigatório.")
    if not city.strip():
        errors.append("A cidade é obrigatória.")
    if not state.strip():
        errors.append("O estado é obrigatório.")
    return errors


def build_institution_data(
    name: str,
    description: str,
    address: str,
    city: str,
    state: str,
    zip_code: str,
    latitude: str,
    longitude: str,
    phone: str,
    email: str,
    opening_hours: str,
    is_active: Optional[str],
) -> Tuple[Optional[InstitutionIn], List[str]]:
    """
    Junta a validação manual (campos obrigatórios, coordenadas) com a
    validação do schema Pydantic (regras específicas de cada campo).
    Retorna os dados prontos (ou None) e a lista de erros encontrados.
    """
    errors = _validate_required_fields(name, address, city, state)

    latitude_value = _parse_coordinate(latitude)
    longitude_value = _parse_coordinate(longitude)
    if latitude_value is None:
        errors.append("Latitude inválida. Use um número, ex: -23.5505.")
    if longitude_value is None:
        errors.append("Longitude inválida. Use um número, ex: -46.6333.")

    if errors:
        return None, errors

    try:
        data = InstitutionIn(
            name=name.strip(),
            description=description.strip() or None,
            address=address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_code=zip_code.strip() or None,
            latitude=latitude_value,
            longitude=longitude_value,
            phone=phone.strip() or None,
            email=email.strip() or None,
            opening_hours=opening_hours.strip() or None,
            is_active=is_active == "on",
        )
        return data, []
    except ValidationError as exc:
        return None, [error["msg"] for error in exc.errors()]


# ---------- Estatísticas ----------

def get_public_stats(db: Session) -> dict:
    """Números exibidos na home pública."""
    return {
        "institutions": db.query(Institution).count(),
        "donation_points": db.query(Institution).filter(Institution.is_active.is_(True)).count(),
        "help_requests": db.query(HelpRequest).count(),
        "cities": db.query(Institution.city).distinct().count(),
    }


def get_institutions_per_city(db: Session) -> List[Tuple[str, int]]:
    from sqlalchemy import func

    rows = (
        db.query(Institution.city, func.count(Institution.id))
        .group_by(Institution.city)
        .order_by(func.count(Institution.id).desc())
        .all()
    )
    return rows


def get_most_needed_donation_types(db: Session) -> List[Tuple[str, int]]:
    """
    Conta quantas solicitações de ajuda pediram cada tipo de doação —
    usado na página de estatísticas para mostrar o que está mais faltando.
    """
    from sqlalchemy import func

    rows = (
        db.query(DonationType.name, func.count(HelpRequest.id))
        .join(HelpRequest, HelpRequest.help_type_id == DonationType.id)
        .group_by(DonationType.name)
        .order_by(func.count(HelpRequest.id).desc())
        .all()
    )
    return rows
