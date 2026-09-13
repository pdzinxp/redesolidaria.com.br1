"""
Rota pública onde qualquer pessoa pode solicitar ajuda, sem precisar de
login. As solicitações ficam disponíveis para o administrador em
/admin/solicitacoes.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Form, Request
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.help_request import HelpRequestIn
from app.services import help_request_service, institution_service
from app.templating import templates

router = APIRouter(prefix="/ajuda", tags=["help-requests"])


@router.get("/solicitar")
def help_request_form(request: Request, db: Session = Depends(get_db)):
    donation_types = institution_service.get_all_donation_types(db)
    return templates.TemplateResponse(
        "help_requests/form.html",
        {"request": request, "donation_types": donation_types, "errors": [], "enviado": False},
    )


@router.post("/solicitar")
def submit_help_request(
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...),
    age: str = Form(""),
    household_size: str = Form(""),
    family_income: str = Form(""),
    city: str = Form(...),
    neighborhood: str = Form(""),
    help_type_id: int = Form(...),
    description: str = Form(...),
    contact: str = Form(...),
):
    errors = []

    if not name.strip():
        errors.append("O nome é obrigatório.")
    if not city.strip():
        errors.append("A cidade é obrigatória.")
    if not description.strip():
        errors.append("Conte um pouco sobre a sua situação.")
    if not contact.strip():
        errors.append("Informe uma forma de contato (telefone, e-mail, etc.).")

    def _to_int(value: str) -> Optional[int]:
        try:
            return int(value) if value.strip() else None
        except ValueError:
            return None

    def _to_float(value: str) -> Optional[float]:
        try:
            return float(value.replace(",", ".")) if value.strip() else None
        except ValueError:
            return None

    data = None
    if not errors:
        try:
            data = HelpRequestIn(
                name=name.strip(),
                age=_to_int(age),
                household_size=_to_int(household_size),
                family_income=_to_float(family_income),
                city=city.strip(),
                neighborhood=neighborhood.strip() or None,
                help_type_id=help_type_id,
                description=description.strip(),
                contact=contact.strip(),
            )
        except ValidationError as exc:
            errors = [error["msg"] for error in exc.errors()]

    if errors:
        donation_types = institution_service.get_all_donation_types(db)
        return templates.TemplateResponse(
            "help_requests/form.html",
            {
                "request": request,
                "donation_types": donation_types,
                "errors": errors,
                "enviado": False,
            },
            status_code=422,
        )

    help_request_service.create_help_request(db, data)

    donation_types = institution_service.get_all_donation_types(db)
    return templates.TemplateResponse(
        "help_requests/form.html",
        {
            "request": request,
            "donation_types": donation_types,
            "errors": [],
            "enviado": True,
        },
    )
