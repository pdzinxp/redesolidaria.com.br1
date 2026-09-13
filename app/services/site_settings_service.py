"""
Serviço de configurações do site — os contadores manuais de "pessoas
ajudadas" e "visitas ao site", editados pelo administrador.
"""

from sqlalchemy.orm import Session

from app.models import SiteSettings

SETTINGS_ID = 1


def get_settings(db: Session) -> SiteSettings:
    """
    Retorna a linha única de configurações, criando-a com valores zerados
    se ainda não existir (por exemplo, na primeira execução do sistema).
    """
    settings = db.query(SiteSettings).filter(SiteSettings.id == SETTINGS_ID).first()
    if settings is None:
        settings = SiteSettings(id=SETTINGS_ID, people_helped=0, site_visits=0)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def update_settings(db: Session, people_helped: int, site_visits: int) -> SiteSettings:
    settings = get_settings(db)
    settings.people_helped = max(0, people_helped)
    settings.site_visits = max(0, site_visits)
    db.commit()
    db.refresh(settings)
    return settings
