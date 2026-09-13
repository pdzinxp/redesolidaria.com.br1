# Rede Solidária

Projeto escolar cujo objetivo é conectar pessoas que precisam de ajuda com
instituições e pontos de doação, exibidos em um mapa colaborativo.

**Status atual do projeto:** todas as funcionalidades principais estão
implementadas e testadas: página inicial, cadastro de instituições com
upload de imagens, login administrativo, painel administrativo, mapa com
Leaflet, formulário público de solicitação de ajuda, busca/filtros e
página de estatísticas.

## Tecnologias

- **Backend:** Python + FastAPI
- **Templates:** Jinja2 (HTML renderizado no servidor)
- **Frontend:** HTML + CSS + JavaScript puro (sem frameworks)
- **Banco de dados:** SQLite (via SQLAlchemy)
- **Mapas:** Leaflet + OpenStreetMap (arquivos do Leaflet hospedados localmente no projeto — não dependem de internet para carregar, só os "tiles" do mapa em si precisam de conexão)
- **Autenticação:** sessão de servidor + senha com hash PBKDF2 (biblioteca padrão do Python, sem dependências externas)

## Como executar o projeto localmente (Windows)

### 1. Pré-requisitos

- Python 3.10 ou superior instalado. Para verificar, abra o **PowerShell** ou **Prompt de Comando** e digite:
  ```
  python --version
  ```
  Se não tiver o Python, baixe em https://www.python.org/downloads/ (marque a opção "Add Python to PATH" durante a instalação).

### 2. Baixe/extraia o projeto

Coloque a pasta `rede-solidaria` em um local de fácil acesso, por exemplo:
`C:\Users\SeuUsuario\Documents\rede-solidaria`

### 3. Abra o terminal na pasta do projeto

No Explorador de Arquivos, entre na pasta `rede-solidaria`, clique com o
botão direito em um espaço vazio e escolha **"Abrir no Terminal"** (ou
**"Abrir janela do PowerShell aqui"**).

### 4. Crie um ambiente virtual (recomendado)

```
python -m venv venv
venv\Scripts\activate
```

Você saberá que funcionou porque o terminal passará a mostrar `(venv)` no
início da linha.

### 5. Instale as dependências

```
pip install -r requirements.txt
```

### 6. Execute o servidor

```
uvicorn app.main:app --reload
```

Na primeira execução, o terminal vai mostrar algo assim:

```
================================================================
Administrador padrão criado automaticamente:
  usuário: admin
  senha:   admin123
Acesse /admin/login para entrar. Troque essa senha depois.
================================================================
Uvicorn running on http://127.0.0.1:8000
```

**Guarde essas credenciais** — são a única forma de acessar o painel
administrativo. Elas só são criadas se ainda não existir nenhum usuário
no banco (ou seja, aparecem só na primeira execução).

### 7. Acesse no navegador

- Site público: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Painel administrativo: [http://127.0.0.1:8000/admin/login](http://127.0.0.1:8000/admin/login)

Para parar o servidor, volte ao terminal e pressione `CTRL + C`.

### Observação sobre fontes

A página usa as fontes "Fraunces" e "Work Sans" do Google Fonts, carregadas
pela internet. Sem conexão, o site continua funcionando, mas usa fontes
padrão do sistema no lugar dessas duas (já existe um fallback configurado
no CSS). O mapa (Leaflet) funciona offline exceto pelos "tiles" (imagens
do mapa em si), que sempre precisam de internet — isso é uma limitação do
OpenStreetMap, não do código do projeto.

## Estrutura do projeto

```
rede-solidaria/
├── app/
│   ├── main.py                 → cria a aplicação FastAPI e registra tudo
│   ├── config.py                → caminhos, constantes e credenciais padrão
│   ├── database.py              → configuração do SQLAlchemy (engine, sessão)
│   ├── templating.py            → configuração compartilhada do Jinja2
│   ├── dependencies.py          → proteção de rotas administrativas (login)
│   ├── models/                  → tabelas do banco (User, Institution, InstitutionImage,
│   │                               InstitutionSuggestion, DonationType, HelpRequest)
│   ├── schemas/                 → validação de dados com Pydantic
│   ├── services/                → lógica de negócio (instituições, sugestões, imagens, ajuda, autenticação, seed)
│   ├── routers/
│   │   ├── pages.py             → página inicial
│   │   ├── institutions.py      → listagem e detalhe públicos (busca/filtros)
│   │   ├── institution_suggestions.py → formulário público de sugestão de instituição
│   │   ├── admin.py             → painel administrativo (protegido por login)
│   │   ├── auth.py              → login/logout
│   │   ├── map.py                → página do mapa + endpoint de dados JSON
│   │   ├── help_requests.py     → formulário público de solicitação de ajuda
│   │   └── stats.py              → página pública de estatísticas
│   ├── templates/
│   │   ├── base.html             → layout público (header + footer)
│   │   ├── index.html            → página inicial
│   │   ├── map.html               → mapa (Leaflet)
│   │   ├── stats.html             → estatísticas públicas
│   │   ├── institutions/          → listagem e detalhe públicos
│   │   ├── help_requests/         → formulário de solicitação de ajuda
│   │   ├── auth/                  → tela de login
│   │   └── admin/                 → layout e páginas do painel administrativo
│   └── static/
│       ├── css/                   → style.css (site público) e admin.css (painel)
│       ├── js/                    → main.js (menu mobile)
│       └── vendor/leaflet/        → Leaflet hospedado localmente
├── uploads/
│   └── institutions/              → imagens enviadas pelo admin (uma pasta por instituição)
├── requirements.txt
├── README.md
└── .gitignore
```

## Funcionalidades implementadas

- [x] Página inicial responsiva com estatísticas reais do banco
- [x] Cadastro, edição, exclusão e listagem de instituições (painel administrativo)
- [x] Sugestão pública de instituições, com fila de revisão/aprovação pelo admin
- [x] Upload de múltiplas imagens por instituição (com validação de tipo, tamanho e conteúdo real do arquivo)
- [x] Login administrativo com senha criptografada e proteção de rotas
- [x] Painel administrativo com dashboard, gerenciamento de instituições, sugestões e solicitações
- [x] Mapa interativo (Leaflet + OpenStreetMap) com busca
- [x] Formulário público de solicitação de ajuda
- [x] Busca e filtros de instituições (por nome, cidade, tipo de doação)
- [x] Página individual de cada instituição
- [x] Página de estatísticas com gráficos simples (instituições por cidade, tipos de doação mais pedidos)
- [x] Avaliação do site por estrelas (1 a 5) com comentário opcional, moderada pelo admin
- [x] Números de impacto editáveis pelo admin ("pessoas ajudadas" e "visitas ao site")
- [x] Troca de usuário e senha do administrador, protegida por confirmação da senha atual

## Sobre a separação entre público e administrativo

Nenhuma página pública (`/`, `/instituicoes`, `/mapa`, `/estatisticas`, etc.)
contém qualquer botão, link ou informação que dependa de estar logado como
administrador — mesmo que um admin esteja navegando pelo site com a sessão
ativa. Toda ação de gerenciamento (criar, editar, excluir instituições,
aprovar/rejeitar sugestões, ver solicitações de ajuda) vive exclusivamente
sob `/admin/*`, protegida por login. Isso evita misturar controles
administrativos com a experiência pública e reduz a chance de exposição
acidental de funcionalidades sensíveis.

Quem visita o site publicamente não cadastra instituições diretamente —
apenas **sugere** uma instituição em `/instituicoes/sugerir`. A sugestão
fica pendente em `/admin/sugestoes` até que um administrador logado
revise, complete os dados técnicos (latitude/longitude, fotos, tipos de
doação) e aprove a publicação.

## Sobre o tratamento ético dos dados de vulnerabilidade social

O campo `organization_score`, calculado a partir dos dados informados no
formulário de solicitação de ajuda, é usado **apenas para ordenar** a
lista no painel administrativo (por exemplo, mostrar primeiro casos com
indicadores de maior vulnerabilidade). Ele **não é** e nunca deve ser
apresentado como uma decisão automática sobre quem "merece" ou "não
merece" receber ajuda — isso está explícito tanto no código
(`app/models/help_request.py` e `app/services/help_request_service.py`)
quanto na interface (aviso visível no formulário público e na lista do
admin). A avaliação de cada caso é sempre responsabilidade de uma pessoa.

## Possíveis melhorias futuras

- Busca por nome sem diferenciar acentos (hoje "Esperanca" não encontra "Esperança" — limitação do SQLite `LIKE`)
- Geocodificação automática de endereço (hoje o admin precisa informar latitude/longitude manualmente)
- Permitir múltiplos administradores com diferentes níveis de permissão
- Exportar solicitações de ajuda em CSV/PDF
