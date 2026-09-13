"""
Schema: InstitutionSuggestionIn

Valida os dados do formulário público de sugestão de instituição.
"""

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class InstitutionSuggestionIn(BaseModel):
    name: str = Field(..., max_length=150)
    description: Optional[str] = None
    address: str = Field(..., max_length=255)
    city: str = Field(..., max_length=100)
    state: str = Field(..., max_length=2)
    zip_code: Optional[str] = Field(None, max_length=9)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=150)
    suggested_by_name: str = Field(..., max_length=150)
    suggested_by_contact: str = Field(..., max_length=150)

    @field_validator("state")
    @classmethod
    def state_deve_ter_duas_letras(cls, value: str) -> str:
        value = value.strip().upper()
        if len(value) != 2:
            raise ValueError("O estado deve ser a sigla com 2 letras, ex: SP.")
        return value

    @field_validator("email")
    @classmethod
    def email_deve_conter_arroba(cls, value: Optional[str]) -> Optional[str]:
        if value and "@" not in value:
            raise ValueError("Informe um e-mail válido.")
        return value
