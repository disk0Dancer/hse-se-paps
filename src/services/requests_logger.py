import logging
from datetime import datetime
from fastapi import Request

logger = logging.getLogger("requests_logger")


def log_request(request: Request):
    logger.info(f"{datetime.now()} - {request.method} {request.url.path}")
