from pathlib import Path

from app.resume.docx_parser import (
    extract_text_from_docx,
    extract_text_from_docx_bytes,
)

from app.resume.pdf_parser import (
    extract_text_from_pdf,
    extract_text_from_pdf_bytes,
)

from app.resume.txt_parser import (
    extract_text_from_txt,
    extract_text_from_txt_bytes,
)


SUPPORTED_FORMATS = {
    ".pdf",
    ".docx",
    ".txt",
}


def extract_resume_text(
    file_path: str,
) -> str:

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            file_path
        )

    extension = path.suffix.lower()

    if extension == ".pdf":
        return extract_text_from_pdf(
            str(path)
        )

    if extension == ".docx":
        return extract_text_from_docx(
            str(path)
        )

    if extension == ".txt":
        return extract_text_from_txt(
            str(path)
        )

    raise ValueError(
        f"Unsupported resume format: "
        f"{extension}"
    )


def extract_resume_text_from_bytes(
    filename: str,
    data: bytes,
) -> str:

    extension = Path(
        filename
    ).suffix.lower()

    if extension == ".pdf":
        return extract_text_from_pdf_bytes(
            data
        )

    if extension == ".docx":
        return extract_text_from_docx_bytes(
            data
        )

    if extension == ".txt":
        return extract_text_from_txt_bytes(
            data
        )

    raise ValueError(
        f"Unsupported resume format: "
        f"{extension}"
    )
