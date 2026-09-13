"""
Serviço de feedback (avaliações e comentários dos visitantes).
"""

from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Feedback
from app.schemas.feedback import FeedbackIn


def create_feedback(db: Session, data: FeedbackIn) -> Feedback:
    feedback = Feedback(
        rating=data.rating,
        comment=data.comment,
        reviewer_name=data.reviewer_name,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


def list_feedbacks(db: Session, limit: Optional[int] = None) -> List[Feedback]:
    query = db.query(Feedback).order_by(Feedback.created_at.desc())
    if limit:
        query = query.limit(limit)
    return query.all()


def count_feedbacks(db: Session) -> int:
    return db.query(Feedback).count()


def get_average_rating(db: Session) -> float:
    feedbacks = db.query(Feedback).all()
    if not feedbacks:
        return 0.0
    return round(sum(f.rating for f in feedbacks) / len(feedbacks), 1)


def get_feedback_or_404(db: Session, feedback_id: int) -> Feedback:
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if feedback is None:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada.")
    return feedback


def delete_feedback(db: Session, feedback: Feedback) -> None:
    db.delete(feedback)
    db.commit()
