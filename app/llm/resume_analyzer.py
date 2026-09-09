import json

from app.llm.ollama_client import (
    get_ollama_client,
    get_ollama_model,
)
from app.schemas.llm import LLMResumeAnalysis


RESUME_SCHEMA = {
    "type": "object",
    "properties": {
        "candidate_name": {
            "type": ["string", "null"]
        },
        "professional_summary": {
            "type": "string"
        },
        "skills": {
            "type": "array",
            "items": {"type": "string"}
        },
        "experience_years": {
            "type": "number"
        },
        "seniority": {
            "type": ["string", "null"]
        },
        "relevant_experience": {
            "type": "array",
            "items": {"type": "string"}
        },
        "education": {
            "type": "array",
            "items": {"type": "string"}
        },
        "certifications": {
            "type": "array",
            "items": {"type": "string"}
        },
        "projects": {
            "type": "array",
            "items": {"type": "string"}
        },
    },
    "required": [
        "candidate_name",
        "professional_summary",
        "skills",
        "experience_years",
        "seniority",
        "relevant_experience",
        "education",
        "certifications",
        "projects",
    ],
}


def analyze_resume(resume_text: str) -> LLMResumeAnalysis:
    client = get_ollama_client()
    model = get_ollama_model()

    prompt = f"""
You are a resume analysis system.

Extract ONLY information explicitly supported
by the resume text.

Do not invent facts.
Do not infer protected characteristics.

Return ONLY valid JSON matching this schema:

{json.dumps(RESUME_SCHEMA, indent=2)}

Resume:

{resume_text}
"""

    response = client.chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a precise resume information "
                    "extraction system."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        format=RESUME_SCHEMA,
        options={
            "temperature": 0,
        },
    )

    content = response["message"]["content"]

    data = json.loads(content)

    return LLMResumeAnalysis(**data)
