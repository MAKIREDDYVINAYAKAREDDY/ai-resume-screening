from app.llm.job_analyzer import analyze_job
from app.llm.resume_analyzer import analyze_resume
from app.schemas.job import JobProfile
from app.schemas.resume import EducationItem, ExperienceItem, ResumeProfile


def llm_resume_to_profile(
    analysis,
    raw_text: str,
) -> ResumeProfile:
    experience = [
        ExperienceItem(
            job_title=item,
            description=item,
            duration_years=0.0,
        )
        for item in analysis.relevant_experience
    ]

    education = [
        EducationItem(
            degree=item,
        )
        for item in analysis.education
    ]

    profile = ResumeProfile(
        name=analysis.candidate_name,
        summary=analysis.professional_summary,
        skills=analysis.skills,
        experience=experience,
        education=education,
        certifications=analysis.certifications,
        projects=analysis.projects,
        seniority=analysis.seniority,
        raw_text=raw_text,
    )

    return profile


def llm_job_to_profile(
    analysis,
    raw_text: str,
) -> JobProfile:
    return JobProfile(
        title=analysis.job_title,
        required_skills=analysis.required_skills,
        preferred_skills=analysis.preferred_skills,
        experience_years=analysis.experience_years,
        seniority=analysis.seniority,
        education=analysis.education,
        raw_text=raw_text,
    )


def analyze_resume_with_llm(
    resume_text: str,
) -> ResumeProfile:
    analysis = analyze_resume(resume_text)

    return llm_resume_to_profile(
        analysis,
        resume_text,
    )


def analyze_job_with_llm(
    job_description: str,
) -> JobProfile:
    analysis = analyze_job(job_description)

    return llm_job_to_profile(
        analysis,
        job_description,
    )
