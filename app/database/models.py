from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class ScreeningResult(Base):

    __tablename__ = "screening_results"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    candidate_name: Mapped[str] = mapped_column(
        String(255),
        default="Unknown",
    )

    filename: Mapped[str] = mapped_column(
        String(255),
    )

    score: Mapped[float] = mapped_column(
        Float,
    )

    matched_skills: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    missing_skills: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    semantic_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    skill_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
