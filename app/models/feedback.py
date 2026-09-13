"""
Model: Feedback

Avaliação (1 a 5 estrelas) e comentário opcional deixado por um visitante
do site. Qualquer pessoa pode enviar, sem precisar de login — o
administrador pode remover avaliações inadequadas pelo painel.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database import Base


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)

    rating = Column(Integer, nullable=False)  # de 1 a 5
    comment = Column(Text, nullable=True)
    reviewer_name = Column(String(100), nullable=True)  # opcional; "Anônimo" se vazio

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Feedback id={self.id} rating={self.rating}>"
