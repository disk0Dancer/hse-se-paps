import os
import httpx
from fastapi import APIRouter, Depends, Body

from src.services.auth import get_current_user
from src.services.streaming import stream_response
from src.settings import settings

router = APIRouter()


@router.post("/completions")
async def completions(body=Body(...)):
    if "stream" in body and body["stream"]:
        return await stream_response(settings.llm_url, body)
    else:
        async with httpx.AsyncClient() as client:
            return (await client.post(settings.llm_url, json=body)).json()
