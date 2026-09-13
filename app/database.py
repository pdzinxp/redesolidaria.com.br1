"""
Configuração do banco de dados usando SQLAlchemy.

Este arquivo define:
- O "engine": a conexão real com o arquivo SQLite.
- O "SessionLocal": uma fábrica de sessões (conversas com o banco).
- O "Base": classe da qual todos os models (tabelas) vão herdar.
- get_db(): uma função usada pelo FastAPI para abrir e fechar uma sessão
  automaticamente a cada requisição.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL

# O argumento "check_same_thread": False é necessário porque o SQLite,
# por padrão, só permite uso na mesma thread que criou a conexão.
# O FastAPI pode atender requisições em threads diferentes, então
# precisamos liberar essa checagem.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Fábrica de sessões: cada requisição vai pedir uma sessão nova com SessionLocal()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe base da qual todos os models (tabelas) herdam
Base = declarative_base()


def get_db():
    """
    Dependência do FastAPI que fornece uma sessão de banco de dados
    para cada requisição, garantindo que ela seja sempre fechada no final,
    mesmo se ocorrer um erro.

    Uso em uma rota:

        @router.get("/exemplo")
        def exemplo(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
