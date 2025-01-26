from httpx import AsyncClient
from fastapi import HTTPException
from starlette.responses import StreamingResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR


async def stream_response(url: str, body: object):
    async def _iter():
        try:
            async with AsyncClient(timeout=30) as client:
                async with client.stream("POST", url, json=body) as response:
                    if response.status_code != 200:
                        raise HTTPException(
                            status_code=response.status_code,
                            detail=f"Error from LLM: {response.text}",
                        )
                    async for chunk in response.aiter_bytes():
                        yield chunk

        except HTTPException as http_exc:
            raise http_exc

        except Exception as request_error:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Request failed: {str(request_error)}",
            )

    return StreamingResponse(_iter())
