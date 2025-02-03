import logging
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Update


class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data):
        # logging.info(f"Получено обновление: {event}")
        return await handler(event, data)
