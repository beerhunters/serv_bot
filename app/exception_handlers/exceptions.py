# import logging
# import traceback
# from aiogram import Router, Bot
# from aiogram.handlers import ErrorHandler
# from aiogram.types import Update
#
# from config import BOT_OWNERS, ADMIN_URL
# import app.general_keyboards as kb
# from tools.fluent_loader import get_fluent_localization
#
# error_router = Router()
#
#
# @error_router.errors()
# class MyHandler(ErrorHandler):
#     async def handle(self) -> None:
#         """Обработчик ошибок в боте"""
#         # Извлекаем имя и сообщение исключения
#         exception_name = type(self.event.exception).__name__
#         exception_message = str(self.event.exception)
#
#         # Извлекаем трассировку ошибки
#         tb_info = traceback.format_exc()
#         tb_lines = tb_info.splitlines()
#
#         # Оставляем только последние 3 строки перед ошибкой + саму ошибку
#         traceback_snippet = "\n".join(tb_lines[-4:]) if len(tb_lines) >= 4 else tb_info
#
#         # Определяем точное место ошибки
#         error_location = "❓ Неизвестное местоположение"
#         if self.event and hasattr(self.event, "exception"):
#             tb = traceback.extract_tb(self.event.exception.__traceback__)
#             if tb:
#                 last_call = tb[-1]  # Берем последнюю запись из стека
#                 filename = last_call.filename
#                 line = last_call.lineno
#                 func = last_call.name
#                 code_line = last_call.line.strip() if last_call.line else "???"
#                 error_location = (
#                     f"📂 <b>Файл:</b> {filename}\n"
#                     f"📌 <b>Строка:</b> {line}\n"
#                     f"🔹 <b>Функция:</b> {func}\n"
#                     f"🖥 <b>Код:</b> <pre>{code_line}</pre>"
#                 )
#
#         # Логирование ошибки
#         logging.error(
#             "Ошибка %s: %s\nМестоположение: %s\nTraceback: %s",
#             exception_name,
#             exception_message,
#             error_location.replace("\n", " | "),
#             traceback_snippet,
#         )
#         # # 🔹 Создаем кнопку "Связаться с Администратором" через ID
#         # admin_button = await kb.create_buttons(
#         #     buttons_data=[("📞 Связаться с Администратором", ADMIN_URL, "url")],
#         #     main_menu=False,  # Отключаем кнопку "Главное меню"
#         # )
#         # Отправляем сообщение пользователю
#         try:
#             update: Update = self.event.update
#             # l10n = get_fluent_localization(update.message.from_user.language_code)
#             # # 🔹 Создаем кнопку "Связаться с Администратором" через ID
#             # admin_button = await kb.create_buttons(
#             #     buttons_data=[
#             #         (l10n.format_value("contact_admin_button"), ADMIN_URL, "url")
#             #     ],
#             #     main_menu=False,  # Отключаем кнопку "Главное меню"
#             # )
#             # user_message = (
#             #     "⚠️ Произошла ошибка!\n\n"
#             #     "Пожалуйста, сделайте скриншот этого сообщения и отправьте его администратору, "
#             #     "описав, что вы делали перед ошибкой.\n\n"
#             #     "Спасибо за помощь в улучшении бота! 😊"
#             # )
#             # user_message = l10n.format_value("error_text")
#             # Проверяем, где есть сообщение, чтобы отправить пользователю
#             if update.message:
#                 l10n = get_fluent_localization(update.message.from_user.language_code)
#                 # 🔹 Создаем кнопку "Связаться с Администратором" через ID
#                 admin_button = await kb.create_buttons(
#                     buttons_data=[
#                         (l10n.format_value("contact_admin_button"), ADMIN_URL, "url")
#                     ],
#                     main_menu=False,  # Отключаем кнопку "Главное меню"
#                 )
#                 user_message = l10n.format_value("error_text")
#                 await update.message.answer(user_message, reply_markup=admin_button)
#                 logging.info("Сообщение об ошибке отправлено пользователю (Message).")
#             elif update.callback_query and update.callback_query.message:
#                 l10n = get_fluent_localization(
#                     update.callback_query.from_user.language_code
#                 )
#                 # 🔹 Создаем кнопку "Связаться с Администратором" через ID
#                 admin_button = await kb.create_buttons(
#                     buttons_data=[
#                         (l10n.format_value("contact_admin_button"), ADMIN_URL, "url")
#                     ],
#                     main_menu=False,  # Отключаем кнопку "Главное меню"
#                 )
#                 user_message = l10n.format_value("error_text")
#                 await update.callback_query.message.answer(
#                     user_message, reply_markup=admin_button
#                 )
#                 logging.info(
#                     "Сообщение об ошибке отправлено пользователю (CallbackQuery)."
#                 )
#             else:
#                 logging.warning(
#                     f"Ошибка произошла в неизвестном типе update: {type(update)}"
#                 )
#
#         except Exception as e:
#             logging.error(f"Не удалось отправить сообщение пользователю: {e}")
#
#         # Отправляем сообщение владельцам бота
#         try:
#             bot: Bot = self.bot
#             for owner in BOT_OWNERS:
#                 await bot.send_message(
#                     owner,
#                     f"⚠️ <b>Ошибка в боте!</b>\n\n"
#                     f"📛 <b>Исключение:</b> {exception_name}\n"
#                     f"📋 <b>Сообщение:</b> {exception_message}\n\n"
#                     f"📍 <b>Местоположение:</b>\n{error_location}\n\n"
#                     f"🖥 <b>Traceback:</b>\n<pre>{traceback_snippet}</pre>",
#                     reply_markup=await kb.create_buttons(l10n=l10n),
#                     # reply_markup=await kb.create_buttons(),
#                 )
#         except Exception as e:
#             logging.error(f"Не удалось отправить сообщение владельцу: {e}")
import logging
import traceback
from aiogram import Router, Bot
from aiogram.handlers import ErrorHandler
from aiogram.types import Update

from config import BOT_OWNERS, ADMIN_URL
import app.general_keyboards as kb
from tools.fluent_loader import get_fluent_localization

error_router = Router()


@error_router.errors()
class MyHandler(ErrorHandler):
    async def handle(self) -> None:
        """Обработчик ошибок в боте"""

        # Извлекаем имя и сообщение исключения
        exception_name = "Неизвестное исключение"
        exception_message = "Неизвестная ошибка"
        if self.event and hasattr(self.event, "exception"):
            exception = self.event.exception
            exception_name = type(exception).__name__
            exception_message = str(exception)

        # Извлекаем трассировку ошибки
        tb_info = traceback.format_exc()
        tb_lines = tb_info.splitlines()

        # Оставляем только последние 3 строки перед ошибкой + саму ошибку
        traceback_snippet = "\n".join(tb_lines[-4:]) if len(tb_lines) >= 4 else tb_info

        # Определяем точное место ошибки
        error_location = "❓ Неизвестное местоположение"
        if self.event and hasattr(self.event, "exception"):
            tb = traceback.extract_tb(self.event.exception.__traceback__)
            if tb:
                last_call = tb[-1]  # Берем последнюю запись из стека
                filename = last_call.filename
                line = last_call.lineno
                func = last_call.name
                code_line = last_call.line.strip() if last_call.line else "???"
                error_location = (
                    f"📂 <b>Файл:</b> {filename}\n"
                    f"📌 <b>Строка:</b> {line}\n"
                    f"🔹 <b>Функция:</b> {func}\n"
                    f"🖥 <b>Код:</b> <pre>{code_line}</pre>"
                )

        # Логирование ошибки
        logging.error(
            "Ошибка %s: %s\nМестоположение: %s\nTraceback: %s",
            exception_name,
            exception_message,
            error_location.replace("\n", " | "),
            traceback_snippet,
        )

        # Отправка сообщения пользователю
        try:
            update: Update = self.event.update
            l10n = (
                get_fluent_localization(update.message.from_user.language_code)
                if hasattr(update, "message")
                else None
            )
            if not l10n:
                l10n = get_fluent_localization("en")  # или другой fallback

            admin_button = None
            try:
                # Создаем кнопку "Связаться с Администратором"
                admin_button = await kb.create_buttons(
                    buttons_data=[
                        (l10n.format_value("contact_admin_button"), ADMIN_URL, "url")
                    ],
                    main_menu=False,  # Отключаем кнопку "Главное меню"
                )
            except Exception as e:
                logging.error(f"Не удалось создать кнопки: {str(e)}")

            user_message = (
                l10n.format_value("error_text") if l10n else "Произошла ошибка!"
            )

            if update.message:
                await update.message.answer(user_message, reply_markup=admin_button)
                logging.info("Сообщение об ошибке отправлено пользователю (Message).")
            elif update.callback_query and update.callback_query.message:
                await update.callback_query.message.answer(
                    user_message, reply_markup=admin_button
                )
                logging.info(
                    "Сообщение об ошибке отправлено пользователю (CallbackQuery)."
                )
            else:
                logging.warning(
                    f"Ошибка произошла в неизвестном типе update: {type(update)}"
                )

        except Exception as e:
            logging.error(f"Ошибка при отправке сообщения пользователю: {str(e)}")

        # Отправляем сообщение владельцам бота
        try:
            bot: Bot = self.bot
            for owner in BOT_OWNERS:
                await bot.send_message(
                    owner,
                    f"⚠️ <b>Ошибка в боте!</b>\n\n"
                    f"📛 <b>Исключение:</b> {exception_name}\n"
                    f"📋 <b>Сообщение:</b> {exception_message}\n\n"
                    f"📍 <b>Местоположение:</b>\n{error_location}\n\n"
                    f"🖥 <b>Traceback:</b>\n<pre>{traceback_snippet}</pre>",
                    reply_markup=await kb.create_buttons(l10n=l10n),
                )
        except Exception as e:
            logging.error(f"Не удалось отправить сообщение владельцу: {e}")
