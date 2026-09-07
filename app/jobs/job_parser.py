import re
from pathlib import Path

import pandas as pd

from app.ml.preprocessing import clean_text
from app.ml.skill_extraction import extract_skills
from app.schemas.job import JobProfile


def _section(
    text: str,
    start: str,
    ends: tuple[str, ...],
) -> str:

    if ends:

        end_pattern = "|".join(
            re.escape(end)
            for end in ends
        )

        lookahead = (
            rf"(?=(?:{end_pattern})"
            rf"\s*:|$)"
        )

    else:

        lookahead = r"(?=$)"

    pattern = (
        rf"{re.escape(start)}"
        rf"\s*:\s*(.*?)"
        rf"{lookahead}"
    )

    match = re.search(
        pattern,
        text,
        flags=re.IGNORECASE
        | re.DOTALL,
    )

    if match:
        return match.group(1).strip()

    return ""


def parse_job_description(
    text: str,
    skills_df: pd.DataFrame,
) -> JobProfile:

    title_match = re.search(
        r"(?:JOB TITLE|TITLE)"
        r"\s*:\s*(.+)",
        text,
        flags=re.IGNORECASE,
    )

    title = (
        title_match.group(1).strip()
        if title_match
        else ""
    )

    required_text = _section(
        text,
        "REQUIRED SKILLS",
        (
            "PREFERRED SKILLS",
            "EXPERIENCE",
            "EDUCATION",
        ),
    )

    preferred_text = _section(
        text,
        "PREFERRED SKILLS",
        (
            "EXPERIENCE",
            "EDUCATION",
        ),
    )

    experience_text = _section(
        text,
        "EXPERIENCE",
        ("EDUCATION",),
    )

    education_text = _section(
        text,
        "EDUCATION",
        (),
    )

    years_match = re.search(
        r"(\d+(?:\.\d+)?)"
        r"\s*\+?\s*years?",
        experience_text,
        flags=re.IGNORECASE,
    )

    experience_years = (
        float(years_match.group(1))
        if years_match
        else 0.0
    )

    return JobProfile(

        title=title,

        required_skills=extract_skills(
            required_text,
            skills_df,
        ),

        preferred_skills=extract_skills(
            preferred_text,
            skills_df,
        ),

        experience_years=experience_years,

        education=[
            line.strip(" -•")
            for line in education_text.splitlines()
            if line.strip()
        ],

        raw_text=clean_text(text),
    )


def load_job_file(
    file_path: str,
    skills_file: str,
) -> JobProfile:

    text = Path(
        file_path
    ).read_text(
        encoding="utf-8"
    )

    skills_df = pd.read_csv(
        skills_file
    )

    return parse_job_description(
        text,
        skills_df,
    )
