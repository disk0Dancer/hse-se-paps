import httpx
from fastapi import APIRouter

from src.services.settings import settings


router = APIRouter(tags=["healthcheck"])


@router.get("/")
async def health_ping():
    client = httpx.AsyncClient()
    
    llm_service_response = await client.get(f"{settings.llm_url}/v1/models")
    llm_chat_service_response = await client.get(f"{settings.llm_chat_url}/v1/models")
    
    response = {
        "backend": "ok",
        "database": "ok", #TODO: add database healthcheck
        "llm_service": "ok" if llm_service_response.status_code == 200 else "failed",
        "llm_chat_service": "ok" if llm_chat_service_response.status_code == 200 else "failed",
    }
    return response
