
from datetime import datetime, timedelta, timezone
import logging
import secrets

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, DatabaseSession
from app.core.config import settings
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.password_reset_otp import PasswordResetOTP
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    SignupRequest,
    TokenResponse,
    UserResponse,
)
from app.services.otp_service import (
    generate_otp,
    hash_otp,
    send_otp_email,
    verify_otp_hash,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str = Field(pattern=r"^[0-9]{6}$")


class ResetPasswordOTPRequest(BaseModel):
    email: EmailStr
    otp: str = Field(pattern=r"^[0-9]{6}$")
    new_password: str = Field(min_length=8, max_length=128)


def utc_now_naive():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def get_active_otp(db: Session, user_id: int):
    return (
        db.query(PasswordResetOTP)
        .filter(
            PasswordResetOTP.user_id == user_id,
            PasswordResetOTP.used.is_(False),
        )
        .order_by(PasswordResetOTP.id.desc())
        .first()
    )


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def signup(data: SignupRequest, db: DatabaseSession):
    normalized_email = str(data.email).lower().strip()

    existing_user = (
        db.query(User)
        .filter(User.email == normalized_email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = User(
        name=data.name.strip(),
        email=normalized_email,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: DatabaseSession):
    normalized_email = str(data.email).lower().strip()

    user = (
        db.query(User)
        .filter(User.email == normalized_email)
        .first()
    )

    if (
        user is None
        or not user.is_active
        or not verify_password(data.password, user.hashed_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(access_token=create_access_token(str(user.id)))


@router.get("/me", response_model=UserResponse)
def get_me(current_user: CurrentUser):
    return current_user


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: DatabaseSession):
    response = {
        "message": (
            "If an account exists for that email, "
            "a verification code will be sent."
        )
    }

    email = str(data.email).lower().strip()
    user = db.query(User).filter(User.email == email).first()

    if user is None or not user.is_active:
        return response

    # Invalidate earlier OTPs for this user.
    db.query(PasswordResetOTP).filter(
        PasswordResetOTP.user_id == user.id,
        PasswordResetOTP.used.is_(False),
    ).update({"used": True}, synchronize_session=False)

    otp = generate_otp()
    record = PasswordResetOTP(
        user_id=user.id,
        otp_hash=hash_otp(otp),
        expires_at=(
            utc_now_naive()
            + timedelta(minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES)
        ),
        attempts=0,
        verified=False,
        used=False,
    )

    db.add(record)
    db.commit()

    try:
        send_otp_email(user.email, otp)
    except Exception:
        logger.exception("Unable to send password-reset OTP")
        record.used = True
        db.commit()

    return response


@router.post("/verify-otp")
def verify_password_reset_otp(
    data: VerifyOTPRequest,
    db: DatabaseSession,
):
    email = str(data.email).lower().strip()
    user = db.query(User).filter(User.email == email).first()

    record = (
        get_active_otp(db, user.id)
        if user is not None and user.is_active
        else None
    )

    if record is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification code.",
        )

    if record.expires_at <= utc_now_naive():
        record.used = True
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification code.",
        )

    if record.attempts >= 5:
        record.used = True
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="Too many attempts. Request a new code.",
        )

    record.attempts += 1

    if not verify_otp_hash(data.otp, record.otp_hash):
        if record.attempts >= 5:
            record.used = True
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification code.",
        )

    record.verified = True
    db.commit()

    return {"message": "OTP verified. You can now reset your password."}


@router.post("/reset-password")
def reset_password_otp(
    data: ResetPasswordOTPRequest,
    db: DatabaseSession,
):
    email = str(data.email).lower().strip()
    user = db.query(User).filter(User.email == email).first()

    record = (
        get_active_otp(db, user.id)
        if user is not None and user.is_active
        else None
    )

    if (
        record is None
        or not record.verified
        or record.expires_at <= utc_now_naive()
        or not verify_otp_hash(data.otp, record.otp_hash)
    ):
        raise HTTPException(
            status_code=400,
            detail="Verify a valid OTP before resetting your password.",
        )

    user.hashed_password = hash_password(data.new_password)
    record.used = True

    # Invalidate any other outstanding OTPs.
    db.query(PasswordResetOTP).filter(
        PasswordResetOTP.user_id == user.id,
        PasswordResetOTP.id != record.id,
        PasswordResetOTP.used.is_(False),
    ).update({"used": True}, synchronize_session=False)

    db.commit()

    return {
        "message": "Password reset successfully. You can now sign in."
    }
