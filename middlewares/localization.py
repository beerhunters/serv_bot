from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from tools.fluent_loader import get_fluent_localization


class L10nMiddleware(BaseMiddleware):
    def __init__(self, default_locale: str = "ru"):
        self.default_locale = default_locale

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        # Получаем язык пользователя или используем язык по умолчанию
        language_code = (
            getattr(event.from_user, "language_code", None) or self.default_locale
        )

        try:
            # Загружаем локализацию
            l10n = get_fluent_localization(language_code[:2])
            data["l10n"] = l10n
        except FileNotFoundError:
            # Если файл локализации не найден, используем язык по умолчанию
            data["l10n"] = get_fluent_localization(self.default_locale)

        return await handler(event, data)
