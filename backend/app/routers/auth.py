# Authentication router for FlatWatch
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..auth import (
    Token,
    LoginRequest,
    SignupRequest,
    User,
    create_access_token,
    authenticate_user,
    create_user,
    get_current_user,
)
from ..audit import AuditAction, log_action

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post("/login", response_model=Token)
async def login(request: LoginRequest, req: Request):
    """
    Login endpoint (POC mock).
    In production, this will verify Firebase ID tokens.
    """
    user = authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "id": user.id}
    )

    # Audit log
    log_action(
        AuditAction.LOGIN,
        user.id,
        f"User logged in: {user.email}",
        ip_address=req.client.host if req.client else None,
    )

    return Token(access_token=access_token, user=user)


@router.post("/signup", response_model=Token)
async def signup(request: SignupRequest, req: Request):
    """
    Signup endpoint (POC mock).
    In production, this will create Firebase user.
    """
    # Check if user exists
    from ..auth import MOCK_USERS
    if request.email in MOCK_USERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )

    user = create_user(request.email, request.name, request.flat_number)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "id": user.id}
    )

    # Audit log
    log_action(
        AuditAction.SIGNUP,
        user.id,
        f"New user signed up: {user.email}",
        ip_address=req.client.host if req.client else None,
    )

    return Token(access_token=access_token, user=user)


@router.get("/me", response_model=User)
async def get_me(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from token."""
    user = get_current_user(credentials.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return user


@router.post("/verify")
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify Firebase token (POC stub).
    In production, this will call Firebase Admin SDK.
    """
    user = get_current_user(credentials.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return {"valid": True, "user": user}
