import re
from datetime import date
from dateutil.relativedelta import relativedelta


DATE_PATTERN = re.compile(
    r"""
    (?P<start>
        (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)
        [a-z]*\s+\d{4}
        |
        \d{1,2}/\d{4}
        |
        \d{4}
    )
    \s*(?:-|–|—|to)\s*
    (?P<end>
        (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)
        [a-z]*\s+\d{4}
        |
        \d{1,2}/\d{4}
        |
        \d{4}
        |
        Present
        |
        Current
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)


def parse_date(value: str) -> date | None:
    value = value.strip()

    if value.lower() in {"present", "current"}:
        return date.today()

    formats = [
        "%b %Y",
        "%B %Y",
        "%m/%Y",
        "%Y",
    ]

    for fmt in formats:
        try:
            return __import__("datetime").datetime.strptime(value, fmt).date()
        except ValueError:
            continue

    return None


def calculate_duration(start: str, end: str) -> float:
    start_date = parse_date(start)
    end_date = parse_date(end)

    if not start_date or not end_date:
        return 0.0

    if end_date < start_date:
        return 0.0

    delta = relativedelta(end_date, start_date)

    return round(
        delta.years + delta.months / 12,
        1,
    )


def extract_experience(section_text: str) -> list[dict]:
    lines = [
        line.strip(" -•\t")
        for line in section_text.splitlines()
        if line.strip()
    ]

    experiences = []
    current = None

    for line in lines:
        match = DATE_PATTERN.search(line)

        if match:
            if current:
                experiences.append(current)

            start = match.group("start")
            end = match.group("end")

            before_date = line[:match.start()].strip(" -|")
            after_date = line[match.end():].strip(" -|")

            title = before_date
            company = after_date

            if "|" in before_date:
                parts = [
                    p.strip()
                    for p in before_date.split("|")
                    if p.strip()
                ]

                if len(parts) >= 2:
                    title = parts[0]
                    company = parts[1]

            current = {
                "job_title": title or None,
                "company": company or None,
                "start_date": start,
                "end_date": end,
                "duration_years": calculate_duration(
                    start,
                    end,
                ),
                "description": "",
            }

        elif current:
            if current["description"]:
                current["description"] += " "
            current["description"] += line

    if current:
        experiences.append(current)

    return experiences


def total_experience_years(
    experiences: list[dict],
) -> float:
    return round(
        sum(
            experience.get("duration_years", 0.0)
            for experience in experiences
        ),
        1,
    )
