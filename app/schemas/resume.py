from pydantic import BaseModel, Field


class ExperienceItem(BaseModel):
    job_title: str | None = None
    company: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    duration_years: float = 0.0
    description: str = ""


class EducationItem(BaseModel):
    degree: str | None = None
    institution: str | None = None
    field_of_study: str | None = None
    duration: str | None = None


class ResumeProfile(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None

    summary: str = ""

    skills: list[str] = Field(
        default_factory=list
    )

    experience: list[ExperienceItem] = Field(
        default_factory=list
    )

    education: list[EducationItem] = Field(
        default_factory=list
    )

    certifications: list[str] = Field(
        default_factory=list
    )

    projects: list[str] = Field(
        default_factory=list
    )

    seniority: str | None = None

    raw_text: str = ""
