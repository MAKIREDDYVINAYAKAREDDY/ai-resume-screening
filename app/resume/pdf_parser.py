from pathlib import Path

import pymupdf


def extract_text_from_pdf(
    file_path: str,
) -> str:

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            file_path
        )

    if path.suffix.lower() != ".pdf":
        raise ValueError(
            "Expected a PDF file"
        )

    document = pymupdf.open(
        str(path)
    )

    try:

        pages = []

        for page in document:
            pages.append(
                page.get_text("text")
            )

        return "\n".join(pages).strip()

    finally:

        document.close()


def extract_text_from_pdf_bytes(
    data: bytes,
) -> str:

    document = pymupdf.open(
        stream=data,
        filetype="pdf",
    )

    try:

        return "\n".join(
            page.get_text("text")
            for page in document
        ).strip()

    finally:

        document.close()
