import re

import pandas as pd

from app.ml.preprocessing import clean_text


def load_skills(file_path: str) -> pd.DataFrame:

    return pd.read_csv(file_path)


def _skill_pattern(skill: str) -> str:

    normalized = clean_text(skill)

    return (
        rf"(?<!\w)"
        rf"{re.escape(normalized)}"
        rf"(?!\w)"
    )


def extract_skills(
    text: str,
    skills_df: pd.DataFrame,
) -> list[str]:

    cleaned_text = clean_text(text)

    found_skills: list[str] = []

    for skill in skills_df["skill"].dropna():

        skill = str(skill)

        pattern = _skill_pattern(skill)

        if re.search(
            pattern,
            cleaned_text,
            flags=re.IGNORECASE,
        ):
            found_skills.append(skill)

    return found_skills
