"""
Model: HelpRequest

Representa uma solicitação de ajuda feita por uma pessoa.

AVISO ÉTICO IMPORTANTE (leia antes de mexer neste arquivo):
Este sistema NÃO decide quem "merece" ou "não merece" receber ajuda.
O campo `organization_score` existe apenas para ajudar a ORGANIZAR a lista
de solicitações (por exemplo, ordenar por urgência aparente com base nos
dados informados), mas ele é só uma ferramenta operacional. A avaliação
real de cada caso deve sempre ser feita por uma instituição ou profissional
responsável — nunca automaticamente pelo sistema. Por isso o campo não se
chama "priority" nem "deserves_help": o nome já deixa claro que é apenas
apoio à organização, não um veredito.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.database import Base

STATUS_PENDENTE = "pendente"
STATUS_ATENDIDA = "atendida"


class HelpRequest(Base):
    __tablename__ = "help_requests"

    id = Column(Integer, primary_key=True, index=True)

    # Dados da pessoa solicitante
    name = Column(String(150), nullable=False)
    age = Column(Integer, nullable=True)
    household_size = Column(Integer, nullable=True)  # nº de pessoas na residência
    family_income = Column(Numeric(10, 2), nullable=True)  # renda familiar mensal

    # Localização (usada para direcionar a instituições próximas)
    city = Column(String(100), nullable=False)
    neighborhood = Column(String(100), nullable=True)

    # Tipo de ajuda necessária (reaproveita as mesmas categorias de doação)
    help_type_id = Column(Integer, ForeignKey("donation_types.id"), nullable=False)

    description = Column(Text, nullable=False)
    contact = Column(String(150), nullable=False)

    # Ferramenta de organização interna — NUNCA um julgamento de mérito.
    # Ver aviso ético no topo deste arquivo.
    organization_score = Column(Integer, default=0, nullable=False)

    # Controle de acompanhamento: se a solicitação já foi atendida por
    # alguma instituição ou ainda está em aberto. Isso é só um controle de
    # fluxo de trabalho do admin — não afeta em nada a avaliação do caso.
    status = Column(String(20), default=STATUS_PENDENTE, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # ---------- Relacionamentos ----------
    help_type = relationship("DonationType")

    def __repr__(self):
        return f"<HelpRequest id={self.id} name={self.name!r}>"
