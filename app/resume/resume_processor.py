from app.ml.preprocessing import clean_text
from app.ml.skill_extraction import extract_skills, load_skills
from app.resume.contact_extractor import extract_email, extract_phone
from app.resume.experience_extractor import extract_experience
from app.resume.education_extractor import extract_education
from app.resume.name_extractor import extract_name
from app.ml.seniority_detector import detect_seniority
from app.resume.section_parser import parse_sections
from app.schemas.resume import (
    EducationItem,
    ExperienceItem,
    ResumeProfile,
)


def _lines(section: str) -> list[str]:
    return [
        x.strip(" -•\t")
        for x in section.splitlines()
        if x.strip()
    ]


def process_resume(
    text: str,
    skills_file: str,
) -> ResumeProfile:

    skills_df = load_skills(skills_file)

    sections = parse_sections(text)

    skills = extract_skills(
        text,
        skills_df,
    )

    experience_data = extract_experience(
        sections.get("experience", "")
    )

    experience = [
        ExperienceItem(**item)
        for item in experience_data
    ]

    education = extract_education(
        sections.get("education", "")
    )

    return ResumeProfile(
        name=extract_name(text),

        email=extract_email(text),

        phone=extract_phone(text),

        summary=sections.get(
            "summary",
            "",
        ),

        skills=skills,

        experience=experience,

        education=education,

        certifications=_lines(
            sections.get(
                "certifications",
                "",
            )
        ),

        projects=_lines(
            sections.get(
                "projects",
                "",
            )
        ),

        seniority=detect_seniority(
            sections.get("experience", "")
        ),

        raw_text=clean_text(text),
    )
