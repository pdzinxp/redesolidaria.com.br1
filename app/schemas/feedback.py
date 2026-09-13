"""
Schema: FeedbackIn

Valida a avaliação (1 a 5 estrelas) e o comentário opcional enviados pelo
formulário público de feedback.
"""

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class FeedbackIn(BaseModel):
    rating: int
    comment: Optional[str] = Field(None, max_length=1000)
    reviewer_name: Optional[str] = Field(None, max_length=100)

    @field_validator("rating")
    @classmethod
    def rating_entre_1_e_5(cls, value: int) -> int:
        if not 1 <= value <= 5:
            raise ValueError("A avaliação deve ser de 1 a 5 estrelas.")
        return value
