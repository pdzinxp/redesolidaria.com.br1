"""
Model: InstitutionSuggestion

Representa uma instituição SUGERIDA por um visitante do site, ainda não
publicada. Isso existe para resolver um problema de segurança/design:
antes, o cadastro de instituições ficava "próximo demais" das páginas
públicas. Agora, qualquer visitante pode sugerir uma instituição, mas
apenas um administrador logado pode revisar e efetivamente publicá-la
(criando um registro real em `Institution`).
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base

STATUS_PENDENTE = "pendente"
STATUS_APROVADA = "aprovada"
STATUS_REJEITADA = "rejeitada"


class InstitutionSuggestion(Base):
    __tablename__ = "institution_suggestions"

    id = Column(Integer, primary_key=True, index=True)

    # Dados da instituição sugerida (mais simples que o cadastro completo —
    # coordenadas, fotos e tipos de doação são preenchidos pelo admin
    # somente quando a sugestão é aprovada e vira uma instituição de verdade).
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(2), nullable=False)
    zip_code = Column(String(9), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(150), nullable=True)

    # Dados de quem está sugerindo, para o admin poder confirmar informações
    suggested_by_name = Column(String(150), nullable=False)
    suggested_by_contact = Column(String(150), nullable=False)

    status = Column(String(20), default=STATUS_PENDENTE, nullable=False)
    admin_notes = Column(Text, nullable=True)

    # Preenchido quando a sugestão é aprovada e uma instituição real é criada.
    linked_institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=True)
    linked_institution = relationship("Institution")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<InstitutionSuggestion id={self.id} name={self.name!r} status={self.status!r}>"
