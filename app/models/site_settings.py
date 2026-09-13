"""
Model: SiteSettings

Tabela "singleton" (sempre terá uma única linha, com id=1) que guarda
números de impacto exibidos no site — "pessoas ajudadas" e "visitas ao
site". Esses números são digitados manualmente pelo administrador (não
são calculados automaticamente), porque o projeto não tem um sistema de
rastreamento de visitas nem uma forma automática de contar quantas
pessoas foram efetivamente ajudadas fora da plataforma.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer

from app.database import Base


class SiteSettings(Base):
    __tablename__ = "site_settings"

    id = Column(Integer, primary_key=True)
    people_helped = Column(Integer, default=0, nullable=False)
    site_visits = Column(Integer, default=0, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
