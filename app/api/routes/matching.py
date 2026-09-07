import json
from pathlib import Path

import pandas as pd

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from sqlalchemy.orm import Session

from app.database.database import (
    get_db,
)

from app.database.models import (
    ScreeningResult,
)

from app.jobs.job_parser import (
    parse_job_description,
)

from app.ml.scoring import (
    calculate_match,
)

from app.resume.resume_parser import (
    extract_resume_text_from_bytes,
)

from app.resume.resume_processor import (
    process_resume,
)

from app.schemas.match import (
    MatchResult,
)


router = APIRouter(
    tags=["screening"]
)


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parents[3]
)


SKILLS_FILE = (
    BASE_DIR
    / "data/skills/skills.csv"
)


@router.post(
    "/screen",
    response_model=list[MatchResult],
)
async def screen_resumes(

    job_description: str = Form(...),

    resumes: list[
        UploadFile
    ] = File(...),

    db: Session = Depends(
        get_db
    ),
):

    if not job_description.strip():

        raise HTTPException(
            status_code=400,
            detail=(
                "Job description "
                "is empty."
            ),
        )

    if not resumes:

        raise HTTPException(
            status_code=400,
            detail=(
                "At least one "
                "resume is required."
            ),
        )

    skills_df = pd.read_csv(
        SKILLS_FILE
    )

    job = parse_job_description(
        job_description,
        skills_df,
    )

    if not job.required_skills:

        raise HTTPException(
            status_code=400,
            detail=(
                "No recognized required "
                "skills found."
            ),
        )

    results = []

    for upload in resumes:

        filename = (
            upload.filename
            or "resume.txt"
        )

        data = await upload.read()

        try:

            text = (
                extract_resume_text_from_bytes(
                    filename,
                    data,
                )
            )

            profile = process_resume(
                text,
                str(SKILLS_FILE),
            )

        except Exception as exc:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Could not parse "
                    f"{filename}: {exc}"
                ),
            ) from exc

        score = calculate_match(
            profile,
            job,
        )

        result = MatchResult(
            filename=filename,
            candidate_name=(
                profile.name
                or "Unknown"
            ),
            **score,
        )

        results.append(
            result
        )

        db.add(
            ScreeningResult(
                candidate_name=(
                    result.candidate_name
                ),
                filename=(
                    result.filename
                ),
                score=(
                    result.final_score
                ),
                matched_skills=json.dumps(
                    result.matched_skills
                ),
                missing_skills=json.dumps(
                    result.missing_skills
                ),
                semantic_score=(
                    result.semantic_score
                ),
                skill_score=(
                    result.skill_score
                ),
            )
        )

    db.commit()

    results.sort(
        key=lambda result: (
            result.final_score
        ),
        reverse=True,
    )

    return results


@router.get(
    "/results"
)
def get_results(
    db: Session = Depends(
        get_db
    ),
):

    rows = (
        db.query(
            ScreeningResult
        )
        .order_by(
            ScreeningResult.score.desc()
        )
        .all()
    )

    return [

        {
            "id": row.id,

            "candidate_name":
                row.candidate_name,

            "filename":
                row.filename,

            "score":
                row.score,

            "matched_skills":
                json.loads(
                    row.matched_skills
                ),

            "missing_skills":
                json.loads(
                    row.missing_skills
                ),

            "semantic_score":
                row.semantic_score,

            "skill_score":
                row.skill_score,

            "created_at":
                row.created_at.isoformat(),
        }

        for row in rows
    ]
