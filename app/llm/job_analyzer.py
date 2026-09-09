import json

from app.llm.ollama_client import (
    get_ollama_client,
    get_ollama_model,
)
from app.schemas.llm import LLMJobAnalysis


JOB_SCHEMA = {
    "type": "object",
    "properties": {
        "job_title": {
            "type": "string"
        },
        "required_skills": {
            "type": "array",
            "items": {"type": "string"}
        },
        "preferred_skills": {
            "type": "array",
            "items": {"type": "string"}
        },
        "experience_years": {
            "type": "number"
        },
        "seniority": {
            "type": ["string", "null"]
        },
        "education": {
            "type": "array",
            "items": {"type": "string"}
        },
        "responsibilities": {
            "type": "array",
            "items": {"type": "string"}
        },
    },
    "required": [
        "job_title",
        "required_skills",
        "preferred_skills",
        "experience_years",
        "seniority",
        "education",
        "responsibilities",
    ],
    "additionalProperties": False,
}


def analyze_job(job_description: str) -> LLMJobAnalysis:
    if not job_description.strip():
        raise ValueError("Job description is empty.")

    client = get_ollama_client()
    model = get_ollama_model()

    prompt = f"""
You are a job description analysis system.

Extract ONLY information explicitly supported
by the job description.

Rules:
- Do not invent skills.
- Do not invent experience requirements.
- Do not invent education requirements.
- Do not infer protected characteristics.
- Separate required skills from preferred skills.
- Extract the minimum required years of experience.
- Identify seniority only when explicitly stated.
- Return ONLY valid JSON matching the schema.

Schema:

{json.dumps(JOB_SCHEMA, indent=2)}

Job description:

{job_description}
"""

    response = client.chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a precise job description "
                    "information extraction system."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        format=JOB_SCHEMA,
        options={
            "temperature": 0,
        },
    )

    content = response["message"]["content"]

    data = json.loads(content)

    return LLMJobAnalysis(**data)
