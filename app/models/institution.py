"""
Model: Institution

Representa uma instituição ou ponto de doação cadastrado na plataforma
(ex: um centro comunitário, uma ONG, um ponto de coleta).
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.institution_donation_type import institution_donation_types


class Institution(Base):
    __tablename__ = "institutions"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)

    # Endereço
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(2), nullable=False)  # sigla, ex: "SP"
    zip_code = Column(String(9), nullable=True)  # formato 00000-000

    # Coordenadas geográficas, usadas para exibir a instituição no mapa
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    # Contato
    phone = Column(String(20), nullable=True)
    email = Column(String(150), nullable=True)
    opening_hours = Column(String(255), nullable=True)

    # Controle
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Ordem de exibição nos cards/carrossel, definida manualmente pelo admin
    # (botões "mover para cima/baixo" no painel). Por padrão todas as
    # instituições começam empatadas em 0, e nesse caso a ordenação cai de
    # volta para "mais recente primeiro" (created_at) — ou seja, nada muda
    # pra quem nunca usar os botões de reordenar.
    display_order = Column(Integer, default=0, nullable=False)

    # ---------- Relacionamentos ----------

    # Uma instituição tem várias imagens (relação um-para-muitos).
    # cascade="all, delete-orphan" garante que, se a instituição for
    # excluída, as imagens associadas a ela também sejam removidas do banco
    # (a exclusão do arquivo físico é tratada à parte, pelo image_service).
    images = relationship(
        "InstitutionImage",
        back_populates="institution",
        cascade="all, delete-orphan",
        order_by="InstitutionImage.uploaded_at",
    )

    # Uma instituição aceita vários tipos de doação, e cada tipo pode ser
    # aceito por várias instituições (relação muitos-para-muitos).
    donation_types = relationship(
        "DonationType",
        secondary=institution_donation_types,
        backref="institutions",
    )

    def __repr__(self):
        return f"<Institution id={self.id} name={self.name!r}>"

    @property
    def main_image(self):
        """Retorna a imagem marcada como principal, ou a primeira disponível."""
        for image in self.images:
            if image.is_main:
                return image
        return self.images[0] if self.images else None
