import re

from app.schemas.resume import EducationItem


DEGREE_PATTERNS = [
    r"\bB\.?Tech\b",
    r"\bM\.?Tech\b",
    r"\bB\.?E\b",
    r"\bM\.?E\b",
    r"\bB\.?Sc\b",
    r"\bM\.?Sc\b",
    r"\bB\.?A\b",
    r"\bM\.?A\b",
    r"\bB\.?Com\b",
    r"\bM\.?Com\b",
    r"\bMBA\b",
    r"\bMCA\b",
    r"\bBCA\b",
    r"\bPh\.?D\b",
    r"\bBachelor(?:'s)?\b",
    r"\bMaster(?:'s)?\b",
    r"\bDoctorate\b",
]


def detect_degree(text: str) -> str | None:
    for pattern in DEGREE_PATTERNS:
        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:
            return match.group(0)

    return None


def extract_education(
    section_text: str,
) -> list[EducationItem]:

    items = []

    for raw_line in section_text.splitlines():

        line = raw_line.strip(" -•\t")

        if not line:
            continue

        parts = [
            part.strip()
            for part in line.split("|")
            if part.strip()
        ]

        degree = detect_degree(line)

        institution = None
        field_of_study = None
        duration = None

        if len(parts) >= 2:
            institution = parts[1]

        if len(parts) >= 3:
            duration = parts[2]

        field_match = re.search(
            r"(?:in|of)\s+([A-Za-z][A-Za-z &/-]+)",
            line,
            flags=re.IGNORECASE,
        )

        if field_match:
            field_of_study = field_match.group(1).strip()

        items.append(
            EducationItem(
                degree=degree or (
                    parts[0]
                    if parts
                    else None
                ),
                institution=institution,
                field_of_study=field_of_study,
                duration=duration,
            )
        )

    return items
