from app.ml.seniority_detector import (
    calculate_seniority_score,
)


def calculate_preferred_skill_score(
    resume_skills: list[str],
    preferred_skills: list[str],
) -> float:

    if not preferred_skills:
        return 100.0

    resume_skill_set = {
        skill.lower()
        for skill in resume_skills
    }

    matched = sum(
        1
        for skill in preferred_skills
        if skill.lower() in resume_skill_set
    )

    return round(
        matched
        / len(preferred_skills)
        * 100,
        2,
    )


def calculate_seniority_match_score(
    candidate_seniority: str | None,
    required_seniority: str | None,
) -> float:

    return calculate_seniority_score(
        candidate_seniority,
        required_seniority,
    )
