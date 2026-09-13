"""
Rotas do painel administrativo. TODAS as rotas deste arquivo exigem um
administrador logado — isso é garantido pela dependência
`get_current_admin`, aplicada uma única vez no nível do router (veja o
parâmetro `dependencies=` logo abaixo), em vez de repetida em cada rota.
"""

from typing import List, Optional
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_admin
from app.models import User
from app.services import (
    auth_service,
    feedback_service,
    help_request_service,
    institution_service,
    institution_suggestion_service,
    site_settings_service,
)
from app.services.image_service import (
    ImageValidationError,
    delete_institution_image,
    replace_institution_image,
    save_institution_image,
    set_main_image,
)
from app.templating import templates

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(get_current_admin)])

EMPTY_VALUES = {
    "name": "", "description": "", "address": "", "city": "", "state": "",
    "zip_code": "", "latitude": "", "longitude": "", "phone": "", "email": "",
    "opening_hours": "",
}


def _values_from_institution(institution) -> dict:
    return {
        "name": institution.name,
        "description": institution.description or "",
        "address": institution.address,
        "city": institution.city,
        "state": institution.state,
        "zip_code": institution.zip_code or "",
        "latitude": institution.latitude,
        "longitude": institution.longitude,
        "phone": institution.phone or "",
        "email": institution.email or "",
        "opening_hours": institution.opening_hours or "",
    }


def _values_from_suggestion(suggestion) -> dict:
    values = dict(EMPTY_VALUES)
    values.update({
        "name": suggestion.name,
        "description": suggestion.description or "",
        "address": suggestion.address,
        "city": suggestion.city,
        "state": suggestion.state,
        "zip_code": suggestion.zip_code or "",
        "phone": suggestion.phone or "",
        "email": suggestion.email or "",
    })
    return values


def _values_from_submitted_form(name, description, address, city, state, zip_code,
                                 latitude, longitude, phone, email, opening_hours) -> dict:
    return {
        "name": name, "description": description, "address": address, "city": city,
        "state": state, "zip_code": zip_code, "latitude": latitude, "longitude": longitude,
        "phone": phone, "email": email, "opening_hours": opening_hours,
    }


# ============================================================
# DASHBOARD
# ============================================================

@router.get("")
def dashboard(request: Request, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    stats = institution_service.get_public_stats(db)
    pending_requests = help_request_service.count_help_requests(db)
    pending_suggestions = institution_suggestion_service.count_pending_suggestions(db)
    feedback_count = feedback_service.count_feedbacks(db)
    feedback_average = feedback_service.get_average_rating(db)
    site_settings = site_settings_service.get_settings(db)
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "admin": admin,
            "active": "dashboard",
            "stats": stats,
            "pending_requests": pending_requests,
            "pending_suggestions": pending_suggestions,
            "feedback_count": feedback_count,
            "feedback_average": feedback_average,
            "site_settings": site_settings,
        },
    )


# ============================================================
# INSTITUIÇÕES
# ============================================================

@router.get("/instituicoes")
def admin_list_institutions(request: Request, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    institutions = institution_service.list_institutions(db)
    return templates.TemplateResponse(
        "admin/institutions_list.html",
        {"request": request, "admin": admin, "active": "instituicoes", "institutions": institutions},
    )


@router.get("/instituicoes/nova")
def new_institution_form(
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
    sugestao: Optional[int] = None,
):
    donation_types = institution_service.get_all_donation_types(db)

    from_suggestion = None
    values = dict(EMPTY_VALUES)
    if sugestao:
        from_suggestion = institution_suggestion_service.get_suggestion_or_404(db, sugestao)
        values = _values_from_suggestion(from_suggestion)

    return templates.TemplateResponse(
        "admin/institution_form.html",
        {
            "request": request,
            "admin": admin,
            "active": "instituicoes",
            "page_title": "Cadastrar instituição",
            "institution": None,
            "values": values,
            "from_suggestion": from_suggestion,
            "donation_types": donation_types,
            "selected_type_ids": [],
            "errors": [],
            "erro_imagem": None,
        },
    )


@router.post("/instituicoes/nova")
def create_institution(
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
    name: str = Form(...),
    description: str = Form(""),
    address: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    zip_code: str = Form(""),
    latitude: str = Form(...),
    longitude: str = Form(...),
    phone: str = Form(""),
    email: str = Form(""),
    opening_hours: str = Form(""),
    is_active: Optional[str] = Form(None),
    donation_type_ids: List[int] = Form([]),
    sugestao_id: Optional[int] = Form(None),
):
    data, errors = institution_service.build_institution_data(
        name, description, address, city, state, zip_code,
        latitude, longitude, phone, email, opening_hours, is_active,
    )

    if errors:
        donation_types = institution_service.get_all_donation_types(db)
        from_suggestion = (
            institution_suggestion_service.get_suggestion_or_404(db, sugestao_id) if sugestao_id else None
        )
        return templates.TemplateResponse(
            "admin/institution_form.html",
            {
                "request": request,
                "admin": admin,
                "active": "instituicoes",
                "page_title": "Cadastrar instituição",
                "institution": None,
                "values": _values_from_submitted_form(
                    name, description, address, city, state, zip_code,
                    latitude, longitude, phone, email, opening_hours,
                ),
                "from_suggestion": from_suggestion,
                "donation_types": donation_types,
                "selected_type_ids": donation_type_ids,
                "errors": errors,
                "erro_imagem": None,
            },
            status_code=422,
        )

    institution = institution_service.create_institution(db, data, donation_type_ids)

    if sugestao_id:
        suggestion = institution_suggestion_service.get_suggestion_or_404(db, sugestao_id)
        institution_suggestion_service.link_institution(db, suggestion, institution)

    # Vai direto para a edição, para o admin já poder adicionar fotos.
    return RedirectResponse(url=f"/admin/instituicoes/{institution.id}/editar", status_code=303)


@router.get("/instituicoes/{institution_id}/editar")
def edit_institution_form(
    institution_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
    erro_imagem: Optional[str] = None,
):
    institution = institution_service.get_institution_or_404(db, institution_id)
    donation_types = institution_service.get_all_donation_types(db)
    selected_type_ids = [dt.id for dt in institution.donation_types]
    return templates.TemplateResponse(
        "admin/institution_form.html",
        {
            "request": request,
            "admin": admin,
            "active": "instituicoes",
            "page_title": "Editar instituição",
            "institution": institution,
            "values": _values_from_institution(institution),
            "from_suggestion": None,
            "donation_types": donation_types,
            "selected_type_ids": selected_type_ids,
            "errors": [],
            "erro_imagem": erro_imagem,
        },
    )


@router.post("/instituicoes/{institution_id}/editar")
def update_institution(
    institution_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
    name: str = Form(...),
    description: str = Form(""),
    address: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    zip_code: str = Form(""),
    latitude: str = Form(...),
    longitude: str = Form(...),
    phone: str = Form(""),
    email: str = Form(""),
    opening_hours: str = Form(""),
    is_active: Optional[str] = Form(None),
    donation_type_ids: List[int] = Form([]),
):
    institution = institution_service.get_institution_or_404(db, institution_id)

    data, errors = institution_service.build_institution_data(
        name, description, address, city, state, zip_code,
        latitude, longitude, phone, email, opening_hours, is_active,
    )

    if errors:
        donation_types = institution_service.get_all_donation_types(db)
        return templates.TemplateResponse(
            "admin/institution_form.html",
            {
                "request": request,
                "admin": admin,
                "active": "instituicoes",
                "page_title": "Editar instituição",
                "institution": institution,
                "values": _values_from_submitted_form(
                    name, description, address, city, state, zip_code,
                    latitude, longitude, phone, email, opening_hours,
                ),
                "from_suggestion": None,
                "donation_types": donation_types,
                "selected_type_ids": donation_type_ids,
                "errors": errors,
                "erro_imagem": None,
            },
            status_code=422,
        )

    institution_service.update_institution(db, institution, data, donation_type_ids)
    return RedirectResponse(url=f"/admin/instituicoes/{institution.id}/editar", status_code=303)


@router.post("/instituicoes/{institution_id}/excluir")
def delete_institution(institution_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    institution = institution_service.get_institution_or_404(db, institution_id)
    institution_service.delete_institution(db, institution)
    return RedirectResponse(url="/admin/instituicoes", status_code=303)


# ============================================================
# IMAGENS DAS INSTITUIÇÕES
# ============================================================

def _redirect_to_edit(institution_id: int, error_message: str = "") -> RedirectResponse:
    url = f"/admin/instituicoes/{institution_id}/editar"
    if error_message:
        url += f"?erro_imagem={quote(error_message)}"
    return RedirectResponse(url=url, status_code=303)


@router.post("/instituicoes/{institution_id}/imagens")
def upload_image(
    institution_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
    file: UploadFile = File(...),
    is_main: str = Form(None),
):
    institution = institution_service.get_institution_or_404(db, institution_id)
    try:
        save_institution_image(db, institution, file, is_main=(is_main == "on"))
    except ImageValidationError as exc:
        return _redirect_to_edit(institution_id, str(exc))
    return _redirect_to_edit(institution_id)


@router.post("/instituicoes/{institution_id}/imagens/{image_id}/principal")
def make_main_image(
    institution_id: int, image_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)
):
    institution = institution_service.get_institution_or_404(db, institution_id)
    set_main_image(db, institution, image_id)
    return _redirect_to_edit(institution_id)


@router.post("/instituicoes/{institution_id}/imagens/{image_id}/substituir")
def replace_image(
    institution_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
    file: UploadFile = File(...),
):
    institution = institution_service.get_institution_or_404(db, institution_id)
    try:
        replace_institution_image(db, institution, image_id, file)
    except ImageValidationError as exc:
        return _redirect_to_edit(institution_id, str(exc))
    return _redirect_to_edit(institution_id)


@router.post("/instituicoes/{institution_id}/imagens/{image_id}/excluir")
def delete_image(
    institution_id: int, image_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)
):
    institution = institution_service.get_institution_or_404(db, institution_id)
    delete_institution_image(db, institution, image_id)
    return _redirect_to_edit(institution_id)


# ============================================================
# SUGESTÕES DE INSTITUIÇÃO
# ============================================================

@router.get("/sugestoes")
def list_suggestions(
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
    status: str = "pendente",
):
    status_filter = status if status in {"pendente", "aprovada", "rejeitada"} else None
    suggestions = institution_suggestion_service.list_suggestions(db, status=status_filter)
    return templates.TemplateResponse(
        "admin/suggestions_list.html",
        {
            "request": request,
            "admin": admin,
            "active": "sugestoes",
            "suggestions": suggestions,
            "status_filter": status,
        },
    )


@router.post("/sugestoes/{suggestion_id}/aprovar")
def approve_suggestion(
    suggestion_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)
):
    suggestion = institution_suggestion_service.get_suggestion_or_404(db, suggestion_id)
    institution_suggestion_service.approve_suggestion(db, suggestion)
    return RedirectResponse(url=f"/admin/instituicoes/nova?sugestao={suggestion.id}", status_code=303)


@router.post("/sugestoes/{suggestion_id}/rejeitar")
def reject_suggestion(
    suggestion_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
    motivo: str = Form(""),
):
    suggestion = institution_suggestion_service.get_suggestion_or_404(db, suggestion_id)
    institution_suggestion_service.reject_suggestion(db, suggestion, notes=motivo)
    return RedirectResponse(url="/admin/sugestoes", status_code=303)


# ============================================================
# SOLICITAÇÕES DE AJUDA
# ============================================================

@router.get("/solicitacoes")
def list_help_requests(
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
    ordenar: str = "recentes",
):
    help_requests = help_request_service.list_help_requests(db, order_by_score=(ordenar == "organizacao"))
    return templates.TemplateResponse(
        "admin/help_requests_list.html",
        {
            "request": request,
            "admin": admin,
            "active": "solicitacoes",
            "help_requests": help_requests,
            "ordenar": ordenar,
        },
    )


# ============================================================
# FEEDBACKS DOS USUÁRIOS
# ============================================================

@router.get("/feedbacks")
def list_feedbacks(request: Request, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    feedbacks = feedback_service.list_feedbacks(db)
    average = feedback_service.get_average_rating(db)
    return templates.TemplateResponse(
        "admin/feedbacks_list.html",
        {
            "request": request,
            "admin": admin,
            "active": "feedbacks",
            "feedbacks": feedbacks,
            "average": average,
        },
    )


@router.post("/feedbacks/{feedback_id}/excluir")
def delete_feedback(feedback_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    feedback = feedback_service.get_feedback_or_404(db, feedback_id)
    feedback_service.delete_feedback(db, feedback)
    return RedirectResponse(url="/admin/feedbacks", status_code=303)


# ============================================================
# CONFIGURAÇÕES (números de impacto + conta do administrador)
# ============================================================

@router.get("/configuracoes")
def settings_page(
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
    erro_conta: str = "",
    sucesso_conta: str = "",
    sucesso_metricas: str = "",
):
    site_settings = site_settings_service.get_settings(db)
    return templates.TemplateResponse(
        "admin/settings.html",
        {
            "request": request,
            "admin": admin,
            "active": "configuracoes",
            "site_settings": site_settings,
            "erro_conta": erro_conta,
            "sucesso_conta": sucesso_conta,
            "sucesso_metricas": sucesso_metricas,
        },
    )


@router.post("/configuracoes/metricas")
def update_metrics(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
    people_helped: int = Form(0),
    site_visits: int = Form(0),
):
    site_settings_service.update_settings(db, people_helped, site_visits)
    return RedirectResponse(url="/admin/configuracoes?sucesso_metricas=1", status_code=303)


@router.post("/configuracoes/conta")
def update_account(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
    current_password: str = Form(...),
    new_username: str = Form(...),
    new_password: str = Form(""),
):
    errors = auth_service.update_credentials(db, admin, current_password, new_username, new_password)
    if errors:
        return RedirectResponse(
            url=f"/admin/configuracoes?erro_conta={quote(' | '.join(errors))}", status_code=303
        )
    return RedirectResponse(url="/admin/configuracoes?sucesso_conta=1", status_code=303)
