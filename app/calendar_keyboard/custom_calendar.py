from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime, timedelta


class CustomCalendar:
    """Класс для создания и управления инлайн-календарем в aiogram с поддержкой локализации."""

    def __init__(self):
        # Поддерживаемые языки: Русский и Английский
        self.locales = {
            "ru": {
                "days_of_week": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
                "months": ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                           "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
            },
            "en": {
                "days_of_week": ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
                "months": ["January", "February", "March", "April", "May", "June",
                           "July", "August", "September", "October", "November", "December"]
            }
        }

    async def generate_calendar(self, year: int, month: int, back_callback: str, locale: str = "ru") -> InlineKeyboardMarkup:
        """
        Создает инлайн-календарь для указанного года и месяца с поддержкой локализации.

        :param back_callback:
        :param year: Год
        :param month: Месяц
        :param locale: Локаль для отображения (например, "en" или "ru")
        :return: Объект InlineKeyboardMarkup с календарем
        """
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        localization = self.locales.get(locale, self.locales["en"])  # Получаем локализацию или используем английскую по умолчанию

        # Кнопки для переключения года
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text="<<", callback_data=f"calendar:prev_year:{year}:{month}"),
            InlineKeyboardButton(text=f"{year}", callback_data="ignore"),
            InlineKeyboardButton(text=">>", callback_data=f"calendar:next_year:{year}:{month}")
        ])

        # Кнопки для переключения месяца
        month_name = localization["months"][month - 1]  # Название месяца на нужном языке
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text="<", callback_data=f"calendar:prev_month:{year}:{month}"),
            InlineKeyboardButton(text=month_name, callback_data="ignore"),
            InlineKeyboardButton(text=">", callback_data=f"calendar:next_month:{year}:{month}")
        ])

        # Дни недели
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text=day, callback_data="ignore") for day in localization["days_of_week"]
        ])

        # Определение первого и последнего дня месяца
        first_day_of_month = datetime(year, month, 1)
        last_day_of_month = (datetime(year, month + 1, 1) - timedelta(days=1)) if month != 12 else (datetime(year + 1, 1, 1) - timedelta(days=1))

        # Определяем текущую дату
        today = datetime.today()

        # Кнопки для дней месяца
        days_buttons = []
        # Добавление пустых кнопок для дней до начала месяца
        for _ in range(first_day_of_month.weekday()):
            days_buttons.append(InlineKeyboardButton(text=" ", callback_data="ignore"))

        for day in range(1, last_day_of_month.day + 1):
            day_date = datetime(year, month, day)
            # Выделяем текущий день
            if day_date.date() == today.date():
                button_text = f"[{day}]"
            else:
                button_text = str(day)
            days_buttons.append(InlineKeyboardButton(
                text=button_text,
                callback_data=f"calendar:day:{year}:{month}:{day}"
            ))

        # Разделение дней по строкам (неделям)
        for week in range(0, len(days_buttons), 7):
            week_buttons = days_buttons[week:week + 7]
            # Добавляем пустые кнопки в конец, чтобы всегда было 7 ячеек
            while len(week_buttons) < 7:
                week_buttons.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
            keyboard.inline_keyboard.append(week_buttons)

        # Кнопка "Назад"
        back_button_text = "◀️ Назад" if locale == "ru" else "◀️ Back"
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=back_button_text, callback_data=back_callback)])

        return keyboard

    async def handle_callback(self, callback: CallbackQuery, back_callback: str, locale: str = "ru"):
        """
        Обработчик колбэков для календаря.

        :param locale:
        :param back_callback:
        :param callback: CallbackQuery объект
        """
        data = callback.data.split(":")
        action = data[1]

        # Проверка на корректность длины данных
        if len(data) < 4:
            return False

        current_year = int(data[2])
        current_month = int(data[3])

        if action == "prev_year":
            current_year -= 1
        elif action == "next_year":
            current_year += 1
        elif action == "prev_month":
            current_month -= 1
            if current_month < 1:
                current_month = 12
                current_year -= 1
        elif action == "next_month":
            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1
        elif action == "day":
            selected_day = int(data[4])
            selected_date = datetime(current_year, current_month, selected_day)
            # await callback.message.edit_text(f"Вы выбрали дату: {selected_date.strftime('%d.%m.%Y')}")
            return selected_date  # Возвращаем дату для дальнейшей обработки
        # else:
        #     pass

        # Предположим, что мы можем получить локаль из состояния или данных пользователя
        await callback.message.edit_reply_markup(
            reply_markup=await self.generate_calendar(
                current_year, current_month, back_callback, locale
            )
        )
