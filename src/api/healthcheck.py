import httpx
from fastapi import APIRouter

from src.services.settings import settings

router = APIRouter(tags=["healthcheck"])


@router.get("/health")
async def health_check(request):
    """Check health of all dependent services"""
    health_status = {"llm_service": False, "llm_chat_service": False, "logging": True}

    async with httpx.AsyncClient() as client:
        try:
            llm_resp = await client.get(f"{settings.llm_url}/v1/models")
            health_status["llm_service"] = llm_resp.status_code == 200
        except Exception:
            health_status["llm_service"] = False

        try:
            chat_resp = await client.get(f"{settings.llm_chat_url}/v1/models")
            health_status["llm_chat_service"] = chat_resp.status_code == 200
        except Exception:
            health_status["llm_chat_service"] = False

    return health_status
