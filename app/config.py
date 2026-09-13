"""
Configurações centrais do projeto Rede Solidária.

Mantemos aqui os caminhos e constantes usados em várias partes do sistema,
para não espalhar "números mágicos" pelo código.
"""

from pathlib import Path

# Diretório raiz do projeto (rede-solidaria/)
BASE_DIR = Path(__file__).resolve().parent.parent

# Diretório da aplicação (rede-solidaria/app/)
APP_DIR = BASE_DIR / "app"

# Diretório de arquivos estáticos (CSS, JS, imagens fixas do site)
STATIC_DIR = APP_DIR / "static"

# Diretório de templates HTML (Jinja2)
TEMPLATES_DIR = APP_DIR / "templates"

# Diretório onde ficam as imagens enviadas pelo administrador
UPLOADS_DIR = BASE_DIR / "uploads"
INSTITUTIONS_UPLOADS_DIR = UPLOADS_DIR / "institutions"

# Caminho do banco de dados SQLite
DATABASE_URL = f"sqlite:///{BASE_DIR / 'rede_solidaria.db'}"

# Chave usada para assinar o cookie de sessão do login administrativo.
# Em um projeto real isso viria de uma variável de ambiente; aqui, como é
# um projeto escolar rodando localmente, uma constante já resolve.
SECRET_KEY = "rede-solidaria-chave-de-sessao-trocar-se-for-usar-em-producao"

# Credenciais do administrador criado automaticamente na primeira execução,
# caso ainda não exista nenhum usuário no banco.
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"

# Nome exibido do site (usado nos templates)
SITE_NAME = "Rede Solidária"
