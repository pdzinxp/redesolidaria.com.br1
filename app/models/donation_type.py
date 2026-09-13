"""
Model: DonationType

Representa uma categoria de doação (ex: Alimentos, Roupas, Calçados...).
Essa tabela existe separada, em vez de uma lista fixa no código, para que
novas categorias possam ser adicionadas no futuro sem alterar o banco.

É usada em dois relacionamentos:
- Muitos-para-muitos com Institution (uma instituição aceita vários tipos,
  e um tipo é aceito por várias instituições) através da tabela
  institution_donation_types.
- Um-para-muitos com HelpRequest (uma solicitação de ajuda pede um tipo
  principal de ajuda).
"""

from sqlalchemy import Column, Integer, String

from app.database import Base


class DonationType(Base):
    __tablename__ = "donation_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"<DonationType id={self.id} name={self.name!r}>"
