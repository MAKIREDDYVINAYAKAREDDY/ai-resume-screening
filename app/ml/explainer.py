from app.schemas.job import JobProfile
from app.schemas.resume import ResumeProfile


def generate_explanation(
    resume: ResumeProfile,
    job: JobProfile,
    score: dict,
) -> dict:

    required_count = len(
        job.required_skills
    )

    matched_count = len(
        score["matched_skills"]
    )

    candidate_experience = round(
        sum(
            item.duration_years
            for item in resume.experience
        ),
        1,
    )

    required_experience = job.experience_years

    if required_experience > 0:
        experience_text = (
            f"{candidate_experience} years experience "
            f"vs {required_experience} years required"
        )
    else:
        experience_text = (
            f"{candidate_experience} years experience"
        )

    if score["education_score"] >= 100:
        education_text = (
            "Education requirement satisfied"
        )
    elif score["education_score"] > 0:
        education_text = (
            "Some education requirements matched"
        )
    else:
        education_text = (
            "Education requirement not matched"
        )

    if score["semantic_score"] >= 80:
        semantic_text = "Strong semantic relevance"
    elif score["semantic_score"] >= 60:
        semantic_text = "Moderate semantic relevance"
    else:
        semantic_text = "Low semantic relevance"

    strengths = [
        f"{matched_count}/{required_count} "
        "required skills matched"
        if required_count
        else "No required skills specified",

        experience_text,

        education_text,

        semantic_text,
    ]

    missing_skills = score[
        "missing_skills"
    ]

    return {
        "summary": (
            f"{score['final_score']:.1f}% overall match"
        ),

        "strengths": strengths,

        "missing_skills": missing_skills,

        "matched_skills": score[
            "matched_skills"
        ],

        "score_breakdown": {
            "skills": score[
                "skill_score"
            ],
            "experience": score[
                "experience_score"
            ],
            "education": score[
                "education_score"
            ],
            "semantic": score[
                "semantic_score"
            ],
        },
    }
