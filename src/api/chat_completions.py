import httpx
from fastapi import APIRouter, Body, Depends, Request

from src.models.user import User
from src.services.auth import AuthService
from src.services.streaming import stream_response
from src.services.settings import settings
from src.services.requests_logger import log_request

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/completions")
async def create_chat_completion(
    request: Request,
    request_data: dict = Body(...),
    current_user: User = Depends(AuthService.get_current_user),
):
    """Handle chat completion requests for interactive coding assistance"""
    url = f"{settings.llm_chat_url}/v1/chat/completions"
    await log_request(
        request, extra={"user": current_user.login, "request_type": "chat_completion"}
    )

    if "stream" in request_data and request_data["stream"]:
        return await stream_response(url, request_data)
    else:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=request_data)
            return response.json()
