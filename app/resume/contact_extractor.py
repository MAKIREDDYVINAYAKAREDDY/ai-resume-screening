import re


EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+"
    r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)


PHONE_PATTERN = re.compile(
    r"(?<!\d)"
    r"(?:\+?\d{1,3}[\s.-]?)?"
    r"(?:\(?\d{3,5}\)?[\s.-]?)?"
    r"\d{3,5}[\s.-]?"
    r"\d{3,5}"
    r"(?!\d)"
)


def extract_email(
    text: str,
) -> str | None:

    match = EMAIL_PATTERN.search(
        text
    )

    if match:
        return match.group(0)

    return None


def extract_phone(
    text: str,
) -> str | None:

    match = PHONE_PATTERN.search(
        text
    )

    if match:
        return match.group(0)

    return None
