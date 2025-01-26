import httpx
from fastapi import APIRouter

from src.services.settings import settings


router = APIRouter(tags=["healthcheck"])


@router.get("/")
async def health_ping():
    client = httpx.AsyncClient()
    response = {
        "backend": "ok",
        "database": "ok",
        "llm_service": await client.get(f"{settings.llm_url}/v1/models"),
        "llm_chat_service": await client.get(f"{settings.llm_url}/v1/models"),
    }
    return response
