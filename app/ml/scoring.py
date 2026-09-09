from app.ml.advanced_scoring import (
    calculate_preferred_skill_score,
    calculate_seniority_match_score,
)
from app.ml.education_matcher import (
    calculate_education_score as calculate_education_score_v2,
)
from app.ml.embedding_matcher import (
    semantic_similarity,
)
from app.ml.experience_matcher import (
    calculate_experience_score as calculate_experience_score_v2,
)
from app.schemas.job import JobProfile
from app.schemas.resume import ResumeProfile


REQUIRED_SKILL_WEIGHT = 0.35
EXPERIENCE_WEIGHT = 0.25
EDUCATION_WEIGHT = 0.10
PREFERRED_SKILL_WEIGHT = 0.10
SENIORITY_WEIGHT = 0.10
SEMANTIC_WEIGHT = 0.10


def calculate_experience_score(
    resume: ResumeProfile,
    job: JobProfile,
) -> float:

    return calculate_experience_score_v2(
        resume.experience,
        job.experience_years,
    )


def calculate_education_score(
    resume: ResumeProfile,
    job: JobProfile,
) -> float:

    return calculate_education_score_v2(
        job.education,
        resume.education,
    )


def calculate_skill_score(
    resume: ResumeProfile,
    job: JobProfile,
) -> tuple[float, list[str], list[str]]:

    resume_skills = {
        skill.lower(): skill
        for skill in resume.skills
    }

    required_skills = job.required_skills

    matched_skills = [
        skill
        for skill in required_skills
        if skill.lower() in resume_skills
    ]

    missing_skills = [
        skill
        for skill in required_skills
        if skill.lower() not in resume_skills
    ]

    if required_skills:
        skill_score = (
            len(matched_skills)
            / len(required_skills)
            * 100
        )
    else:
        skill_score = 100.0

    return (
        round(skill_score, 2),
        matched_skills,
        missing_skills,
    )


def calculate_match(
    resume: ResumeProfile,
    job: JobProfile,
) -> dict:

    (
        required_skill_score,
        matched_skills,
        missing_skills,
    ) = calculate_skill_score(
        resume,
        job,
    )

    experience_score = calculate_experience_score(
        resume,
        job,
    )

    education_score = calculate_education_score(
        resume,
        job,
    )

    preferred_skill_score = (
        calculate_preferred_skill_score(
            resume.skills,
            job.preferred_skills,
        )
    )

    seniority_score = (
        calculate_seniority_match_score(
            resume.seniority,
            job.seniority,
        )
    )

    semantic_score = semantic_similarity(
        resume.raw_text,
        job.raw_text,
    )

    final_score = (
        REQUIRED_SKILL_WEIGHT
        * required_skill_score
        + EXPERIENCE_WEIGHT
        * experience_score
        + EDUCATION_WEIGHT
        * education_score
        + PREFERRED_SKILL_WEIGHT
        * preferred_skill_score
        + SENIORITY_WEIGHT
        * seniority_score
        + SEMANTIC_WEIGHT
        * semantic_score
    )

    return {
        "final_score": round(
            final_score,
            2,
        ),
        "skill_score": required_skill_score,
        "experience_score": experience_score,
        "education_score": education_score,
        "preferred_skill_score": (
            preferred_skill_score
        ),
        "seniority_score": seniority_score,
        "semantic_score": semantic_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "resume_skills": resume.skills,
        "job_required_skills": (
            job.required_skills
        ),
        "job_preferred_skills": (
            job.preferred_skills
        ),
        "candidate_seniority": (
            resume.seniority
        ),
        "required_seniority": (
            job.seniority
        ),
    }
