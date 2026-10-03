"""
Serviço de imagens de instituições.

Responsável por TUDO que envolve arquivos de imagem: validar, salvar no
disco, associar ao banco de dados, trocar a imagem principal, substituir
e excluir. Mantemos essa lógica separada dos routers para que as rotas
fiquem simples (só recebem a requisição e chamam estas funções).

CAMADAS DE SEGURANÇA APLICADAS AQUI:
1. Lista de extensões permitidas (allow-list, não block-list) — só aceita
   o que conhecemos, em vez de tentar bloquear "o que é perigoso".
2. Verificação do Content-Type declarado pelo navegador.
3. Limite de tamanho do arquivo.
4. Verificação do CONTEÚDO real do arquivo com Pillow — garante que os
   bytes enviados realmente formam uma imagem válida, e não um arquivo
   malicioso disfarçado com extensão de imagem.
5. Nome de arquivo sempre gerado pelo servidor (uuid), nunca o nome
   original enviado pelo usuário — evita conflitos de nome e problemas
   de caminho (path traversal).
"""

from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from PIL import Image
from sqlalchemy.orm import Session

from app.config import BASE_DIR, INSTITUTIONS_UPLOADS_DIR
from app.models import Institution, InstitutionImage

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# O Content-Type é apenas um sinal AUXILIAR — quem define esse cabeçalho é o
# navegador/sistema operacional de quem está enviando o arquivo, e isso nem
# sempre é confiável (por exemplo, alguns navegadores no Windows enviam
# "application/octet-stream" para arquivos .webp, mesmo sendo um WebP
# válido). Por isso só rejeitamos aqui quando o tipo é claramente algo que
# NÃO é imagem (ex: "text/plain", "application/pdf"); tipos ausentes ou
# genéricos passam para a validação de verdade, que é a extensão (allow-list)
# e a abertura real dos bytes com Pillow, logo abaixo.
GENERIC_CONTENT_TYPES = {"", "application/octet-stream", "binary/octet-stream"}

MAX_FILE_SIZE_MB = 20
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Maior lado (largura OU altura) que uma imagem pode ter depois de salva.
MAX_DIMENSION = 1600
JPEG_WEBP_QUALITY = 85


class ImageValidationError(Exception):
    """Erro esperado quando o arquivo enviado não passa nas validações."""


def _get_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def _generate_safe_filename(original_filename: str) -> str:
    """
    Gera um nome de arquivo totalmente novo (não usa o nome original),
    evitando conflitos entre uploads e problemas de segurança relacionados
    a nomes de arquivo manipulados pelo usuário.
    """
    extension = _get_extension(original_filename or "")
    return f"{uuid4().hex}{extension}"


def _resize_if_needed(contents: bytes, extension: str) -> bytes:
    """Redimensiona a imagem se o lado maior ultrapassar MAX_DIMENSION."""
    image = Image.open(BytesIO(contents))
    width, height = image.size

    if max(width, height) <= MAX_DIMENSION:
        return contents

    image.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.Resampling.LANCZOS)
    output = BytesIO()

    if extension in (".jpg", ".jpeg"):
        if image.mode in ("RGBA", "LA", "P"):
            rgba = image.convert("RGBA")
            background = Image.new("RGB", rgba.size, (255, 255, 255))
            background.paste(rgba, mask=rgba.split()[-1])
            image = background
        else:
            image = image.convert("RGB")
        image.save(output, "JPEG", quality=JPEG_WEBP_QUALITY, optimize=True)
    elif extension == ".webp":
        image.save(output, "WEBP", quality=JPEG_WEBP_QUALITY, method=6)
    else:
        image.save(output, "PNG", optimize=True)

    return output.getvalue()


def _validate_and_read(upload_file: UploadFile) -> bytes:
    """
    Executa todas as validações e, se tudo estiver certo, devolve os
    bytes do arquivo (para serem gravados no disco pelo chamador).
    Lança ImageValidationError com uma mensagem em português se algo
    estiver errado.
    """
    extension = _get_extension(upload_file.filename or "")
    if extension not in ALLOWED_EXTENSIONS:
        raise ImageValidationError(
            "Formato de arquivo não permitido. Envie uma imagem JPG, JPEG, PNG ou WebP."
        )

    content_type = (upload_file.content_type or "").lower()
    if content_type not in GENERIC_CONTENT_TYPES and not content_type.startswith("image/"):
        raise ImageValidationError(
            "O arquivo enviado não foi reconhecido como uma imagem válida."
        )

    upload_file.file.seek(0, 2)  # vai para o final do arquivo
    size = upload_file.file.tell()  # posição atual = tamanho em bytes
    upload_file.file.seek(0)  # volta para o início

    if size == 0:
        raise ImageValidationError("O arquivo enviado está vazio.")

    if size > MAX_FILE_SIZE_BYTES:
        raise ImageValidationError(
            f"O arquivo excede o tamanho máximo permitido ({MAX_FILE_SIZE_MB} MB)."
        )

    contents = upload_file.file.read()
    upload_file.file.seek(0)

    # Verificação real do conteúdo: tenta abrir os bytes como imagem.
    # Isso pega, por exemplo, um arquivo .txt renomeado para .jpg.
    #
    # Usamos "except Exception" de propósito aqui (e não só os dois tipos
    # mais comuns de erro): esta função existe especificamente para separar
    # "é uma imagem processável" de "não é" antes de qualquer outra parte do
    # sistema tocar no arquivo, então qualquer falha do Pillow — incluindo
    # fotos extremamente grandes, que disparam a proteção interna do Pillow
    # contra "decompression bombs" (Image.DecompressionBombError) — deve
    # virar uma mensagem clara para quem está enviando, em vez de um erro
    # interno do servidor (HTTP 500).
    try:
        image = Image.open(BytesIO(contents))
        image.verify()
    except Exception:
        raise ImageValidationError(
            "Não foi possível processar essa imagem — o arquivo pode estar corrompido "
            "ou a resolução pode ser grande demais. Tente uma foto com resolução menor."
        )

    try:
        contents = _resize_if_needed(contents, extension)
    except Exception:
        pass

    return contents


def _get_institution_dir(institution_id: int) -> Path:
    directory = INSTITUTIONS_UPLOADS_DIR / str(institution_id)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _find_image_or_404(institution: Institution, image_id: int) -> InstitutionImage:
    for image in institution.images:
        if image.id == image_id:
            return image
    raise HTTPException(status_code=404, detail="Imagem não encontrada para esta instituição.")


def save_institution_image(
    db: Session,
    institution: Institution,
    upload_file: UploadFile,
    is_main: bool = False,
) -> InstitutionImage:
    """Valida, salva no disco e cria o registro da nova imagem no banco."""
    contents = _validate_and_read(upload_file)

    directory = _get_institution_dir(institution.id)
    filename = _generate_safe_filename(upload_file.filename)
    destination = directory / filename
    destination.write_bytes(contents)

    relative_path = f"uploads/institutions/{institution.id}/{filename}"

    # A primeira imagem de uma instituição vira principal automaticamente,
    # mesmo que o usuário não tenha marcado a caixa "definir como principal".
    should_be_main = is_main or len(institution.images) == 0

    if should_be_main:
        for existing_image in institution.images:
            existing_image.is_main = False

    image = InstitutionImage(
        institution_id=institution.id,
        file_path=relative_path,
        is_main=should_be_main,
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


def set_main_image(db: Session, institution: Institution, image_id: int) -> None:
    target = _find_image_or_404(institution, image_id)
    for image in institution.images:
        image.is_main = image.id == target.id
    db.commit()


def replace_institution_image(
    db: Session, institution: Institution, image_id: int, upload_file: UploadFile
) -> InstitutionImage:
    """Substitui o arquivo de uma imagem já cadastrada, mantendo o mesmo registro."""
    image = _find_image_or_404(institution, image_id)
    contents = _validate_and_read(upload_file)

    old_path = BASE_DIR / image.file_path

    directory = _get_institution_dir(institution.id)
    filename = _generate_safe_filename(upload_file.filename)
    destination = directory / filename
    destination.write_bytes(contents)

    _safely_delete_file(old_path)

    image.file_path = f"uploads/institutions/{institution.id}/{filename}"
    db.commit()
    db.refresh(image)
    return image


def delete_institution_image(db: Session, institution: Institution, image_id: int) -> None:
    image = _find_image_or_404(institution, image_id)
    was_main = image.is_main
    file_path = BASE_DIR / image.file_path

    db.delete(image)
    db.commit()

    _safely_delete_file(file_path)

    # Se a imagem excluída era a principal, promove outra automaticamente
    # (se existir alguma restante), para que a instituição nunca fique
    # "sem imagem principal" enquanto tiver pelo menos uma foto.
    if was_main:
        remaining = (
            db.query(InstitutionImage)
            .filter(InstitutionImage.institution_id == institution.id)
            .order_by(InstitutionImage.uploaded_at)
            .first()
        )
        if remaining:
            remaining.is_main = True
            db.commit()


def _safely_delete_file(path: Path) -> None:
    """Remove um arquivo do disco sem derrubar a aplicação se algo falhar."""
    try:
        if path.exists():
            path.unlink()
    except OSError:
        pass
