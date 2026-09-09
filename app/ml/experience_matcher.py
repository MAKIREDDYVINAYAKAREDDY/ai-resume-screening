from datetime import date
from app.resume.experience_extractor import parse_date


def calculate_unique_experience_years(
    experiences: list,
) -> float:
    periods = []

    for experience in experiences:
        start = parse_date(
            experience.start_date or ""
        )
        end = parse_date(
            experience.end_date or ""
        )

        if not start or not end:
            continue

        if end < start:
            continue

        periods.append((start, end))

    if not periods:
        return 0.0

    periods.sort(key=lambda x: x[0])

    merged = []

    current_start, current_end = periods[0]

    for start, end in periods[1:]:

        if start <= current_end:
            if end > current_end:
                current_end = end
        else:
            merged.append(
                (current_start, current_end)
            )
            current_start = start
            current_end = end

    merged.append(
        (current_start, current_end)
    )

    total_days = sum(
        (end - start).days
        for start, end in merged
    )

    return round(
        total_days / 365.25,
        1,
    )


def calculate_experience_score(
    experiences: list,
    required_years: float,
) -> float:

    if required_years <= 0:
        return 100.0

    candidate_years = (
        calculate_unique_experience_years(
            experiences
        )
    )

    score = (
        candidate_years
        / required_years
        * 100
    )

    return round(
        min(score, 100.0),
        2,
    )
