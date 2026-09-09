from app.llm.job_analyzer import analyze_job


job_description = """
JOB TITLE: Senior Machine Learning Engineer

REQUIRED SKILLS:
Python
SQL
Machine Learning
PyTorch
Scikit-learn
Pandas
NumPy
Docker
Git

PREFERRED SKILLS:
AWS
Kubernetes
MLflow
FastAPI
Natural Language Processing

EXPERIENCE:
5+ years of experience in machine learning or data science.

EDUCATION:
Master's degree in Computer Science, Data Science,
Artificial Intelligence, or a related field.

RESPONSIBILITIES:
- Design and deploy machine learning models.
- Build data preprocessing pipelines.
- Train and evaluate ML models.
- Develop production ML APIs.
- Monitor model performance.
"""


if __name__ == "__main__":
    result = analyze_job(job_description)

    print("\nLLM JOB ANALYSIS")
    print("=" * 60)
    print(result.model_dump_json(indent=2))
