from pydantic import BaseModel, Field


class ExperienceItem(BaseModel):

    job_title: str | None = None

    company: str | None = None

    duration: str | None = None

    description: str = ""


class EducationItem(BaseModel):

    degree: str | None = None

    institution: str | None = None

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

    raw_text: str = ""
