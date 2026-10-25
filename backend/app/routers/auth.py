from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, StudentProfile, PrivacyPreference
from app.schemas.user import (
    UserCreate, UserLogin, UserResponse, TokenResponse, TokenRefreshRequest,
    StudentProfileUpdate, StudentProfileResponse
)
from app.core.security import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    decode_access_token, access_token_ttl
)
from app.core.deps import get_current_user
from app.core.rate_limit import (
    login_block_reason, record_login_failure, clear_login_failures
)

router = APIRouter(prefix="/auth", tags=["Authentication & Profiles"])


def _token_response(user: User) -> dict:
    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
        "refresh_token": create_refresh_token(user.id),
        "expires_in": int(access_token_ttl().total_seconds()),
        "user": user,
    }


def _rate_keys(request: Request, email: str) -> tuple:
    ip = request.client.host if request.client else "unknown"
    return (f"login:email:{email}", f"login:ip:{ip}")

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_in.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    # Create new user
    user = User(
        email=user_in.email.lower(),
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Initialize default student profile and privacy preferences
    profile = StudentProfile(user_id=user.id)
    privacy = PrivacyPreference(user_id=user.id)
    db.add(profile)
    db.add(privacy)
    db.commit()

    return _token_response(user)

@router.post("/login", response_model=TokenResponse)
def login(
    login_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    email_key, ip_key = _rate_keys(request, login_data.email.lower())
    retry_after = login_block_reason(email_key, ip_key)
    if retry_after is not None:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Please try again later.",
            headers={"Retry-After": str(retry_after)},
        )

    user = db.query(User).filter(User.email == login_data.email.lower()).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        record_login_failure(email_key, ip_key)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )

    if not user.is_active:
        record_login_failure(email_key, ip_key)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is inactive."
        )

    clear_login_failures(email_key, ip_key)
    return _token_response(user)

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(payload: TokenRefreshRequest, db: Session = Depends(get_db)):
    """Exchange a refresh token for a fresh short-lived access token."""
    data = decode_access_token(payload.refresh_token)
    if not data or data.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    try:
        user = db.query(User).filter(User.id == int(data.get("sub", ""))).first()
    except (TypeError, ValueError):
        user = None
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    return _token_response(user)

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/profile", response_model=StudentProfileResponse)
def get_student_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        profile = StudentProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@router.put("/profile", response_model=StudentProfileResponse)
def update_student_profile(
    profile_in: StudentProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        profile = StudentProfile(user_id=current_user.id)
        db.add(profile)

    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile
