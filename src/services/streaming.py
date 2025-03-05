import asyncio
from httpx import AsyncClient
from fastapi import HTTPException
from starlette.responses import StreamingResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from typing import AsyncGenerator, Dict, Any
from .requests_logger import logger_adapter


async def log_stream_chunk(chunk: bytes, extra: Dict[str, Any] = None) -> None:
    """Async log stream chunks with context"""
    try:
        message = f"Stream chunk: {len(chunk)} bytes"
        if extra:
            message += f" - {str(extra)}"
        await logger_adapter.log_message(message)
    except Exception as e:
        # Log errors but don't break streaming
        print(f"Logging error: {str(e)}")


async def stream_response(url: str, body: object) -> StreamingResponse:
    async def response_generator() -> AsyncGenerator[bytes, None]:
        try:
            async with AsyncClient(timeout=30.0) as client:
                async with client.stream("POST", url, json=body) as response:
                    if response.status_code != 200:
                        raise HTTPException(
                            status_code=response.status_code,
                            detail=f"Error from LLM: {response.text}",
                        )

                    async for chunk in response.aiter_bytes():
                        # Log chunk asynchronously without blocking the stream
                        asyncio.create_task(log_stream_chunk(chunk, {"url": url}))
                        yield chunk

        except HTTPException as http_exc:
            raise http_exc
        except Exception as request_error:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Request failed: {str(request_error)}",
            )

    return StreamingResponse(response_generator())
