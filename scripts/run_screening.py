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


BASE_DIR = Path(
    __file__
).resolve().parents[1]

SKILLS_FILE = (
    BASE_DIR
    / "data/skills/skills.csv"
)

JOB_FILE = (
    BASE_DIR
    / "data/raw/jobs/ml_engineer.txt"
)

RESUME_DIR = (
    BASE_DIR
    / "data/raw/resumes"
)


def main():

    skills_df = pd.read_csv(
        SKILLS_FILE
    )

    job_text = JOB_FILE.read_text(
        encoding="utf-8"
    )

    job = parse_job_description(
        job_text,
        skills_df,
    )

    results = []

    for resume_file in sorted(
        RESUME_DIR.iterdir()
    ):

        if resume_file.suffix.lower() not in {
            ".txt",
            ".pdf",
            ".docx",
        }:
            continue

        resume_text = extract_resume_text(
            str(resume_file)
        )

        profile = process_resume(
            resume_text,
            str(SKILLS_FILE),
        )

        score = calculate_match(
            profile,
            job,
        )

        results.append(
            (
                profile.name
                or "Unknown",
                resume_file.name,
                score,
            )
        )

    results.sort(
        key=lambda item: item[2]["final_score"],
        reverse=True,
    )

    print()
    print("=" * 60)
    print("AI RESUME SCREENING")
    print("=" * 60)

    for rank, (
        name,
        filename,
        score,
    ) in enumerate(
        results,
        start=1,
    ):

        print()
        print(
            f"{rank}. {name}"
        )

        print(
            f"   File: {filename}"
        )

        print(
            f"   Final Score: "
            f"{score['final_score']:.2f}%"
        )

        print(
            f"   Skill Score: "
            f"{score['skill_score']:.2f}%"
        )

        print(
            f"   Semantic Score: "
            f"{score['semantic_score']:.2f}%"
        )

        print(
            "   Matched: "
            + (
                ", ".join(
                    score["matched_skills"]
                )
                or "None"
            )
        )

        print(
            "   Missing: "
            + (
                ", ".join(
                    score["missing_skills"]
                )
                or "None"
            )
        )


if __name__ == "__main__":
    main()
