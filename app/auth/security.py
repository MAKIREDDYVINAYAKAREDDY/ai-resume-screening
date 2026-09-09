from datetime import (
    datetime,
    timedelta,
    timezone,
)

import bcrypt

from jose import (
    JWTError,
    jwt,
)

from app.core.config import (
    get_settings,
)


settings = get_settings()


# bcrypt supports a maximum of 72 bytes.
MAX_PASSWORD_BYTES = 72


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    bcrypt only supports passwords up to 72 bytes.
    We explicitly validate the byte length so the
    application returns a controlled error instead
    of crashing inside the bcrypt library.
    """

    password_bytes = password.encode("utf-8")

    if len(password_bytes) > MAX_PASSWORD_BYTES:
        raise ValueError(
            "Password cannot exceed 72 bytes."
        )

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt(),
    )

    return hashed.decode("utf-8")


def verify_password(
    plain_password: str,
    password_hash: str,
) -> bool:
    """
    Verify a plain-text password against a bcrypt hash.
    """

    password_bytes = plain_password.encode("utf-8")

    if len(password_bytes) > MAX_PASSWORD_BYTES:
        return False

    try:
        return bcrypt.checkpw(
            password_bytes,
            password_hash.encode("utf-8"),
        )
    except (
        ValueError,
        TypeError,
    ):
        return False


def create_access_token(
    data: dict,
    expires_minutes: int | None = None,
) -> str:
    """
    Create a JWT access token.
    """

    payload = data.copy()

    if expires_minutes is None:
        expires_minutes = (
            settings.access_token_expire_minutes
        )

    expire = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=expires_minutes
        )
    )

    payload.update(
        {
            "exp": expire,
        }
    )

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(
    token: str,
) -> dict | None:
    """
    Decode and validate a JWT access token.
    """

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[
                settings.jwt_algorithm
            ],
        )

        return payload

    except JWTError:
        return None
