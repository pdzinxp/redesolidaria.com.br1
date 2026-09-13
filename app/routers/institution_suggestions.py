"""
Rota pública onde qualquer visitante pode SUGERIR uma instituição, sem
precisar de login. A sugestão não vira uma instituição publicada
automaticamente — ela só aparece no site depois que um administrador
revisa e aprova em /admin/sugestoes.
"""

from fastapi import APIRouter, Depends, Form, Request
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.institution_suggestion import InstitutionSuggestionIn
from app.services import institution_suggestion_service
from app.templating import templates

router = APIRouter(prefix="/instituicoes", tags=["institution-suggestions"])


@router.get("/sugerir")
def suggest_institution_form(request: Request):
    return templates.TemplateResponse(
        "institution_suggestions/form.html",
        {"request": request, "errors": [], "enviado": False},
    )


@router.post("/sugerir")
def submit_institution_suggestion(
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...),
    description: str = Form(""),
    address: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    zip_code: str = Form(""),
    phone: str = Form(""),
    email: str = Form(""),
    suggested_by_name: str = Form(...),
    suggested_by_contact: str = Form(...),
):
    errors = []
    data = None
    try:
        data = InstitutionSuggestionIn(
            name=name.strip(),
            description=description.strip() or None,
            address=address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_code=zip_code.strip() or None,
            phone=phone.strip() or None,
            email=email.strip() or None,
            suggested_by_name=suggested_by_name.strip(),
            suggested_by_contact=suggested_by_contact.strip(),
        )
    except ValidationError as exc:
        errors = [error["msg"] for error in exc.errors()]

    if errors:
        return templates.TemplateResponse(
            "institution_suggestions/form.html",
            {"request": request, "errors": errors, "enviado": False},
            status_code=422,
        )

    institution_suggestion_service.create_suggestion(db, data)

    return templates.TemplateResponse(
        "institution_suggestions/form.html",
        {"request": request, "errors": [], "enviado": True},
    )
