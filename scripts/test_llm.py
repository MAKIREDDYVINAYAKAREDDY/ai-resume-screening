from app.llm.resume_analyzer import analyze_resume


resume = """
John Doe

Professional Summary:
Machine Learning Engineer with experience building
production machine learning systems.

Skills:
Python
SQL
Machine Learning
Pandas
NumPy
Scikit-learn
PyTorch
Docker
Git

Experience:

Senior Machine Learning Engineer | ABC Technologies |
Jan 2022 - Present

Developed machine learning models and deployed
production APIs.

Education:

B.Tech Computer Science | XYZ University | 2017 - 2021

Projects:

Customer churn prediction system using Python,
Pandas and Scikit-learn.
"""


result = analyze_resume(resume)

print()
print("===== LLM RESUME ANALYSIS =====")
print()

print(
    result.model_dump_json(
        indent=2
    )
)
