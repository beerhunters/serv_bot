import logging
import traceback
from datetime import datetime
from typing import Optional

from aiogram import Router, Bot
from aiogram.handlers import ErrorHandler
from aiogram.types import Update
from fluent.runtime import FluentLocalization

from tgbot.config import ADMIN_URL, FOR_LOGS
import tgbot.keyboards.general_keyboards as kb

from tgbot.tools.fluent_loader import get_fluent_localization

# Настройка логгера
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | [%(filename)s:%(lineno)d] - %(message)s",
    level=logging.ERROR,
    filename="logs/bot_errors.log",
    encoding="utf-8",
)
logger = logging.getLogger(__name__)

error_router = Router()


class ErrorInfo:
    """Класс для хранения информации об ошибке"""

    def __init__(self, exception: Exception, update: Optional[Update] = None):
        self.exception = exception
        self.exception_name = type(exception).__name__
        self.exception_message = str(exception)
        self.error_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.update = update
        self.traceback_info = traceback.format_exc()
        self.traceback_snippet = self._format_traceback()
        self.error_location = self._get_error_location()

    def _get_error_location(self) -> str:
        """Получение точного местоположения ошибки"""
        if not hasattr(self.exception, "__traceback__"):
            return "❓ Неизвестное местоположение"

        tb = traceback.extract_tb(self.exception.__traceback__)
        if not tb:
            return "❓ Неизвестное местоположение"

        last_call = tb[-1]
        filename = last_call.filename
        line = last_call.lineno
        func = last_call.name
        code_line = last_call.line.strip() if last_call.line else "???"
        return (
            f"📂 <b>Файл:</b> {filename}\n"
            f"📌 <b>Строка:</b> {line}\n"
            f"🔹 <b>Функция:</b> {func}\n"
            f"🖥 <b>Код:</b> <pre>{code_line}</pre>"
        )

    def _format_traceback(self, max_length: int = 2000) -> str:
        """Форматирование трейсбека с ограничением длины"""
        tb_lines = self.traceback_info.splitlines()
        snippet = (
            "\n".join(tb_lines[-4:]) if len(tb_lines) >= 4 else self.traceback_info
        )
        if len(snippet) > max_length:
            return snippet[:max_length] + "\n...[сокращено]"
        return snippet

    def get_user_info(self) -> tuple[Optional[int], Optional[str], Optional[str]]:
        """Получение информации о пользователе"""
        if not self.update:
            return None, None, None
        if hasattr(self.update, "message") and self.update.message:
            return (
                self.update.message.from_user.id,
                self.update.message.from_user.full_name,
                self.update.message.text,
            )
        elif hasattr(self.update, "callback_query") and self.update.callback_query:
            return (
                self.update.callback_query.from_user.id,
                self.update.callback_query.from_user.full_name,
                self.update.callback_query.data,
            )
        return None, None, None


@error_router.errors()
class MyHandler(ErrorHandler):
    """Обработчик ошибок в боте"""

    async def handle(self) -> None:
        logger.info("Обработчик ошибок вызван")

        exception = getattr(self.event, "exception", None)
        update = getattr(self.event, "update", None)

        if not exception:
            logger.error("Событие без исключения: %s", self.event)
            return

        error_info = ErrorInfo(exception, update)

        # Логирование ошибки
        logger.error(
            "Ошибка %s: %s\nМестоположение: %s\nTraceback: %s",
            error_info.exception_name,
            error_info.exception_message,
            error_info.error_location.replace("\n", " | "),
            error_info.traceback_snippet,
        )

        # Обработка уведомлений
        await self._handle_notifications(error_info)

    async def _handle_notifications(self, error_info: ErrorInfo) -> None:
        """Управление уведомлениями об ошибке"""
        l10n = await self._get_localization(error_info.update)

        # Уведомление пользователя
        try:
            await self._notify_user(error_info.update, l10n)
        except Exception as e:
            logger.error(
                "Ошибка при уведомлении пользователя: %s\n%s",
                str(e),
                traceback.format_exc(),
            )

        # Уведомление администраторов
        try:
            await self._notify_admins(error_info, l10n)
        except Exception as e:
            logger.error(
                "Ошибка при уведомлении администраторов: %s\n%s",
                str(e),
                traceback.format_exc(),
            )

    async def _get_localization(self, update: Optional[Update]) -> FluentLocalization:
        """Получение локализации для пользователя"""
        try:
            if update and hasattr(update, "message") and update.message:
                return get_fluent_localization(update.message.from_user.language_code)
            elif update and hasattr(update, "callback_query") and update.callback_query:
                return get_fluent_localization(
                    update.callback_query.from_user.language_code
                )
            return get_fluent_localization("en")
        except Exception as e:
            logger.error("Ошибка получения локализации: %s", str(e))
            return get_fluent_localization("en")

    async def _notify_user(
        self, update: Optional[Update], l10n: FluentLocalization
    ) -> None:
        """Отправка сообщения пользователю"""
        if not update:
            logger.warning("Нет update для уведомления пользователя")
            return

        try:
            admin_button = await kb.create_buttons(
                buttons_data=[
                    (l10n.format_value("contact_admin_button"), ADMIN_URL, "url"),
                ],
                back_callback_data="main_menu",
                l10n=l10n,
            )
        except Exception as e:
            logger.error("Не удалось создать кнопки: %s", str(e))
            admin_button = None

        # Проверка наличия ключа в локализации
        try:
            user_message = l10n.format_value("error_text")
        except Exception:
            user_message = "Произошла ошибка!"
            logger.warning(
                "Ключ 'error_text' не найден в локализации, использовано запасное значение"
            )

        try:
            if update.message:
                await update.message.answer(user_message, reply_markup=admin_button)
                logger.info("Сообщение об ошибке отправлено пользователю (Message)")
            elif update.callback_query and update.callback_query.message:
                await update.callback_query.message.answer(
                    user_message, reply_markup=admin_button
                )
                logger.info(
                    "Сообщение об ошибке отправлено пользователю (CallbackQuery)"
                )
            else:
                logger.warning("Неизвестный тип update: %s", type(update))
        except Exception as e:
            logger.error("Ошибка при отправке сообщения пользователю: %s", str(e))

    async def _notify_admins(
        self, error_info: ErrorInfo, l10n: FluentLocalization
    ) -> None:
        """Отправка уведомления администраторам"""
        user_id, user_name, user_message = error_info.get_user_info()

        admin_message = (
            f"⚠️ <b>Ошибка в боте!</b>\n\n"
            f"⏰ <b>Время:</b> {error_info.error_time}\n\n"
            f"👤 <b>Пользователь:</b> {user_name or 'Неизвестно'}\n"
            f"🆔 <b>ID:</b> {user_id or 'Неизвестно'}\n"
            f"💬 <b>Сообщение:</b> {user_message or 'Неизвестно'}\n\n"
            f"❌ <b>Тип ошибки:</b> {error_info.exception_name}\n"
            f"📝 <b>Описание:</b> {error_info.exception_message}\n\n"
            f"📍 <b>Местоположение:</b>\n{error_info.error_location}\n\n"
            f"📚 <b>Трейсбек:</b>\n<pre>{error_info.traceback_snippet}</pre>"
        )

        bot: Bot = self.bot
        try:
            await bot.send_message(
                FOR_LOGS,
                admin_message,
                parse_mode="HTML",
            )
            logger.info("Сообщение отправлено администратору %s", FOR_LOGS)
        except Exception as e:
            logger.error(
                "Не удалось отправить сообщение владельцу %s: %s",
                FOR_LOGS,
                str(e),
            )
