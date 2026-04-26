from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_auth_usecase, get_current_user_id
from app.core.errors import ConflictError, NotFoundError, UnauthorizedError
from app.schemas.auth import RegisterRequest, TokenResponse
from app.schemas.user import UserPublic
from app.usecases.auth import AuthUseCase

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    usecase: Annotated[AuthUseCase, Depends(get_auth_usecase)],
) -> UserPublic:
    try:
        user = await usecase.register(payload.email, payload.password)
        return UserPublic.model_validate(user)
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    usecase: Annotated[AuthUseCase, Depends(get_auth_usecase)],
) -> TokenResponse:
    try:
        access_token = await usecase.login(form_data.username, form_data.password)
        return TokenResponse(access_token=access_token)
    except UnauthorizedError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


@router.get("/me", response_model=UserPublic)
async def me(
    user_id: Annotated[int, Depends(get_current_user_id)],
    usecase: Annotated[AuthUseCase, Depends(get_auth_usecase)],
) -> UserPublic:
    try:
        user = await usecase.get_profile(user_id)
        return UserPublic.model_validate(user)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
