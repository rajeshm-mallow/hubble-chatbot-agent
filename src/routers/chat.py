from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException

from src.agent.agent_service import OrderManagementAgentService
from src.config import settings
from src.context.dependencies import get_request_context
from src.context.request_context import RequestContext
from src.models.pydantic import ChatRequest
from src.sensitive_data_handler.data_handler_service import (
    SensitiveDataUnMaskingService,
)

router = APIRouter()


@router.post("/chat")
async def chat_endpoint(
    chat_request: ChatRequest,
    background_tasks: BackgroundTasks,
    authorization: str | None = Header(None),
    context: RequestContext = Depends(get_request_context),
    session_uuid: Annotated[str | None, Header(alias="X-Chat-Session-Id")] = None,
) -> dict:
    """
    Chat endpoint for order management operations.

    Args:
        request: Chat request containing query and session information
        authorization: Optional authorization header with Bearer token

    Returns:
        Dictionary containing the agent's response message
    """
    if session_uuid is None:
        raise HTTPException(status_code=400, detail="Missing X-Chat-Session-Id header")

    agent_service = OrderManagementAgentService(session_uuid)

    token = authorization.split(" ", 1)[1] if authorization else ""

    response = await agent_service.process_chat_request(
        session_uuid, chat_request.query, context, token
    )

    message = response.message.get("content", [{}])[0].get("text", "")

    for placeholder, original in context.sensitive_key_value.items():
        message = message.replace(placeholder, original)

    data_cache = settings.SENSITIVE_DATA_HANDLER.DATA_CACHE

    unmasked_message = await SensitiveDataUnMaskingService(data_cache).process_data(
        message, session_uuid, context.sensitive_key_value
    )

    if context.sensitive_key_value:
        background_tasks.add_task(
            settings.SENSITIVE_DATA_HANDLER.DATA_CACHE.set_many_under,
            session_uuid,
            context.sensitive_key_value,
        )

    return {"message": unmasked_message}
