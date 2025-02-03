from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime, timedelta


class CustomMonthCalendar:
    """Класс для создания и управления инлайн-календарем с поддержкой переключения между годами и выбором месяцев."""

    def __init__(self):
        # Поддерживаемые языки: Русский и Английский
        self.locales = {
            "ru": {
                "months": ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                           "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
            },
            "en": {
                "months": ["January", "February", "March", "April", "May", "June",
                           "July", "August", "September", "October", "November", "December"]
            }
        }

    async def generate_month_calendar(self, year: int, back_callback: str, locale: str = "ru") -> InlineKeyboardMarkup:
        """
        Создает инлайн-календарь с кнопками месяцев для выбранного года.

        :param year: Год
        :param back_callback: Колбэк для кнопки назад
        :param locale: Локаль для отображения (например, "en" или "ru")
        :return: Объект InlineKeyboardMarkup с календарем
        """
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        localization = self.locales.get(locale, self.locales["en"])  # Получаем локализацию или используем английскую по умолчанию

        # Кнопки для переключения года
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text="<<", callback_data=f"calendar:prev_year:{year}"),
            InlineKeyboardButton(text=f"{year}", callback_data="ignore"),
            InlineKeyboardButton(text=">>", callback_data=f"calendar:next_year:{year}")
        ])

        # Кнопки для месяцев (по 4 в ряд)
        month_buttons = []
        for month_index, month_name in enumerate(localization["months"], start=1):
            month_buttons.append(InlineKeyboardButton(
                text=month_name,
                callback_data=f"calendar:select_month:{year}:{month_index}"
            ))

        # Разделение на ряды по 4 месяца
        for i in range(0, len(month_buttons), 4):
            keyboard.inline_keyboard.append(month_buttons[i:i + 4])

        # Кнопка "Назад"
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data=back_callback)])

        return keyboard

    async def handle_callback(self, callback: CallbackQuery, back_callback: str, locale: str = "ru"):
        """
        Обработчик колбэков для календаря.

        :param callback: CallbackQuery объект
        :param back_callback: Колбэк для кнопки назад
        :param locale: Локаль для отображения (например, "en" или "ru")
        """
        data = callback.data.split(":")
        action = data[1]

        current_year = int(data[2])

        if action == "prev_year":
            current_year -= 1
        elif action == "next_year":
            current_year += 1
        elif action == "select_month":
            selected_month = int(data[3])
            # Определяем начало и конец выбранного месяца
            first_day_of_month = datetime(current_year, selected_month, 1)
            last_day_of_month = (datetime(current_year, selected_month + 1, 1) - timedelta(days=1)) if selected_month !=12 else datetime(current_year, 12, 31)

            # await callback.message.edit_text(f"Вы выбрали период: {first_day_of_month.strftime('%d.%m.%Y')} - {last_day_of_month.strftime('%d.%m.%Y')}")
            return first_day_of_month, last_day_of_month  # Возвращаем начало и конец месяца
        # else:
        #     pass

        # Обновляем календарь
        await callback.message.edit_reply_markup(
            reply_markup=await self.generate_month_calendar(
                current_year, back_callback, locale
            )
        )