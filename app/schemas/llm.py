from pydantic import BaseModel, Field


class LLMResumeAnalysis(BaseModel):

    candidate_name: str | None = None

    professional_summary: str = ""

    skills: list[str] = Field(
        default_factory=list
    )

    experience_years: float = 0.0

    seniority: str | None = None

    relevant_experience: list[str] = Field(
        default_factory=list
    )

    education: list[str] = Field(
        default_factory=list
    )

    certifications: list[str] = Field(
        default_factory=list
    )

    projects: list[str] = Field(
        default_factory=list
    )


class LLMJobAnalysis(BaseModel):

    job_title: str = ""

    required_skills: list[str] = Field(
        default_factory=list
    )

    preferred_skills: list[str] = Field(
        default_factory=list
    )

    experience_years: float = 0.0

    seniority: str | None = None

    education: list[str] = Field(
        default_factory=list
    )

    responsibilities: list[str] = Field(
        default_factory=list
    )
