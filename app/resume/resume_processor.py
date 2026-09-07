from app.ml.preprocessing import clean_text

from app.ml.skill_extraction import (
    extract_skills,
    load_skills,
)

from app.resume.contact_extractor import (
    extract_email,
    extract_phone,
)

from app.resume.name_extractor import (
    extract_name,
)

from app.resume.section_parser import (
    parse_sections,
)

from app.schemas.resume import (
    EducationItem,
    ExperienceItem,
    ResumeProfile,
)


def _lines(
    section: str,
) -> list[str]:

    return [
        line.strip(" -•\t")
        for line in section.splitlines()
        if line.strip()
    ]


def process_resume(
    text: str,
    skills_file: str,
) -> ResumeProfile:

    skills_df = load_skills(
        skills_file
    )

    sections = parse_sections(
        text
    )

    skills = extract_skills(
        text,
        skills_df
    )

    experience_lines = _lines(
        sections.get(
            "experience",
            "",
        )
    )

    education_lines = _lines(
        sections.get(
            "education",
            "",
        )
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

        experience=(
            [
                ExperienceItem(
                    description="\n".join(
                        experience_lines
                    )
                )
            ]
            if experience_lines
            else []
        ),

        education=[
            EducationItem(
                degree=line
            )
            for line in education_lines
        ],

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

        raw_text=clean_text(
            text
        ),
    )
