"""
Serviço de autenticação.

Implementa o hash e a verificação de senha usando apenas a biblioteca
padrão do Python (hashlib + secrets), sem depender de pacotes externos
como bcrypt. O algoritmo usado é PBKDF2-HMAC-SHA256, que é considerado
seguro e é o mesmo tipo de abordagem usada por frameworks como o Django.

Formato do hash salvo no banco: "salt_em_hexadecimal$hash_em_hexadecimal"
"""

import hashlib
import hmac
import secrets
from typing import Optional

from sqlalchemy.orm import Session

from app.config import DEFAULT_ADMIN_PASSWORD, DEFAULT_ADMIN_USERNAME
from app.models import User

PBKDF2_ITERATIONS = 260_000


def hash_password(password: str) -> str:
    """Gera um novo salt aleatório e retorna 'salt$hash'."""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), PBKDF2_ITERATIONS
    )
    return f"{salt}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """Confere se a senha informada corresponde ao hash salvo no banco."""
    try:
        salt, expected_hex = password_hash.split("$")
    except ValueError:
        return False

    actual_digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), PBKDF2_ITERATIONS
    )
    # hmac.compare_digest evita "timing attacks": comparar strings com "=="
    # normal pode vazar informação sobre quantos caracteres já bateram.
    return hmac.compare_digest(actual_digest.hex(), expected_hex)


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Retorna o usuário se as credenciais forem válidas, ou None caso contrário."""
    user = (
        db.query(User)
        .filter(User.username == username, User.is_active.is_(True))
        .first()
    )
    if user and verify_password(password, user.password_hash):
        return user
    return None


def seed_default_admin(db: Session) -> None:
    """
    Cria o administrador padrão na primeira vez que o sistema roda, caso
    ainda não exista nenhum usuário cadastrado. Isso evita que o projeto
    "nasça" sem nenhuma forma de acessar o painel administrativo.
    """
    if db.query(User).count() > 0:
        return

    admin = User(
        username=DEFAULT_ADMIN_USERNAME,
        password_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
    )
    db.add(admin)
    db.commit()

    print("=" * 64)
    print("Administrador padrão criado automaticamente:")
    print(f"  usuário: {DEFAULT_ADMIN_USERNAME}")
    print(f"  senha:   {DEFAULT_ADMIN_PASSWORD}")
    print("Acesse /admin/login para entrar. Troque essa senha depois.")
    print("=" * 64)


def update_credentials(
    db: Session,
    user: User,
    current_password: str,
    new_username: str,
    new_password: str,
) -> list:
    """
    Atualiza usuário e/ou senha do administrador logado.

    Regras:
    - A senha ATUAL sempre precisa ser confirmada corretamente, mesmo que
      a pessoa só queira trocar o nome de usuário — isso evita que alguém
      que já tenha uma sessão aberta (esquecida em um computador
      compartilhado, por exemplo) mude as credenciais sem saber a senha.
    - O novo nome de usuário não pode já pertencer a outro usuário.
    - A nova senha (se informada) precisa ter pelo menos 6 caracteres.

    Retorna uma lista de mensagens de erro (vazia se tudo deu certo).
    """
    errors = []

    if not verify_password(current_password, user.password_hash):
        errors.append("Senha atual incorreta.")
        return errors

    new_username = new_username.strip()
    if not new_username:
        errors.append("O nome de usuário não pode ficar vazio.")
    elif new_username != user.username:
        existing = db.query(User).filter(User.username == new_username, User.id != user.id).first()
        if existing:
            errors.append("Já existe outro usuário com esse nome.")

    if new_password and len(new_password) < 6:
        errors.append("A nova senha deve ter pelo menos 6 caracteres.")

    if errors:
        return errors

    user.username = new_username
    if new_password:
        user.password_hash = hash_password(new_password)
    db.commit()

    return []
