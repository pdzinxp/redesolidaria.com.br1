"""
Schema: InstitutionIn

Usado para validar os dados de uma instituição antes de salvar no banco,
tanto na criação quanto na edição. As checagens mais simples (campos
obrigatórios não vazios) são feitas diretamente no router, em português;
aqui ficam as validações que dependem de regras específicas do dado
(latitude/longitude dentro do intervalo válido, estado com 2 letras).
"""

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class InstitutionIn(BaseModel):
    name: str = Field(..., max_length=150)
    description: Optional[str] = None
    address: str = Field(..., max_length=255)
    city: str = Field(..., max_length=100)
    state: str = Field(..., max_length=2)
    zip_code: Optional[str] = Field(None, max_length=9)
    latitude: float
    longitude: float
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=150)
    opening_hours: Optional[str] = Field(None, max_length=255)
    is_active: bool = True

    @field_validator("state")
    @classmethod
    def state_deve_ter_duas_letras(cls, value: str) -> str:
        value = value.strip().upper()
        if len(value) != 2:
            raise ValueError("O estado deve ser a sigla com 2 letras, ex: SP.")
        return value

    @field_validator("latitude")
    @classmethod
    def latitude_no_intervalo_valido(cls, value: float) -> float:
        if not -90 <= value <= 90:
            raise ValueError("Latitude deve estar entre -90 e 90.")
        return value

    @field_validator("longitude")
    @classmethod
    def longitude_no_intervalo_valido(cls, value: float) -> float:
        if not -180 <= value <= 180:
            raise ValueError("Longitude deve estar entre -180 e 180.")
        return value

    @field_validator("email")
    @classmethod
    def email_deve_conter_arroba(cls, value: Optional[str]) -> Optional[str]:
        if value and "@" not in value:
            raise ValueError("Informe um e-mail válido.")
        return value
