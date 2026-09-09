import re


SKILL_ALIASES = {
    "ml": "Machine Learning",
    "machine-learning": "Machine Learning",
    "machinelearning": "Machine Learning",

    "dl": "Deep Learning",
    "deep-learning": "Deep Learning",
    "deeplearning": "Deep Learning",

    "nlp": "Natural Language Processing",
    "natural-language-processing": "Natural Language Processing",

    "cv": "Computer Vision",
    "computer-vision": "Computer Vision",

    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",

    "tf": "TensorFlow",
    "tensorflow": "TensorFlow",

    "pytorch": "PyTorch",

    "sklearn": "Scikit-learn",
    "scikit learn": "Scikit-learn",
    "scikit-learn": "Scikit-learn",

    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",

    "mongo": "MongoDB",
    "mongodb": "MongoDB",

    "js": "JavaScript",
    "javascript": "JavaScript",

    "ts": "TypeScript",
    "typescript": "TypeScript",

    "reactjs": "React",
    "react.js": "React",

    "nodejs": "Node.js",
    "node.js": "Node.js",

    "aws": "AWS",
    "amazon web services": "AWS",

    "gcp": "GCP",
    "google cloud": "GCP",

    "azure": "Azure",

    "ci cd": "CI/CD",
    "ci-cd": "CI/CD",
    "cicd": "CI/CD",
}


def normalize_skill(skill: str) -> str:
    """
    Convert a skill or alias into a canonical skill name.
    """

    if not skill:
        return ""

    value = skill.strip().lower()

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    value = value.strip(".,;:()[]{}")

    return SKILL_ALIASES.get(
        value,
        skill.strip(),
    )


def normalize_skills(
    skills: list[str],
) -> list[str]:
    """
    Normalize skills and remove duplicates.
    """

    normalized = []

    seen = set()

    for skill in skills:
        canonical = normalize_skill(skill)

        if not canonical:
            continue

        key = canonical.lower()

        if key not in seen:
            normalized.append(canonical)
            seen.add(key)

    return normalized
