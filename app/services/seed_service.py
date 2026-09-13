"""
Serviço de "seed" (dados iniciais).

Popula a tabela donation_types com as categorias padrão do projeto, caso
ainda não existam. É chamado uma vez na inicialização da aplicação
(app/main.py), para que o sistema já tenha essas categorias prontas para
uso assim que o banco é criado.
"""

from sqlalchemy.orm import Session

from app.models import DonationType

DEFAULT_DONATION_TYPES = [
    "Alimentos",
    "Roupas",
    "Calçados",
    "Material escolar",
    "Produtos de higiene",
    "Móveis",
    "Cobertores",
    "Brinquedos",
    "Outros",
]


def seed_donation_types(db: Session) -> None:
    existing_names = {dt.name for dt in db.query(DonationType).all()}
    for name in DEFAULT_DONATION_TYPES:
        if name not in existing_names:
            db.add(DonationType(name=name))
    db.commit()
