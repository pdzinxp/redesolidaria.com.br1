"""
Tabela associativa: institution_donation_types

Esta tabela não vira uma classe/model "completa" porque ela só existe para
conectar Institution e DonationType em uma relação muitos-para-muitos
(uma instituição aceita vários tipos de doação, e um tipo de doação pode
ser aceito por várias instituições). Ela não tem nenhuma informação além
das duas chaves estrangeiras.

É usada em Institution.donation_types (veja app/models/institution.py).
"""

from sqlalchemy import Column, ForeignKey, Integer, Table

from app.database import Base

institution_donation_types = Table(
    "institution_donation_types",
    Base.metadata,
    Column("institution_id", Integer, ForeignKey("institutions.id"), primary_key=True),
    Column("donation_type_id", Integer, ForeignKey("donation_types.id"), primary_key=True),
)
