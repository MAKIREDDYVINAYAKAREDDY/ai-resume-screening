import re


SENIORITY_LEVELS = {
    "intern": 0,
    "entry": 1,
    "junior": 1,
    "associate": 2,
    "mid": 2,
    "mid-level": 2,
    "senior": 3,
    "lead": 4,
    "staff": 4,
    "principal": 5,
    "manager": 5,
    "director": 6,
}


def detect_seniority(text: str) -> str | None:
    """
    Detect the highest-confidence seniority level
    mentioned in a job title or resume text.
    """

    if not text:
        return None

    text = text.lower()

    matches = []

    for level, rank in SENIORITY_LEVELS.items():

        pattern = rf"(?<!\w){re.escape(level)}(?!\w)"

        if re.search(pattern, text):
            matches.append(
                (rank, level)
            )

    if not matches:
        return None

    matches.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return matches[0][1]


def seniority_rank(
    seniority: str | None,
) -> int:
    if not seniority:
        return 0

    return SENIORITY_LEVELS.get(
        seniority.lower(),
        0,
    )


def calculate_seniority_score(
    candidate_seniority: str | None,
    required_seniority: str | None,
) -> float:

    if not required_seniority:
        return 100.0

    if not candidate_seniority:
        return 50.0

    candidate_rank = seniority_rank(
        candidate_seniority
    )

    required_rank = seniority_rank(
        required_seniority
    )

    if candidate_rank >= required_rank:
        return 100.0

    difference = required_rank - candidate_rank

    if difference == 1:
        return 70.0

    if difference == 2:
        return 40.0

    return 20.0
