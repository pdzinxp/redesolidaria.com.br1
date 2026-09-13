"""
Rota pública do mapa de pontos de doação.

A página em si (/mapa) só renderiza o HTML com o Leaflet. Os dados das
instituições vêm de uma rota JSON separada (/mapa/dados), que o
JavaScript do navegador consulta para desenhar os marcadores — assim
evitamos misturar lógica de banco de dados dentro do template.
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Institution
from app.templating import templates

router = APIRouter(prefix="/mapa", tags=["map"])


@router.get("")
def map_page(request: Request):
    return templates.TemplateResponse("map.html", {"request": request})


@router.get("/dados")
def map_data(db: Session = Depends(get_db)):
    institutions = (
        db.query(Institution)
        .filter(Institution.is_active.is_(True))
        .all()
    )

    return [
        {
            "id": institution.id,
            "name": institution.name,
            "latitude": institution.latitude,
            "longitude": institution.longitude,
            "address": institution.address,
            "city": institution.city,
            "state": institution.state,
            "phone": institution.phone,
            "opening_hours": institution.opening_hours,
            "donation_types": [dt.name for dt in institution.donation_types],
            "image_url": f"/{institution.main_image.file_path}" if institution.main_image else None,
            "detail_url": f"/instituicoes/{institution.id}",
        }
        for institution in institutions
    ]
