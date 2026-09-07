import re


SECTION_ALIASES = {

    "summary": {
        "summary",
        "professional summary",
        "profile",
        "objective",
        "career objective",
    },

    "skills": {
        "skills",
        "technical skills",
        "core skills",
        "technical competencies",
        "technologies",
    },

    "experience": {
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "work history",
    },

    "education": {
        "education",
        "academic background",
        "academic qualifications",
    },

    "projects": {
        "projects",
        "personal projects",
        "academic projects",
        "key projects",
    },

    "certifications": {
        "certifications",
        "certificates",
        "professional certifications",
    },
}


def normalize_heading(
    text: str,
) -> str:

    text = text.strip().lower()

    text = re.sub(
        r"[^a-zA-Z ]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def detect_section(
    line: str,
) -> str | None:

    normalized = normalize_heading(
        line
    )

    for section, aliases in SECTION_ALIASES.items():

        if normalized in aliases:
            return section

    return None


def parse_sections(
    text: str,
) -> dict[str, str]:

    sections: dict[str, list[str]] = {
        "header": []
    }

    current_section = "header"

    for raw_line in text.splitlines():

        line = raw_line.strip()

        if not line:
            continue

        section = detect_section(
            line
        )

        if section:

            current_section = section

            sections.setdefault(
                current_section,
                [],
            )

            continue

        sections.setdefault(
            current_section,
            [],
        ).append(line)

    return {
        section: "\n".join(lines).strip()
        for section, lines in sections.items()
    }
