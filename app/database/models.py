from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.database import Base


# ================================================================
# USER
# ================================================================

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(50),
        default="recruiter",
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    screening_runs: Mapped[
        list["ScreeningRun"]
    ] = relationship(
        back_populates="user",
    )


# ================================================================
# SCREENING RUN
# ================================================================

class ScreeningRun(Base):
    __tablename__ = "screening_runs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    job_title: Mapped[str] = mapped_column(
        String(255),
        default="Untitled Job",
    )

    job_description: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    candidate_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    user: Mapped[
        "User | None"
    ] = relationship(
        back_populates="screening_runs",
    )

    results: Mapped[
        list["ScreeningResult"]
    ] = relationship(
        back_populates="screening_run",
        cascade="all, delete-orphan",
    )


# ================================================================
# SCREENING RESULT
# ================================================================

class ScreeningResult(Base):
    __tablename__ = "screening_results"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    screening_run_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "screening_runs.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    candidate_name: Mapped[str] = mapped_column(
        String(255),
        default="Unknown",
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        default="",
    )

    score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    skill_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    preferred_skill_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    experience_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    education_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    seniority_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    semantic_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    matched_skills: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    missing_skills: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    resume_skills: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    job_required_skills: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    job_preferred_skills: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    candidate_seniority: Mapped[
        str | None
    ] = mapped_column(
        String(100),
        nullable=True,
    )

    required_seniority: Mapped[
        str | None
    ] = mapped_column(
        String(100),
        nullable=True,
    )

    explanation_summary: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    explanation_strengths: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    explanation_concerns: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    screening_run: Mapped[
        "ScreeningRun | None"
    ] = relationship(
        back_populates="results",
    )
