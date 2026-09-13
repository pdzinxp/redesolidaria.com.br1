"""
Ponto de entrada da aplicação Rede Solidária.

Este arquivo:
1. Cria a aplicação FastAPI.
2. Configura o middleware de sessão (necessário para o login do admin).
3. Monta as pastas de arquivos estáticos (CSS, JS, imagens, uploads).
4. Cria as tabelas do banco e os dados iniciais (admin padrão + categorias).
5. Registra todos os routers da aplicação.

Para rodar localmente (a partir da pasta rede-solidaria/):
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import SECRET_KEY, STATIC_DIR, UPLOADS_DIR
from app.database import Base, SessionLocal, engine
from app.routers import (
    admin,
    auth,
    feedback,
    help_requests,
    institution_suggestions,
    institutions,
    map as map_router,
    pages,
    stats,
)
from app.services.auth_service import seed_default_admin
from app.services.migration_service import run_lightweight_migrations
from app.services.seed_service import seed_donation_types

# Importa os models para que o SQLAlchemy "os conheça" antes de criar as
# tabelas.
from app import models  # noqa: F401

app = FastAPI(title="Rede Solidária")

# Necessário para o login administrativo funcionar (guarda o id do usuário
# logado em um cookie de sessão assinado).
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Cria as tabelas do banco de dados que ainda não existem.
# (Em um projeto maior usaríamos migrations com Alembic, mas para este
# projeto escolar, criar as tabelas automaticamente é simples e suficiente.)
Base.metadata.create_all(bind=engine)

# Adiciona colunas novas a tabelas já existentes de execuções anteriores
# (veja o comentário em app/services/migration_service.py).
run_lightweight_migrations(engine)

# Dados iniciais: categorias de doação padrão + administrador padrão.
_db = SessionLocal()
try:
    seed_donation_types(_db)
    seed_default_admin(_db)
finally:
    _db.close()

# Arquivos estáticos do próprio site (CSS, JS, imagens fixas do layout)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Imagens enviadas pelo administrador (uploads), servidas em /uploads/...
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

# Registra as rotas da aplicação.
# IMPORTANTE: institution_suggestions precisa vir ANTES de institutions,
# porque /instituicoes/sugerir precisa ser reconhecida antes da rota
# dinâmica /instituicoes/{institution_id} — senão "sugerir" seria
# interpretado como um tentativa de ID de instituição e retornaria erro.
app.include_router(pages.router)
app.include_router(institution_suggestions.router)
app.include_router(institutions.router)
app.include_router(map_router.router)
app.include_router(help_requests.router)
app.include_router(stats.router)
app.include_router(feedback.router)
app.include_router(auth.router)
app.include_router(admin.router)
