from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from fastapi.security import (
    OAuth2PasswordRequestForm,
)

from pydantic import (
    BaseModel,
    EmailStr,
)

from sqlalchemy.orm import (
    Session,
)

from app.auth.dependencies import (
    get_current_user,
)

from app.auth.security import (
    create_access_token,
    hash_password,
    verify_password,
)

from app.database.database import (
    get_db,
)

from app.database.models import (
    User,
)


router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)


# ============================================================
# REQUEST / RESPONSE SCHEMAS
# ============================================================

class RegisterRequest(BaseModel):

    username: str

    email: EmailStr

    password: str


class UserResponse(BaseModel):

    id: int

    username: str

    email: str

    role: str

    is_active: bool

    class Config:

        from_attributes = True


# ============================================================
# REGISTER
# ============================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest,
    db: Session = Depends(
        get_db
    ),
):

    username = request.username.strip()

    email = str(
        request.email
    ).lower().strip()

    password = request.password

    # --------------------------------------------------------
    # Username validation
    # --------------------------------------------------------

    if len(username) < 3:

        raise HTTPException(
            status_code=400,
            detail=(
                "Username must contain "
                "at least 3 characters."
            ),
        )

    if len(username) > 100:

        raise HTTPException(
            status_code=400,
            detail=(
                "Username cannot exceed "
                "100 characters."
            ),
        )

    # --------------------------------------------------------
    # Password validation
    # --------------------------------------------------------

    if len(password) < 8:

        raise HTTPException(
            status_code=400,
            detail=(
                "Password must contain "
                "at least 8 characters."
            ),
        )

    # --------------------------------------------------------
    # Username uniqueness
    # --------------------------------------------------------

    existing_username = (
        db.query(User)
        .filter(
            User.username == username
        )
        .first()
    )

    if existing_username:

        raise HTTPException(
            status_code=409,
            detail=(
                "Username is already registered."
            ),
        )

    # --------------------------------------------------------
    # Email uniqueness
    # --------------------------------------------------------

    existing_email = (
        db.query(User)
        .filter(
            User.email == email
        )
        .first()
    )

    if existing_email:

        raise HTTPException(
            status_code=409,
            detail=(
                "Email is already registered."
            ),
        )

    # --------------------------------------------------------
    # Create recruiter
    # --------------------------------------------------------

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(
            password
        ),
        role="recruiter",
        is_active=True,
    )

    db.add(user)

    try:

        db.commit()

        db.refresh(user)

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not create user account."
            ),
        )

    return user


# ============================================================
# LOGIN
# ============================================================

@router.post(
    "/login"
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(
        get_db
    ),
):

    username = (
        form_data.username.strip()
    )

    user = (
        db.query(User)
        .filter(
            User.username == username
        )
        .first()
    )

    if user is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Invalid username or password."
            ),
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    if not verify_password(
        form_data.password,
        user.password_hash,
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Invalid username or password."
            ),
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    if not user.is_active:

        raise HTTPException(
            status_code=403,
            detail=(
                "User account is inactive."
            ),
        )

    access_token = (
        create_access_token(
            data={
                "sub": str(user.id),
                "username": user.username,
                "role": user.role,
            }
        )
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
        },
    }


# ============================================================
# CURRENT USER
# ============================================================

@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(
        get_current_user
    ),
):

    return current_user
