import httpx
from fastapi import APIRouter, Body, Depends, Request

from src.models.user import User
from src.services.auth import AuthService
from src.services.streaming import stream_response
from src.services.settings import settings

router = APIRouter()


@router.post("/completions")
async def create_completion(
    request: Request,
    request_data: dict = Body(...),
    current_user: User = Depends(AuthService.get_current_user),
):
    """Handle code completion requests with async logging"""
    url = f"{settings.llm_url}/v1/completions"

    if "stream" in request_data and request_data["stream"]:
        return await stream_response(url, request_data)
    else:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=request_data)
            return response.json()
