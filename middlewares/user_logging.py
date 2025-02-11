import logging
import traceback
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Update

# ---- Кастомный логгер ----


class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;21m"
    green = "\x1b[32;1m"
    yellow = "\x1b[33;1m"
    red = "\x1b[31;1m"
    bold_red = "\x1b[41m"
    reset = "\x1b[0m"
    format = "%(asctime)s | %(levelname)s | [%(filename)s:%(lineno)d] - %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.format)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        record.levelname = record.levelname.ljust(8)
        return formatter.format(record)


# ---- Настройка логгера ----

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(CustomFormatter())

logger = logging.getLogger("bot_logger")

if not logger.handlers:
    logger.addHandler(handler)

logger.setLevel(logging.DEBUG)
logger.propagate = False

# Убираем логи aiogram про Update id=...
logging.getLogger("aiogram.event").setLevel(logging.WARNING)


# ---- Middleware с улучшенным логированием ----


class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data):
        try:
            # Определяем стек вызова, но исключаем middleware
            stack = traceback.extract_stack()
            for frame in reversed(stack):
                if (
                    "middlewares" not in frame.filename
                ):  # Берем первый вызов не из middleware
                    file_name = frame.filename.split("/")[-1]
                    line_number = frame.lineno
                    break
            else:
                file_name, line_number = "unknown", 0  # На случай ошибки

            # Определяем тип события
            event_type = event.event_type if hasattr(event, "event_type") else "unknown"

            # Формируем лог-сообщение
            log_message = (
                f"📌 EVENT | {event_type.upper()} | [{file_name}:{line_number}]"
            )

            # Логируем текст сообщений
            if event.message:
                log_message += f" | User ID: {event.message.from_user.id} | Text: {event.message.text}"
            elif event.callback_query:
                log_message += f" | User ID: {event.callback_query.from_user.id} | Callback: {event.callback_query.data}"

            logger.info(log_message)

            return await handler(event, data)

        except Exception as e:
            logger.error(f"Logging error: {e}", exc_info=True)
            return await handler(event, data)
