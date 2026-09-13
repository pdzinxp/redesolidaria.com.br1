"""
Schema: HelpRequestIn

Valida os dados do formulário público de solicitação de ajuda antes de
salvar no banco.
"""

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class HelpRequestIn(BaseModel):
    name: str = Field(..., max_length=150)
    age: Optional[int] = None
    household_size: Optional[int] = None
    family_income: Optional[float] = None
    city: str = Field(..., max_length=100)
    neighborhood: Optional[str] = Field(None, max_length=100)
    help_type_id: int
    description: str = Field(..., max_length=2000)
    contact: str = Field(..., max_length=150)

    @field_validator("age")
    @classmethod
    def idade_valida(cls, value: Optional[int]) -> Optional[int]:
        if value is not None and not (0 < value < 130):
            raise ValueError("Informe uma idade válida.")
        return value

    @field_validator("household_size")
    @classmethod
    def moradores_valido(cls, value: Optional[int]) -> Optional[int]:
        if value is not None and value <= 0:
            raise ValueError("O número de pessoas na residência deve ser maior que zero.")
        return value

    @field_validator("family_income")
    @classmethod
    def renda_valida(cls, value: Optional[float]) -> Optional[float]:
        if value is not None and value < 0:
            raise ValueError("A renda familiar não pode ser negativa.")
        return value
