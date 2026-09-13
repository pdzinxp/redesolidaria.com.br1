"""
Instância compartilhada do Jinja2Templates.

Mantemos isso em um único lugar para que todos os routers usem a mesma
configuração de templates (mesma pasta, mesmos filtros globais, etc.).
"""

from fastapi.templating import Jinja2Templates

from app.config import SITE_NAME, TEMPLATES_DIR

templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Variáveis disponíveis em TODOS os templates, sem precisar passar
# manualmente em cada rota (ex: {{ site_name }} no HTML).
templates.env.globals["site_name"] = SITE_NAME
