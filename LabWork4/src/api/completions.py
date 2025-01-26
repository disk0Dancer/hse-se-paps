import os
import httpx
from fastapi import APIRouter, Depends, Body

from src.services import stream_response
from src.services import settings

router = APIRouter()


@router.post("/completions")
async def completions(body=Body(...)):
    url = f"{settings.llm_chat_url}/v1/completions"

    if "stream" in body and body["stream"]:
        return await stream_response(url, body)
    else:
        async with httpx.AsyncClient() as client:
            return (await client.post(url, json=body)).json()
