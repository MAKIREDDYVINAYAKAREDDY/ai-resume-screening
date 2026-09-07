from pathlib import Path

import pandas as pd

from app.jobs.job_parser import (
    parse_job_description,
)

from app.ml.scoring import (
    calculate_match,
)

from app.resume.resume_parser import (
    extract_resume_text,
)

from app.resume.resume_processor import (
    process_resume,
)

from app.resume.section_parser import (
    parse_sections,
)


BASE_DIR = Path(
    __file__
).resolve().parents[1]

SKILLS_FILE = (
    BASE_DIR
    / "data/skills/skills.csv"
)


def test_section_parser():

    text = """
    JOHN DOE

    SKILLS

    Python
    SQL

    EXPERIENCE

    ML Engineer

    EDUCATION

    B.Tech
    """

    sections = parse_sections(
        text
    )

    assert "skills" in sections

    assert "Python" in (
        sections["skills"]
    )


def test_resume_processing():

    resume_file = (
        BASE_DIR
        / "data/raw/resumes/"
        / "candidate_001.txt"
    )

    text = extract_resume_text(
        str(resume_file)
    )

    profile = process_resume(
        text,
        str(SKILLS_FILE),
    )

    assert profile.name == "JOHN DOE"

    assert (
        "Python"
        in profile.skills
    )

    assert (
        profile.email
        == "john.doe@example.com"
    )


def test_job_and_matching():

    skills_df = pd.read_csv(
        SKILLS_FILE
    )

    job_file = (
        BASE_DIR
        / "data/raw/jobs/"
        / "ml_engineer.txt"
    )

    job = parse_job_description(
        job_file.read_text(),
        skills_df,
    )

    resume_file = (
        BASE_DIR
        / "data/raw/resumes/"
        / "candidate_001.txt"
    )

    profile = process_resume(
        resume_file.read_text(),
        str(SKILLS_FILE),
    )

    result = calculate_match(
        profile,
        job,
    )

    assert (
        result["skill_score"]
        == 100.0
    )

    assert (
        result["final_score"]
        > 0
    )
