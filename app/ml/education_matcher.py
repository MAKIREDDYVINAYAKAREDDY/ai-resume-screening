import re


DEGREE_ALIASES = {
    "bachelor": [
        "bachelor",
        "bachelors",
        "bachelor's",
        "b.tech",
        "btech",
        "b.e",
        "be",
        "b.sc",
        "bsc",
        "bca",
        "b.com",
        "b.a",
    ],
    "master": [
        "master",
        "masters",
        "master's",
        "m.tech",
        "mtech",
        "m.e",
        "me",
        "m.sc",
        "msc",
        "mca",
        "m.com",
        "m.a",
        "mba",
    ],
    "phd": [
        "phd",
        "ph.d",
        "doctorate",
    ],
}


def normalize_education_text(text: str) -> str:
    text = text.lower()
    text = text.replace("’", "'")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def degree_level(text: str) -> str | None:
    text = normalize_education_text(text)

    for level, aliases in DEGREE_ALIASES.items():
        for alias in aliases:
            if alias in text:
                return level

    return None


def education_requirement_matches(
    requirement: str,
    resume_text: str,
) -> bool:

    requirement = normalize_education_text(
        requirement
    )

    resume_text = normalize_education_text(
        resume_text
    )

    required_level = degree_level(
        requirement
    )

    resume_level = degree_level(
        resume_text
    )

    if (
        required_level
        and resume_level
        and required_level == resume_level
    ):
        requirement_words = {
            word
            for word in re.findall(
                r"[a-z]+",
                requirement,
            )
            if word not in {
                "degree",
                "bachelor",
                "bachelors",
                "master",
                "masters",
                "phd",
                "doctorate",
            }
        }

        resume_words = set(
            re.findall(
                r"[a-z]+",
                resume_text,
            )
        )

        if not requirement_words:
            return True

        if requirement_words.issubset(
            resume_words
        ):
            return True

    return requirement in resume_text


def calculate_education_score(
    requirements: list[str],
    resume_education: list,
) -> float:

    if not requirements:
        return 100.0

    if not resume_education:
        return 0.0

    resume_parts = []

    for education in resume_education:
        resume_parts.extend(
            [
                education.degree or "",
                education.institution or "",
                education.field_of_study or "",
            ]
        )

    resume_text = " ".join(
        resume_parts
    )

    matched = 0

    for requirement in requirements:
        if education_requirement_matches(
            requirement,
            resume_text,
        ):
            matched += 1

    return round(
        matched / len(requirements) * 100,
        2,
    )
