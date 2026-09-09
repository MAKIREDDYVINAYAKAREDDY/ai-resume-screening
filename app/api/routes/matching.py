import json
from pathlib import Path

import pandas as pd

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)

from slowapi import Limiter
from slowapi.util import get_remote_address

from sqlalchemy.orm import Session

from app.auth.dependencies import (
    get_current_user,
    require_role,
)

from app.database.database import get_db

from app.database.models import (
    ScreeningResult,
    ScreeningRun,
    User,
)

from app.core.security import (
    sanitize_filename,
    validate_job_description,
    validate_resume_content,
    validate_resume_count,
    validate_resume_extension,
    validate_resume_size,
)

from app.llm.hybrid_analyzer import (
    analyze_job_with_llm,
    analyze_resume_with_llm,
)

from app.llm.match_explainer import (
    generate_llm_explanation,
)

from app.ml.explainer import (
    generate_explanation,
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


# ================================================================
# ROUTER
# ================================================================

router = APIRouter(
    tags=["screening"]
)


# ================================================================
# RATE LIMITER
# ================================================================

limiter = Limiter(
    key_func=get_remote_address
)


# ================================================================
# PATHS
# ================================================================

BASE_DIR = Path(
    __file__
).resolve().parents[3]

SKILLS_FILE = (
    BASE_DIR
    / "data/skills/skills.csv"
)


# ================================================================
# SCREEN RESUMES
# ================================================================

@router.post(
    "/screen",
    response_model=list[MatchResult],
)
@limiter.limit("10/minute")
async def screen_resumes(
    request: Request,
    job_description: str = Form(...),
    resumes: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("recruiter", "admin")
    ),
):
    # ------------------------------------------------------------
    # 1. Validate request
    # ------------------------------------------------------------

    try:
        validate_job_description(
            job_description
        )

        validate_resume_count(
            len(resumes)
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    # ------------------------------------------------------------
    # 2. Validate skills database
    # ------------------------------------------------------------

    try:
        pd.read_csv(
            SKILLS_FILE
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Could not load skills "
                f"database: {exc}"
            ),
        ) from exc

    # ------------------------------------------------------------
    # 3. Analyze job description
    # ------------------------------------------------------------

    try:
        llm_job = (
            analyze_job_with_llm(
                job_description
            )
        )

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Job LLM analysis failed: "
                f"{exc}"
            ),
        ) from exc

    # ------------------------------------------------------------
    # 4. Create screening run
    # ------------------------------------------------------------

    screening_run = ScreeningRun(
        user_id=current_user.id,

        job_title=(
            llm_job.title
            or "Untitled Job"
        ),

        job_description=(
            job_description
        ),

        candidate_count=(
            len(resumes)
        ),
    )

    db.add(
        screening_run
    )

    db.flush()

    results = []

    try:

        # ========================================================
        # PROCESS EACH RESUME
        # ========================================================

        for upload in resumes:

            # ----------------------------------------------------
            # 5. Original filename
            # ----------------------------------------------------

            original_filename = (
                upload.filename
                or ""
            )

            # ----------------------------------------------------
            # 6. Validate extension
            # ----------------------------------------------------

            try:
                validate_resume_extension(
                    original_filename
                )

            except ValueError as exc:
                raise HTTPException(
                    status_code=400,
                    detail=str(exc),
                ) from exc

            # ----------------------------------------------------
            # 7. Read uploaded bytes
            # ----------------------------------------------------

            data = await upload.read()

            # ----------------------------------------------------
            # 8. Validate size and content
            # ----------------------------------------------------

            try:
                validate_resume_size(
                    len(data)
                )

                validate_resume_content(
                    filename=(
                        original_filename
                    ),
                    data=data,
                )

            except ValueError as exc:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"{original_filename}: "
                        f"{exc}"
                    ),
                ) from exc

            # ----------------------------------------------------
            # 9. Sanitize filename
            # ----------------------------------------------------

            filename = (
                sanitize_filename(
                    original_filename
                )
            )

            # ----------------------------------------------------
            # 10. Extract resume text
            # ----------------------------------------------------

            try:
                text = (
                    extract_resume_text_from_bytes(
                        filename,
                        data,
                    )
                )

            except Exception as exc:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Could not extract text "
                        f"from {filename}: "
                        f"{exc}"
                    ),
                ) from exc

            if not text.strip():
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "No readable text was "
                        f"found in {filename}."
                    ),
                )

            # ----------------------------------------------------
            # 11. Deterministic processing
            # ----------------------------------------------------

            try:
                deterministic_profile = (
                    process_resume(
                        text,
                        str(
                            SKILLS_FILE
                        ),
                    )
                )

            except Exception as exc:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Could not process "
                        f"{filename}: "
                        f"{exc}"
                    ),
                ) from exc

            # ----------------------------------------------------
            # 12. LLM resume analysis
            # ----------------------------------------------------

            try:
                llm_profile = (
                    analyze_resume_with_llm(
                        text
                    )
                )

            except Exception as exc:
                raise HTTPException(
                    status_code=503,
                    detail=(
                        "Resume LLM analysis "
                        f"failed for "
                        f"{filename}: "
                        f"{exc}"
                    ),
                ) from exc

            # ----------------------------------------------------
            # 13. Combine skills
            # ----------------------------------------------------

            combined_skills = list(
                dict.fromkeys(
                    deterministic_profile.skills
                    + llm_profile.skills
                )
            )

            deterministic_profile.skills = (
                combined_skills
            )

            # ----------------------------------------------------
            # 14. Fill missing fields
            # ----------------------------------------------------

            if not deterministic_profile.name:
                deterministic_profile.name = (
                    llm_profile.name
                )

            if not deterministic_profile.summary:
                deterministic_profile.summary = (
                    llm_profile.summary
                )

            if not deterministic_profile.seniority:
                deterministic_profile.seniority = (
                    llm_profile.seniority
                )

            # ----------------------------------------------------
            # 15. Calculate match
            # ----------------------------------------------------

            score = calculate_match(
                deterministic_profile,
                llm_job,
            )

            # ----------------------------------------------------
            # 16. Deterministic explanation
            # ----------------------------------------------------

            explanation = (
                generate_explanation(
                    deterministic_profile,
                    llm_job,
                    score,
                )
            )

            # ----------------------------------------------------
            # 17. LLM explanation
            # ----------------------------------------------------

            try:

                llm_explanation = (
                    generate_llm_explanation(
                        candidate_name=(
                            deterministic_profile.name
                            or "Unknown"
                        ),

                        job_title=(
                            llm_job.title
                        ),

                        match_result=score,
                    )
                )

                explanation[
                    "summary"
                ] = llm_explanation.get(
                    "summary",
                    explanation[
                        "summary"
                    ],
                )

                explanation[
                    "strengths"
                ] = llm_explanation.get(
                    "strengths",
                    explanation[
                        "strengths"
                    ],
                )

                explanation[
                    "llm_concerns"
                ] = llm_explanation.get(
                    "concerns",
                    [],
                )

            except Exception:
                # Deterministic explanation
                # remains available.
                pass

            # ----------------------------------------------------
            # 18. Create API result
            # ----------------------------------------------------

            result = MatchResult(

                filename=filename,

                candidate_name=(
                    deterministic_profile.name
                    or "Unknown"
                ),

                final_score=(
                    score[
                        "final_score"
                    ]
                ),

                skill_score=(
                    score[
                        "skill_score"
                    ]
                ),

                preferred_skill_score=(
                    score[
                        "preferred_skill_score"
                    ]
                ),

                experience_score=(
                    score[
                        "experience_score"
                    ]
                ),

                education_score=(
                    score[
                        "education_score"
                    ]
                ),

                seniority_score=(
                    score[
                        "seniority_score"
                    ]
                ),

                semantic_score=(
                    score[
                        "semantic_score"
                    ]
                ),

                matched_skills=(
                    score[
                        "matched_skills"
                    ]
                ),

                missing_skills=(
                    score[
                        "missing_skills"
                    ]
                ),

                resume_skills=(
                    score[
                        "resume_skills"
                    ]
                ),

                job_required_skills=(
                    score[
                        "job_required_skills"
                    ]
                ),

                job_preferred_skills=(
                    score[
                        "job_preferred_skills"
                    ]
                ),

                candidate_seniority=(
                    score[
                        "candidate_seniority"
                    ]
                ),

                required_seniority=(
                    score[
                        "required_seniority"
                    ]
                ),

                explanation=(
                    explanation
                ),
            )

            results.append(
                result
            )

            # ----------------------------------------------------
            # 19. Save database result
            # ----------------------------------------------------

            db.add(
                ScreeningResult(

                    screening_run_id=(
                        screening_run.id
                    ),

                    candidate_name=(
                        result.candidate_name
                    ),

                    filename=(
                        result.filename
                    ),

                    score=(
                        result.final_score
                    ),

                    skill_score=(
                        result.skill_score
                    ),

                    preferred_skill_score=(
                        result.preferred_skill_score
                    ),

                    experience_score=(
                        result.experience_score
                    ),

                    education_score=(
                        result.education_score
                    ),

                    seniority_score=(
                        result.seniority_score
                    ),

                    semantic_score=(
                        result.semantic_score
                    ),

                    matched_skills=json.dumps(
                        result.matched_skills
                    ),

                    missing_skills=json.dumps(
                        result.missing_skills
                    ),

                    resume_skills=json.dumps(
                        result.resume_skills
                    ),

                    job_required_skills=json.dumps(
                        result.job_required_skills
                    ),

                    job_preferred_skills=json.dumps(
                        result.job_preferred_skills
                    ),

                    candidate_seniority=(
                        result.candidate_seniority
                    ),

                    required_seniority=(
                        result.required_seniority
                    ),

                    explanation_summary=(
                        result.explanation.summary
                    ),

                    explanation_strengths=(
                        json.dumps(
                            result.explanation.strengths
                        )
                    ),

                    explanation_concerns=(
                        json.dumps(
                            result.explanation.llm_concerns
                        )
                    ),
                )
            )

        # --------------------------------------------------------
        # 20. Commit
        # --------------------------------------------------------

        db.commit()

    except HTTPException:
        db.rollback()
        raise

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Screening failed: "
                f"{exc}"
            ),
        ) from exc

    # ------------------------------------------------------------
    # 21. Sort highest score first
    # ------------------------------------------------------------

    results.sort(
        key=lambda result: (
            result.final_score
        ),
        reverse=True,
    )

    return results


# ================================================================
# GET RESULTS
# ================================================================

@router.get(
    "/results"
)
def get_results(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    query = (
        db.query(
            ScreeningResult
        )
        .join(
            ScreeningRun,
            ScreeningResult.screening_run_id
            == ScreeningRun.id,
        )
    )

    # Recruiters see only their own results.
    # Admins see all results.
    if current_user.role != "admin":
        query = query.filter(
            ScreeningRun.user_id
            == current_user.id
        )

    rows = (
        query
        .order_by(
            ScreeningResult.score.desc()
        )
        .all()
    )

    return [
        {
            "id": row.id,

            "candidate_name": (
                row.candidate_name
            ),

            "filename": (
                row.filename
            ),

            "score": (
                row.score
            ),

            "matched_skills": (
                json.loads(
                    row.matched_skills
                )
                if row.matched_skills
                else []
            ),

            "missing_skills": (
                json.loads(
                    row.missing_skills
                )
                if row.missing_skills
                else []
            ),

            "semantic_score": (
                row.semantic_score
            ),

            "skill_score": (
                row.skill_score
            ),

            "preferred_skill_score": (
                row.preferred_skill_score
            ),

            "experience_score": (
                row.experience_score
            ),

            "education_score": (
                row.education_score
            ),

            "seniority_score": (
                row.seniority_score
            ),

            "created_at": (
                row.created_at.isoformat()
            ),
        }

        for row in rows
    ]


# ================================================================
# GET SCREENING HISTORY
# ================================================================

@router.get(
    "/history"
)
def get_screening_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    query = db.query(
        ScreeningRun
    )

    # Recruiters see only their own history.
    # Admins see all history.
    if current_user.role != "admin":
        query = query.filter(
            ScreeningRun.user_id
            == current_user.id
        )

    runs = (
        query
        .order_by(
            ScreeningRun.created_at.desc()
        )
        .all()
    )

    output = []

    for run in runs:

        scores = [
            result.score
            for result in run.results
        ]

        top_score = (
            max(scores)
            if scores
            else 0.0
        )

        average_score = (
            sum(scores) / len(scores)
            if scores
            else 0.0
        )

        output.append(
            {
                "id": run.id,

                "job_title": (
                    run.job_title
                ),

                "candidate_count": (
                    run.candidate_count
                ),

                "top_score": round(
                    top_score,
                    2,
                ),

                "average_score": round(
                    average_score,
                    2,
                ),

                "created_at": (
                    run.created_at.isoformat()
                ),
            }
        )

    return output


# ================================================================
# GET HISTORY DETAIL
# ================================================================

@router.get(
    "/history/{run_id}"
)
def get_screening_history_detail(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    run = (
        db.query(
            ScreeningRun
        )
        .filter(
            ScreeningRun.id
            == run_id
        )
        .first()
    )

    if run is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Screening run "
                "not found."
            ),
        )

    # Recruiters can only access their own run.
    # Admins can access every run.
    if (
        current_user.role != "admin"
        and run.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail=(
                "You do not have permission "
                "to access this screening run."
            ),
        )

    results = sorted(
        run.results,
        key=lambda result: (
            result.score
        ),
        reverse=True,
    )

    return {
        "id": run.id,

        "job_title": (
            run.job_title
        ),

        "job_description": (
            run.job_description
        ),

        "candidate_count": (
            run.candidate_count
        ),

        "created_at": (
            run.created_at.isoformat()
        ),

        "results": [

            {
                "id": result.id,

                "candidate_name": (
                    result.candidate_name
                ),

                "filename": (
                    result.filename
                ),

                "final_score": (
                    result.score
                ),

                "skill_score": (
                    result.skill_score
                ),

                "preferred_skill_score": (
                    result.preferred_skill_score
                ),

                "experience_score": (
                    result.experience_score
                ),

                "education_score": (
                    result.education_score
                ),

                "seniority_score": (
                    result.seniority_score
                ),

                "semantic_score": (
                    result.semantic_score
                ),

                "matched_skills": (
                    json.loads(
                        result.matched_skills
                    )
                    if result.matched_skills
                    else []
                ),

                "missing_skills": (
                    json.loads(
                        result.missing_skills
                    )
                    if result.missing_skills
                    else []
                ),

                "resume_skills": (
                    json.loads(
                        result.resume_skills
                    )
                    if result.resume_skills
                    else []
                ),

                "job_required_skills": (
                    json.loads(
                        result.job_required_skills
                    )
                    if result.job_required_skills
                    else []
                ),

                "job_preferred_skills": (
                    json.loads(
                        result.job_preferred_skills
                    )
                    if result.job_preferred_skills
                    else []
                ),

                "candidate_seniority": (
                    result.candidate_seniority
                ),

                "required_seniority": (
                    result.required_seniority
                ),

                "explanation": {

                    "summary": (
                        result.explanation_summary
                    ),

                    "strengths": (
                        json.loads(
                            result.explanation_strengths
                        )
                        if result.explanation_strengths
                        else []
                    ),

                    "concerns": (
                        json.loads(
                            result.explanation_concerns
                        )
                        if result.explanation_concerns
                        else []
                    ),
                },

                "created_at": (
                    result.created_at.isoformat()
                ),
            }

            for result in results
        ],
    }


# ================================================================
# DELETE HISTORY
# ================================================================

@router.delete(
    "/history/{run_id}"
)
def delete_screening_history(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    run = (
        db.query(
            ScreeningRun
        )
        .filter(
            ScreeningRun.id
            == run_id
        )
        .first()
    )

    if run is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Screening run "
                "not found."
            ),
        )

    # Recruiters can delete only their own runs.
    # Admins can delete any run.
    if (
        current_user.role != "admin"
        and run.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail=(
                "You do not have permission "
                "to delete this screening run."
            ),
        )

    db.delete(
        run
    )

    db.commit()

    return {
        "message": (
            "Screening run "
            "deleted successfully."
        ),

        "run_id": run_id,
    }
