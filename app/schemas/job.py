from pydantic import BaseModel, Field


class JobProfile(BaseModel):

    title: str = ""

    required_skills: list[str] = Field(
        default_factory=list
    )

    preferred_skills: list[str] = Field(
        default_factory=list
    )

    experience_years: float = 0.0

    education: list[str] = Field(
        default_factory=list
    )

    raw_text: str = ""
