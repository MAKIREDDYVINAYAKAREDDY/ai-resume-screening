import json

from app.llm.ollama_client import (
    get_ollama_client,
    get_ollama_model,
)


def generate_llm_explanation(
    candidate_name: str,
    job_title: str,
    match_result: dict,
) -> dict:

    client = get_ollama_client()
    model = get_ollama_model()

    prompt = f"""
You are an explainability assistant for a resume
screening decision-support system.

Do NOT make a hiring decision.

Explain the numerical matching result using only
the supplied information.

Candidate:
{candidate_name}

Job:
{job_title}

Match result:
{json.dumps(match_result, indent=2)}

Return ONLY JSON using this structure:

{{
  "summary": "short explanation",
  "strengths": [
    "strength 1",
    "strength 2"
  ],
  "concerns": [
    "concern 1",
    "concern 2"
  ]
}}

Rules:
- Do not invent candidate information.
- Do not infer protected characteristics.
- Do not recommend rejecting or hiring someone.
- Focus only on job-relevant evidence.
- Mention missing required skills when relevant.
"""

    response = client.chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You generate factual explanations "
                    "for ML matching results."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        format={
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string"
                },
                "strengths": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                },
                "concerns": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                },
            },
            "required": [
                "summary",
                "strengths",
                "concerns",
            ],
        },
        options={
            "temperature": 0,
        },
    )

    return json.loads(
        response["message"]["content"]
    )
