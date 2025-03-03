# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
# from datetime import datetime, timedelta
#
#
# class CustomMonthCalendar:
#     """Класс для создания и управления инлайн-календарем с поддержкой переключения между годами и выбором месяцев."""
#
#     def __init__(self):
#         # Поддерживаемые языки: Русский и Английский
#         self.locales = {
#             "ru": {
#                 "months": ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
#                            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
#             },
#             "en": {
#                 "months": ["January", "February", "March", "April", "May", "June",
#                            "July", "August", "September", "October", "November", "December"]
#             }
#         }
#
#     async def generate_month_calendar(self, year: int, back_callback: str, locale: str = "ru") -> InlineKeyboardMarkup:
#         """
#         Создает инлайн-календарь с кнопками месяцев для выбранного года.
#
#         :param year: Год
#         :param back_callback: Колбэк для кнопки назад
#         :param locale: Локаль для отображения (например, "en" или "ru")
#         :return: Объект InlineKeyboardMarkup с календарем
#         """
#         keyboard = InlineKeyboardMarkup(inline_keyboard=[])
#         localization = self.locales.get(locale, self.locales["en"])  # Получаем локализацию или используем английскую по умолчанию
#
#         # Кнопки для переключения года
#         keyboard.inline_keyboard.append([
#             InlineKeyboardButton(text="<<", callback_data=f"calendar:prev_year:{year}"),
#             InlineKeyboardButton(text=f"{year}", callback_data="ignore"),
#             InlineKeyboardButton(text=">>", callback_data=f"calendar:next_year:{year}")
#         ])
#
#         # Кнопки для месяцев (по 4 в ряд)
#         month_buttons = []
#         for month_index, month_name in enumerate(localization["months"], start=1):
#             month_buttons.append(InlineKeyboardButton(
#                 text=month_name,
#                 callback_data=f"calendar:select_month:{year}:{month_index}"
#             ))
#
#         # Разделение на ряды по 4 месяца
#         for i in range(0, len(month_buttons), 4):
#             keyboard.inline_keyboard.append(month_buttons[i:i + 4])
#
#         # Кнопка "Назад"
#         keyboard.inline_keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data=back_callback)])
#
#         return keyboard
#
#     async def handle_callback(self, callback: CallbackQuery, back_callback: str, locale: str = "ru"):
#         """
#         Обработчик колбэков для календаря.
#
#         :param callback: CallbackQuery объект
#         :param back_callback: Колбэк для кнопки назад
#         :param locale: Локаль для отображения (например, "en" или "ru")
#         """
#         data = callback.data.split(":")
#         action = data[1]
#
#         current_year = int(data[2])
#
#         if action == "prev_year":
#             current_year -= 1
#         elif action == "next_year":
#             current_year += 1
#         elif action == "select_month":
#             selected_month = int(data[3])
#             # Определяем начало и конец выбранного месяца
#             first_day_of_month = datetime(current_year, selected_month, 1)
#             last_day_of_month = (datetime(current_year, selected_month + 1, 1) - timedelta(days=1)) if selected_month !=12 else datetime(current_year, 12, 31)
#
#             # await callback.message.edit_text(f"Вы выбрали период: {first_day_of_month.strftime('%d.%m.%Y')} - {last_day_of_month.strftime('%d.%m.%Y')}")
#             return first_day_of_month, last_day_of_month  # Возвращаем начало и конец месяца
#         # else:
#         #     pass
#
#         # Обновляем календарь
#         await callback.message.edit_reply_markup(
#             reply_markup=await self.generate_month_calendar(
#                 current_year, back_callback, locale
#             )
#         )
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
# from datetime import datetime, timedelta
#
#
# class CustomMonthCalendar:
#     """Класс для создания и управления инлайн-календарем с поддержкой переключения между годами и выбором месяцев."""
#
#     def __init__(self):
#         # Поддерживаемые языки: Русский и Английский
#         self.locales = {
#             "ru": {
#                 "months": ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
#                            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
#             },
#             "en": {
#                 "months": ["January", "February", "March", "April", "May", "June",
#                            "July", "August", "September", "October", "November", "December"]
#             }
#         }
#
#     async def generate_month_calendar(self, year: int, back_callback: str, locale: str = "ru") -> InlineKeyboardMarkup:
#         """
#         Создает инлайн-календарь с кнопками месяцев для выбранного года.
#
#         :param year: Год
#         :param back_callback: Колбэк для кнопки назад
#         :param locale: Локаль для отображения (например, "en" или "ru")
#         :return: Объект InlineKeyboardMarkup с календарем
#         """
#         keyboard = InlineKeyboardMarkup(inline_keyboard=[])
#         localization = self.locales.get(locale, self.locales["en"])  # Получаем локализацию или используем английскую по умолчанию
#
#         # Кнопки для переключения года
#         keyboard.inline_keyboard.append([
#             InlineKeyboardButton(text="<<", callback_data=f"calendar:prev_year:{year}"),
#             InlineKeyboardButton(text=f"{year}", callback_data="ignore"),
#             InlineKeyboardButton(text=">>", callback_data=f"calendar:next_year:{year}")
#         ])
#
#         # Кнопки для месяцев (по 4 в ряд)
#         month_buttons = []
#         for month_index, month_name in enumerate(localization["months"], start=1):
#             month_buttons.append(InlineKeyboardButton(
#                 text=month_name,
#                 callback_data=f"calendar:select_month:{year}:{month_index}"
#             ))
#
#         # Разделение на ряды по 4 месяца
#         for i in range(0, len(month_buttons), 4):
#             keyboard.inline_keyboard.append(month_buttons[i:i + 4])
#
#         # Кнопка "Назад"
#         keyboard.inline_keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data=back_callback)])
#
#         return keyboard
#
#     async def handle_callback(self, callback: CallbackQuery, back_callback: str, locale: str = "ru"):
#         """
#         Обработчик колбэков для календаря.
#
#         :param callback: CallbackQuery объект
#         :param back_callback: Колбэк для кнопки назад
#         :param locale: Локаль для отображения (например, "en" или "ru")
#         """
#         data = callback.data.split(":")
#         action = data[1]
#
#         current_year = int(data[2])
#
#         if action == "prev_year":
#             current_year -= 1
#         elif action == "next_year":
#             current_year += 1
#         elif action == "select_month":
#             selected_month = int(data[3])
#             # Определяем начало и конец выбранного месяца
#             first_day_of_month = datetime(current_year, selected_month, 1)
#             last_day_of_month = (datetime(current_year, selected_month + 1, 1) - timedelta(days=1)) if selected_month !=12 else datetime(current_year, 12, 31)
#
#             # await callback.message.edit_text(f"Вы выбрали период: {first_day_of_month.strftime('%d.%m.%Y')} - {last_day_of_month.strftime('%d.%m.%Y')}")
#             return first_day_of_month, last_day_of_month  # Возвращаем начало и конец месяца
#         # else:
#         #     pass
#
#         # Обновляем календарь
#         await callback.message.edit_reply_markup(
#             reply_markup=await self.generate_month_calendar(
#                 current_year, back_callback, locale
#             )
#         )
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from fluent.runtime import FluentLocalization

logger = logging.getLogger(__name__)


class CustomMonthCalendar:
    """Класс для создания и управления инлайн-календарём с выбором месяцев и переключением годов."""

    def __init__(self, l10n: FluentLocalization = None):
        """
        Инициализация календаря с поддержкой локализации.

        Args:
            l10n: Объект FluentLocalization для динамической локализации (опционально).
        """
        self.l10n = l10n
        self.locales = {
            "ru": {
                "months": [
                    "Январь",
                    "Февраль",
                    "Март",
                    "Апрель",
                    "Май",
                    "Июнь",
                    "Июль",
                    "Август",
                    "Сентябрь",
                    "Октябрь",
                    "Ноябрь",
                    "Декабрь",
                ],
                "back_button": "◀️ Назад",
            },
            "en": {
                "months": [
                    "January",
                    "February",
                    "March",
                    "April",
                    "May",
                    "June",
                    "July",
                    "August",
                    "September",
                    "October",
                    "November",
                    "December",
                ],
                "back_button": "◀️ Back",
            },
        }

    async def generate_month_calendar(
        self,
        year: int,
        back_callback: str,
        locale: str = "ru",
        l10n: FluentLocalization = None,
    ) -> InlineKeyboardMarkup:
        """
        Создаёт инлайн-календарь с кнопками месяцев для выбранного года.

        Args:
            year: Год календаря.
            back_callback: Callback_data для кнопки "Назад".
            locale: Код языка ("ru" или "en"), используется если l10n не передан.
            l10n: Объект FluentLocalization для динамической локализации (опционально).

        Returns:
            InlineKeyboardMarkup: Клавиатура с календарём.

        Raises:
            ValueError: Если год некорректен.
        """
        try:
            logger.debug("Генерация календаря месяцев для года %d", year)
            if year < 1970 or year > 9999:  # Ограничение для datetime
                raise ValueError(f"Некорректный год: {year}")

            localization = self.locales.get(locale, self.locales["en"])
            l10n = l10n or self.l10n

            keyboard = InlineKeyboardMarkup(inline_keyboard=[])
            keyboard.inline_keyboard.append(
                [
                    InlineKeyboardButton(
                        text="<<", callback_data=f"calendar:prev_year:{year}"
                    ),
                    InlineKeyboardButton(text=f"{year}", callback_data="ignore"),
                    InlineKeyboardButton(
                        text=">>", callback_data=f"calendar:next_year:{year}"
                    ),
                ]
            )

            month_buttons = [
                InlineKeyboardButton(
                    text=month_name,
                    callback_data=f"calendar:select_month:{year}:{month_index}",
                )
                for month_index, month_name in enumerate(
                    localization["months"], start=1
                )
            ]

            for i in range(0, len(month_buttons), 4):
                keyboard.inline_keyboard.append(month_buttons[i : i + 4])

            back_text = (
                l10n.format_value("btn_back") if l10n else localization["back_button"]
            )
            keyboard.inline_keyboard.append(
                [InlineKeyboardButton(text=back_text, callback_data=back_callback)]
            )

            logger.debug("Календарь месяцев для %d сгенерирован", year)
            return keyboard
        except ValueError as e:
            logger.error("Ошибка валидации года: %s", str(e))
            raise
        except Exception as e:
            logger.error("Ошибка генерации календаря месяцев: %s", str(e))
            return InlineKeyboardMarkup(inline_keyboard=[])

    async def handle_callback(
        self,
        callback: CallbackQuery,
        back_callback: str,
        locale: str = "ru",
        l10n: FluentLocalization = None,
    ) -> Optional[Tuple[datetime, datetime]]:
        """
        Обрабатывает действия пользователя в календаре.

        Args:
            callback: Объект CallbackQuery с данными от пользователя.
            back_callback: Callback_data для кнопки "Назад".
            locale: Код языка ("ru" или "en"), используется если l10n не передан.
            l10n: Объект FluentLocalization для динамической локализации (опционально).

        Returns:
            Optional[Tuple[datetime, datetime]]: Кортеж с началом и концом месяца или None.
        """
        try:
            logger.debug("Начало обработки callback: %s", callback.data)
            await callback.answer()  # Подтверждаем callback сразу
            data = callback.data.split(":")
            if len(data) < 3:
                logger.warning("Некорректный формат callback_data: %s", callback.data)
                await callback.answer("Ошибка формата данных.", show_alert=True)
                return None

            action = data[1]
            current_year = int(data[2])
            logger.debug("Текущий год: %d, действие: %s", current_year, action)

            if action == "prev_year":
                current_year -= 1
            elif action == "next_year":
                current_year += 1
            elif action == "select_month":
                selected_month = int(data[3])
                first_day_of_month = datetime(current_year, selected_month, 1)
                last_day_of_month = (
                    datetime(current_year, selected_month + 1, 1) - timedelta(days=1)
                    if selected_month != 12
                    else datetime(current_year, 12, 31)
                )
                logger.debug(
                    "Выбран период: %s - %s", first_day_of_month, last_day_of_month
                )
                return first_day_of_month, last_day_of_month
            else:
                logger.debug("Игнорируемое действие: %s", action)
                return None

            # Обновляем календарь
            new_keyboard = await self.generate_month_calendar(
                current_year, back_callback, locale, l10n
            )
            await callback.message.edit_reply_markup(reply_markup=new_keyboard)
            logger.debug("Календарь обновлён для года %d", current_year)
            return None
        except ValueError as e:
            logger.error("Ошибка обработки callback_data: %s", str(e))
            await callback.answer("Некорректные данные.", show_alert=True)
            return None
        except TelegramBadRequest as e:
            logger.error("Ошибка Telegram API при обновлении клавиатуры: %s", str(e))
            await callback.answer("Не удалось обновить календарь.", show_alert=True)
            return None
        except Exception as e:
            logger.error("Неизвестная ошибка обработки callback: %s", str(e))
            await callback.answer("Ошибка календаря.", show_alert=True)
            return None
