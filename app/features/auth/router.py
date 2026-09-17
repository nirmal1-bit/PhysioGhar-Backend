from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.features.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.features.auth.service import (
    AuthService,
    InactiveAccountError,
    InvalidCredentialsError,
    RegistrationConflictError,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(request: RegisterRequest) -> UserResponse:
    try:
        therapist = await AuthService().register(request)
    except RegistrationConflictError as error:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(error)},
        )
    return UserResponse.model_validate(therapist)


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest) -> TokenResponse:
    try:
        token = await AuthService().login(request)
    except InvalidCredentialsError as error:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(error)},
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InactiveAccountError as error:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": str(error)},
        )
    access_token, user_type = token
    return TokenResponse(access_token=access_token, user_type=user_type)
