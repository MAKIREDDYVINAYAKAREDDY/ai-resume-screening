from pathlib import Path


def extract_text_from_txt(
    file_path: str,
) -> str:

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            file_path
        )

    return path.read_text(
        encoding="utf-8"
    ).strip()


def extract_text_from_txt_bytes(
    data: bytes,
) -> str:

    return data.decode(
        "utf-8"
    ).strip()
