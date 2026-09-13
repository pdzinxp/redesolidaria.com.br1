"""
Página pública de estatísticas do sistema. Usa consultas já existentes em
institution_service.py, então esta rota fica bem enxuta.
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import DonationType
from app.services import feedback_service, institution_service, site_settings_service
from app.templating import templates

router = APIRouter(tags=["stats"])


@router.get("/estatisticas")
def stats_page(request: Request, db: Session = Depends(get_db)):
    stats = institution_service.get_public_stats(db)
    institutions_per_city = institution_service.get_institutions_per_city(db)
    most_needed = institution_service.get_most_needed_donation_types(db)
    total_categories = db.query(DonationType).count()
    site_settings = site_settings_service.get_settings(db)
    feedback_average = feedback_service.get_average_rating(db)
    feedback_count = feedback_service.count_feedbacks(db)
    recent_feedbacks = feedback_service.list_feedbacks(db, limit=3)

    max_per_city = max([count for _, count in institutions_per_city], default=1)
    max_needed = max([count for _, count in most_needed], default=1)

    return templates.TemplateResponse(
        "stats.html",
        {
            "request": request,
            "stats": stats,
            "total_categories": total_categories,
            "institutions_per_city": institutions_per_city,
            "most_needed": most_needed,
            "max_per_city": max_per_city,
            "max_needed": max_needed,
            "site_settings": site_settings,
            "feedback_average": feedback_average,
            "feedback_count": feedback_count,
            "recent_feedbacks": recent_feedbacks,
        },
    )
