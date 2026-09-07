def extract_name(
    text: str,
) -> str | None:

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return None

    ignored = {
        "resume",
        "curriculum vitae",
        "cv",
        "profile",
        "summary",
    }

    first_line = lines[0]

    if (
        first_line.lower() in ignored
        and len(lines) > 1
    ):
        return lines[1]

    return first_line
