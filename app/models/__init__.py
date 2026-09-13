"""
Este arquivo importa todos os models para que:

1. O SQLAlchemy "conheça" todas as tabelas ao rodar Base.metadata.create_all()
   em app/main.py.
2. Seja possível importar de forma simples em outros arquivos, por exemplo:
       from app.models import Institution, DonationType
   em vez de:
       from app.models.institution import Institution
"""

from app.models.donation_type import DonationType
from app.models.institution_donation_type import institution_donation_types
from app.models.institution import Institution
from app.models.institution_image import InstitutionImage
from app.models.institution_suggestion import InstitutionSuggestion
from app.models.help_request import HelpRequest
from app.models.feedback import Feedback
from app.models.site_settings import SiteSettings
from app.models.user import User

__all__ = [
    "User",
    "Institution",
    "InstitutionImage",
    "InstitutionSuggestion",
    "DonationType",
    "institution_donation_types",
    "HelpRequest",
    "Feedback",
    "SiteSettings",
]
