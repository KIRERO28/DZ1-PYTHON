from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_chat_usecase, get_current_user_id
from app.core.errors import ExternalServiceError
from app.schemas.chat import (
    ChatHistoryResponse,
    ChatRequest,
    ChatResponse,
    ClearHistoryResponse,
)
from app.usecases.chat import ChatUseCase

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def ask_chat(
    payload: ChatRequest,
    user_id: Annotated[int, Depends(get_current_user_id)],
    usecase: Annotated[ChatUseCase, Depends(get_chat_usecase)],
) -> ChatResponse:
    try:
        answer = await usecase.ask(
            user_id=user_id,
            prompt=payload.prompt,
            system=payload.system,
            max_history=payload.max_history,
            temperature=payload.temperature,
        )
        return ChatResponse(answer=answer)
    except ExternalServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.get("/history", response_model=ChatHistoryResponse)
async def get_history(
    user_id: Annotated[int, Depends(get_current_user_id)],
    usecase: Annotated[ChatUseCase, Depends(get_chat_usecase)],
    limit: int = Query(default=50, ge=1, le=200),
) -> ChatHistoryResponse:
    items = await usecase.get_history(user_id=user_id, limit=limit)
    return ChatHistoryResponse(items=items)


@router.delete("/history", response_model=ClearHistoryResponse)
async def clear_history(
    user_id: Annotated[int, Depends(get_current_user_id)],
    usecase: Annotated[ChatUseCase, Depends(get_chat_usecase)],
) -> ClearHistoryResponse:
    await usecase.clear_history(user_id=user_id)
    return ClearHistoryResponse(status="ok")
