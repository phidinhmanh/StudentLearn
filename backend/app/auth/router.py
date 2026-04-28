from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
import uuid
from app.models.schemas import UserRegister, UserLogin, Token
from app.auth.service import hash_password, verify_password, create_access_token
from app.services.factory import get_graph_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token)
async def register(data: UserRegister):
    """Register a new user"""
    try:
        service = get_graph_service()
        if not await service.is_connected():
            raise RuntimeError("Database not connected")
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Database connection failed. Please try again later."},
        )

    # Check if email exists
    try:
        existing = await service.get_user_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Create user
        user_id = str(uuid.uuid4())
        hashed = hash_password(data.password)
        await service.create_user(user_id, data.email, data.name, hashed)

        # Return token
        token = create_access_token({"sub": user_id, "email": data.email})
        return Token(access_token=token)
    except HTTPException:
        raise
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Database connection failed. Please try again later."},
        )


@router.post("/login", response_model=Token)
async def login(data: UserLogin):
    """Login and get access token"""
    try:
        service = get_graph_service()
        if not await service.is_connected():
            raise RuntimeError("Database not connected")
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Database connection failed. Please try again later."},
        )

    try:
        # Get user
        user = await service.get_user_by_email(data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Verify password
        if not verify_password(data.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Return token
        token = create_access_token({"sub": user["id"], "email": user["email"]})
        return Token(access_token=token)
    except HTTPException:
        raise
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Database connection failed. Please try again later."},
        )