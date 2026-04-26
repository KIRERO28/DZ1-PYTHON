from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import UnauthorizedError
from app.core.security import decode_access_token
from app.db.session import AsyncSessionLocal
from app.repositories.chat_messages import ChatMessagesRepository
from app.repositories.users import UsersRepository
from app.services.openrouter_client import OpenRouterClient
from app.usecases.auth import AuthUseCase
from app.usecases.chat import ChatUseCase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


def get_users_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UsersRepository:
    return UsersRepository(session)


def get_chat_messages_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ChatMessagesRepository:
    return ChatMessagesRepository(session)


def get_auth_usecase(
    users_repository: Annotated[UsersRepository, Depends(get_users_repository)],
) -> AuthUseCase:
    return AuthUseCase(users_repository)


def get_chat_usecase(
    messages_repository: Annotated[
        ChatMessagesRepository, Depends(get_chat_messages_repository)
    ],
) -> ChatUseCase:
    return ChatUseCase(messages_repository, OpenRouterClient())


def get_current_user_id(token: Annotated[str, Depends(oauth2_scheme)]) -> int:
    try:
        payload = decode_access_token(token)
        user_id_raw = payload.get("sub")
        if user_id_raw is None:
            raise UnauthorizedError("Missing subject in token")
        return int(user_id_raw)
    except (UnauthorizedError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
