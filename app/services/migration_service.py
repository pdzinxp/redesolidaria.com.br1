"""
Migrações leves (sem Alembic).

Este projeto cria as tabelas automaticamente com `Base.metadata.create_all()`,
o que funciona bem para TABELAS NOVAS — mas não faz nada quando um model
existente ganha uma COLUNA nova (o SQLAlchemy não altera tabelas já
criadas). Sem isso, quem já tinha rodado o projeto antes de uma
atualização precisaria apagar o banco de dados manualmente toda vez.

Este arquivo resolve isso de forma simples: depois de criar as tabelas,
verificamos se cada coluna esperada já existe e, se não existir,
adicionamos com `ALTER TABLE ... ADD COLUMN`. Isso é suficiente para o
nosso caso (só adicionamos colunas, nunca removemos ou renomeamos).
"""

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

# Cada entrada descreve uma coluna que pode estar faltando em um banco
# criado por uma versão anterior do projeto, e o SQL para adicioná-la.
PENDING_COLUMNS = [
    {
        "table": "help_requests",
        "column": "status",
        "ddl": "ALTER TABLE help_requests ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'pendente'",
    },
]


def run_lightweight_migrations(engine: Engine) -> None:
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    with engine.begin() as connection:
        for item in PENDING_COLUMNS:
            if item["table"] not in existing_tables:
                # A tabela ainda nem existe (banco totalmente novo) — o
                # create_all() já vai criá-la com a coluna certa, então
                # não há nada a fazer aqui.
                continue

            existing_columns = {col["name"] for col in inspector.get_columns(item["table"])}
            if item["column"] not in existing_columns:
                connection.execute(text(item["ddl"]))
                print(f"[migração] Coluna '{item['column']}' adicionada à tabela '{item['table']}'.")
