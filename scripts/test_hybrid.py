from app.llm.hybrid_analyzer import (
    analyze_job_with_llm,
    analyze_resume_with_llm,
)
from app.ml.scoring import calculate_match


resume = """
John Doe

Machine Learning Engineer

Experienced machine learning engineer with 4.7 years
of experience building production ML systems.

Skills:
Python, SQL, Pandas, NumPy, Scikit-learn,
Machine Learning, Docker, Git

Experience:
Machine Learning Engineer at ABC Technologies
2021 - Present

Data Analyst at XYZ Corp
2019 - 2021

Education:
Bachelor's degree in Computer Science.
"""


job = """
JOB TITLE: Machine Learning Engineer

REQUIRED SKILLS:
Python
SQL
Machine Learning
Pandas
NumPy
Scikit-learn
Docker
Git
Statistics

PREFERRED SKILLS:
PyTorch
AWS
Kubernetes
MLflow

EXPERIENCE:
3+ years of experience in machine learning.

EDUCATION:
Bachelor's degree in Computer Science.

RESPONSIBILITIES:
Build and deploy machine learning models.
Develop data preprocessing pipelines.
Deploy production ML services.
"""


if __name__ == "__main__":
    print("\nAnalyzing resume with Ollama...")
    resume_profile = analyze_resume_with_llm(resume)

    print("\nAnalyzing job with Ollama...")
    job_profile = analyze_job_with_llm(job)

    print("\nRESUME PROFILE")
    print("=" * 60)
    print(resume_profile.model_dump_json(indent=2))

    print("\nJOB PROFILE")
    print("=" * 60)
    print(job_profile.model_dump_json(indent=2))

    print("\nDETERMINISTIC MATCH")
    print("=" * 60)

    result = calculate_match(
        resume_profile,
        job_profile,
    )

    print(result)
