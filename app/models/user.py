"""
Model: User

Representa um administrador do sistema. Por enquanto só existe um
administrador, mas a tabela já está estruturada para permitir vários no
futuro (por isso "username" é único e não fixamos nada em código).
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Nome de usuário usado para login. Único para não haver conflito.
    username = Column(String(80), unique=True, nullable=False, index=True)

    # NUNCA armazenamos a senha em texto puro — apenas o hash gerado
    # pelo passlib/bcrypt (isso será implementado na etapa de autenticação).
    password_hash = Column(String(255), nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<User id={self.id} username={self.username!r}>"
