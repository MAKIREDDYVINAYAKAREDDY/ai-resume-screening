from pathlib import Path
import re
import zipfile
import io


# ================================================================
# Upload limits
# ================================================================

MAX_RESUME_SIZE = 10 * 1024 * 1024

MAX_RESUMES_PER_REQUEST = 20

MIN_JOB_DESCRIPTION_LENGTH = 20

MAX_JOB_DESCRIPTION_LENGTH = 20_000


# ================================================================
# Supported resume formats
# ================================================================

ALLOWED_RESUME_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
}


# ================================================================
# Filename validation
# ================================================================

def validate_resume_extension(
    filename: str,
) -> None:
    if not filename:
        raise ValueError(
            "Resume filename is required."
        )

    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_RESUME_EXTENSIONS:
        allowed = ", ".join(
            sorted(ALLOWED_RESUME_EXTENSIONS)
        )

        raise ValueError(
            f"Unsupported resume format "
            f"'{extension}'. "
            f"Allowed formats: {allowed}."
        )


# ================================================================
# File size validation
# ================================================================

def validate_resume_size(
    file_size: int,
) -> None:
    if file_size <= 0:
        raise ValueError(
            "Resume file is empty."
        )

    if file_size > MAX_RESUME_SIZE:
        max_mb = MAX_RESUME_SIZE / (
            1024 * 1024
        )

        raise ValueError(
            f"Resume file is too large. "
            f"Maximum allowed size is "
            f"{max_mb:.0f} MB."
        )


# ================================================================
# Number of resumes validation
# ================================================================

def validate_resume_count(
    resume_count: int,
) -> None:
    if resume_count <= 0:
        raise ValueError(
            "At least one resume is required."
        )

    if resume_count > MAX_RESUMES_PER_REQUEST:
        raise ValueError(
            f"Too many resumes. "
            f"A maximum of "
            f"{MAX_RESUMES_PER_REQUEST} "
            f"resumes can be screened "
            f"per request."
        )


# ================================================================
# Job description validation
# ================================================================

def validate_job_description(
    job_description: str,
) -> None:
    if not job_description:
        raise ValueError(
            "Job description is required."
        )

    cleaned = job_description.strip()

    if not cleaned:
        raise ValueError(
            "Job description cannot be empty."
        )

    if len(cleaned) < MIN_JOB_DESCRIPTION_LENGTH:
        raise ValueError(
            f"Job description is too short. "
            f"Minimum length is "
            f"{MIN_JOB_DESCRIPTION_LENGTH} characters."
        )

    if len(cleaned) > MAX_JOB_DESCRIPTION_LENGTH:
        raise ValueError(
            f"Job description is too long. "
            f"Maximum length is "
            f"{MAX_JOB_DESCRIPTION_LENGTH} characters."
        )


# ================================================================
# Filename sanitization
# ================================================================

def sanitize_filename(
    filename: str,
) -> str:
    name = Path(filename).name

    name = re.sub(
        r"[^A-Za-z0-9._-]",
        "_",
        name,
    )

    name = re.sub(
        r"_+",
        "_",
        name,
    )

    if not name:
        return "resume"

    return name[:255]


# ================================================================
# PDF content validation
# ================================================================

def validate_pdf_content(
    data: bytes,
) -> None:
    if not data:
        raise ValueError(
            "PDF file is empty."
        )

    # PDF files begin with %PDF
    if not data.startswith(b"%PDF"):
        raise ValueError(
            "File extension is .pdf, "
            "but the file does not contain "
            "a valid PDF signature."
        )


# ================================================================
# DOCX content validation
# ================================================================

def validate_docx_content(
    data: bytes,
) -> None:
    if not data:
        raise ValueError(
            "DOCX file is empty."
        )

    # DOCX files are ZIP containers.
    if not data.startswith(b"PK"):
        raise ValueError(
            "File extension is .docx, "
            "but the file is not a valid "
            "Office document container."
        )

    try:
        with zipfile.ZipFile(
            io.BytesIO(data)
        ) as archive:

            names = set(
                archive.namelist()
            )

            if "[Content_Types].xml" not in names:
                raise ValueError(
                    "DOCX file is missing "
                    "[Content_Types].xml."
                )

            if (
                "word/document.xml"
                not in names
            ):
                raise ValueError(
                    "DOCX file is missing "
                    "word/document.xml."
                )

            if archive.testzip() is not None:
                raise ValueError(
                    "DOCX archive is corrupted."
                )

    except zipfile.BadZipFile as exc:
        raise ValueError(
            "File extension is .docx, "
            "but the file is not a valid "
            "DOCX archive."
        ) from exc


# ================================================================
# TXT content validation
# ================================================================

def validate_txt_content(
    data: bytes,
) -> None:
    if not data:
        raise ValueError(
            "TXT file is empty."
        )

    encodings = (
        "utf-8",
        "utf-8-sig",
        "latin-1",
    )

    for encoding in encodings:
        try:
            text = data.decode(
                encoding
            )

            if not text.strip():
                raise ValueError(
                    "TXT file contains no "
                    "readable text."
                )

            return

        except UnicodeDecodeError:
            continue

    raise ValueError(
        "TXT file does not contain "
        "readable text."
    )


# ================================================================
# General content validation
# ================================================================

def validate_resume_content(
    filename: str,
    data: bytes,
) -> None:
    extension = Path(
        filename
    ).suffix.lower()

    if extension == ".pdf":
        validate_pdf_content(data)

    elif extension == ".docx":
        validate_docx_content(data)

    elif extension == ".txt":
        validate_txt_content(data)

    else:
        raise ValueError(
            f"Unsupported resume format "
            f"'{extension}'."
        )
