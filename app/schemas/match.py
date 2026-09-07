from pydantic import BaseModel, Field


class MatchResult(BaseModel):

    filename: str

    candidate_name: str

    final_score: float

    skill_score: float

    semantic_score: float

    matched_skills: list[str] = Field(
        default_factory=list
    )

    missing_skills: list[str] = Field(
        default_factory=list
    )

    resume_skills: list[str] = Field(
        default_factory=list
    )

    job_required_skills: list[str] = Field(
        default_factory=list
    )
