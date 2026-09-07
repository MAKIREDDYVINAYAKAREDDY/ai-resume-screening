import re


def clean_text(text: str) -> str:

    if not text:
        return ""

    text = text.replace(
        "\x00",
        " ",
    )

    text = text.lower()

    text = re.sub(
        r"[^a-zA-Z0-9+#./@_\- ]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()
