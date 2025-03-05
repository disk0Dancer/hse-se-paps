import logging
import asyncio
from datetime import datetime
from typing import Any, Dict, List
from collections import deque
from fastapi import Request
from abc import ABC, abstractmethod


# Abstract target interface
class AsyncLogger(ABC):
    @abstractmethod
    async def log_message(self, message: str) -> None:
        pass

    @abstractmethod
    async def log_batch(self, messages: List[str]) -> None:
        pass


class BatchLogger:
    def __init__(self, name: str, batch_size: int = 100, flush_interval: float = 1.0):
        self.logger = logging.getLogger(name)
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.message_queue: deque = deque()
        self.lock = asyncio.Lock()
        self.last_flush = datetime.now()
        self._flush_task = None

    async def start(self):
        """Start the background flush task"""
        if self._flush_task is None:
            self._flush_task = asyncio.create_task(self._periodic_flush())

    async def stop(self):
        """Stop the background flush task and flush remaining messages"""
        if self._flush_task is not None:
            self._flush_task.cancel()
            await self._flush_messages()

    async def _periodic_flush(self):
        """Periodically flush messages"""
        while True:
            await asyncio.sleep(self.flush_interval)
            await self._flush_messages()

    async def _flush_messages(self):
        """Flush queued messages to the logger"""
        async with self.lock:
            messages = list(self.message_queue)
            self.message_queue.clear()

        if messages:
            self.logger.info("\n".join(messages))

    async def add_message(self, message: str):
        """Add a message to the queue"""
        async with self.lock:
            self.message_queue.append(message)
            if len(self.message_queue) >= self.batch_size:
                await self._flush_messages()


# Adapter Pattern - adapts BatchLogger to AsyncLogger interface
class AsyncLoggerAdapter(AsyncLogger):
    def __init__(self, batch_logger: BatchLogger):
        self.batch_logger = batch_logger

    async def log_message(self, message: str) -> None:
        await self.batch_logger.add_message(message)

    async def log_batch(self, messages: List[str]) -> None:
        for message in messages:
            await self.batch_logger.add_message(message)


_batch_logger = BatchLogger("requests_logger", batch_size=100, flush_interval=1.0)
logger_adapter = AsyncLoggerAdapter(_batch_logger)


# Facade pattern - simplify interface for client code
async def log_request(request: Request, extra: Dict[str, Any] = None) -> None:
    """Facade that simplifies request logging with additional context"""
    message = f"{datetime.now()} - {request.method} {request.url.path}"
    if extra:
        message += f" - {str(extra)}"
    await logger_adapter.log_message(message)


async def start_logger():
    await _batch_logger.start()


async def stop_logger():
    await _batch_logger.stop()
