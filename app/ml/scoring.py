from app.ml.matcher import (
    semantic_similarity,
)

from app.schemas.job import JobProfile
from app.schemas.resume import ResumeProfile


def calculate_match(
    resume: ResumeProfile,
    job: JobProfile,
) -> dict:

    resume_skills = {
        skill.lower(): skill
        for skill in resume.skills
    }

    required_skills = (
        job.required_skills
    )

    matched_skills = [
        skill
        for skill in required_skills
        if skill.lower()
        in resume_skills
    ]

    missing_skills = [
        skill
        for skill in required_skills
        if skill.lower()
        not in resume_skills
    ]

    if required_skills:

        skill_score = (
            len(matched_skills)
            / len(required_skills)
            * 100
        )

    else:

        skill_score = 0.0

    semantic_score = semantic_similarity(
        resume.raw_text,
        job.raw_text,
    )

    final_score = (
        0.70 * skill_score
        + 0.30 * semantic_score
    )

    return {

        "final_score": round(
            final_score,
            2,
        ),

        "skill_score": round(
            skill_score,
            2,
        ),

        "semantic_score": semantic_score,

        "matched_skills": matched_skills,

        "missing_skills": missing_skills,

        "resume_skills": resume.skills,

        "job_required_skills": required_skills,
    }
