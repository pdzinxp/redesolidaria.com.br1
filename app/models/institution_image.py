"""
Model: InstitutionImage

Representa uma imagem enviada para uma instituição. Uma instituição pode
ter várias imagens (galeria), e uma delas pode ser marcada como principal
(is_main=True) para aparecer nos cards e na busca.

Esta tabela armazena apenas o CAMINHO do arquivo (file_path), nunca a
imagem em si — os arquivos ficam salvos em uploads/institutions/{id}/,
conforme implementado no image_service (próxima etapa).
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class InstitutionImage(Base):
    __tablename__ = "institution_images"

    id = Column(Integer, primary_key=True, index=True)

    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)

    # Caminho relativo do arquivo, ex: "uploads/institutions/3/foto1.jpg"
    file_path = Column(String(255), nullable=False)

    is_main = Column(Boolean, default=False, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # ---------- Relacionamentos ----------
    institution = relationship("Institution", back_populates="images")

    def __repr__(self):
        return f"<InstitutionImage id={self.id} institution_id={self.institution_id}>"
