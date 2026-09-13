"""
Rota pública onde qualquer visitante pode avaliar o site (1 a 5 estrelas)
e deixar um comentário opcional, sem precisar de login.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Form, Request
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.feedback import FeedbackIn
from app.services import feedback_service
from app.templating import templates

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.get("")
def feedback_form(request: Request, db: Session = Depends(get_db)):
    recent = feedback_service.list_feedbacks(db, limit=6)
    average = feedback_service.get_average_rating(db)
    total = feedback_service.count_feedbacks(db)
    return templates.TemplateResponse(
        "feedback/form.html",
        {
            "request": request,
            "errors": [],
            "enviado": False,
            "recent": recent,
            "average": average,
            "total": total,
        },
    )


@router.post("")
def submit_feedback(
    request: Request,
    db: Session = Depends(get_db),
    rating: str = Form(""),
    comment: str = Form(""),
    reviewer_name: str = Form(""),
):
    errors = []
    data = None

    try:
        rating_int = int(rating)
    except ValueError:
        rating_int = 0
        errors.append("Escolha de 1 a 5 estrelas.")

    if not errors:
        try:
            data = FeedbackIn(
                rating=rating_int,
                comment=comment.strip() or None,
                reviewer_name=reviewer_name.strip() or None,
            )
        except ValidationError as exc:
            errors = [error["msg"] for error in exc.errors()]

    recent = feedback_service.list_feedbacks(db, limit=6)
    average = feedback_service.get_average_rating(db)
    total = feedback_service.count_feedbacks(db)

    if errors:
        return templates.TemplateResponse(
            "feedback/form.html",
            {
                "request": request,
                "errors": errors,
                "enviado": False,
                "recent": recent,
                "average": average,
                "total": total,
            },
            status_code=422,
        )

    feedback_service.create_feedback(db, data)

    # Recalcula depois de salvar, para já refletir a nova avaliação.
    recent = feedback_service.list_feedbacks(db, limit=6)
    average = feedback_service.get_average_rating(db)
    total = feedback_service.count_feedbacks(db)

    return templates.TemplateResponse(
        "feedback/form.html",
        {
            "request": request,
            "errors": [],
            "enviado": True,
            "recent": recent,
            "average": average,
            "total": total,
        },
    )
