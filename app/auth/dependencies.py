from fastapi import (
    Depends,
    HTTPException,
    status,
)

from fastapi.security import (
    OAuth2PasswordBearer,
)

from sqlalchemy.orm import Session

from app.auth.security import (
    decode_access_token,
)

from app.database.database import (
    get_db,
)

from app.database.models import (
    User,
)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login"
)


# ============================================================
# CURRENT USER
# ============================================================

def get_current_user(
    token: str = Depends(
        oauth2_scheme
    ),
    db: Session = Depends(
        get_db
    ),
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    payload = decode_access_token(
        token
    )

    if payload is None:
        raise credentials_exception

    user_id = payload.get(
        "sub"
    )

    if user_id is None:
        raise credentials_exception

    try:

        user_id_int = int(
            user_id
        )

    except (
        TypeError,
        ValueError,
    ):

        raise credentials_exception

    user = (
        db.query(User)
        .filter(
            User.id == user_id_int
        )
        .first()
    )

    if user is None:
        raise credentials_exception

    if not user.is_active:

        raise HTTPException(
            status_code=403,
            detail=(
                "User account is inactive."
            ),
        )

    return user


# ============================================================
# ROLE CHECK
# ============================================================

def require_role(
    *allowed_roles: str,
):

    normalized_roles = {
        role.lower().strip()
        for role in allowed_roles
    }

    def role_checker(
        current_user: User = Depends(
            get_current_user
        ),
    ) -> User:

        if (
            current_user.role.lower()
            not in normalized_roles
        ):

            raise HTTPException(
                status_code=403,
                detail=(
                    "You do not have permission "
                    "to perform this action."
                ),
            )

        return current_user

    return role_checker
