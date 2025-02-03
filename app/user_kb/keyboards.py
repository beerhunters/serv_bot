from datetime import datetime, timedelta
from random import shuffle

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    # WebAppInfo,
)

# from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.requests import (
    get_all_locations,
    get_all_tariffs,
    get_user_by_tg_id,
    # get_all_spaces,
)
from app.general_keyboards import create_buttons
from config import RULES_URL

contact = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📲Отправить контакт", request_contact=True)]],
    resize_keyboard=True,
    input_field_placeholder="Нажмите кнопку ниже.",
    one_time_keyboard=True,
)


# Универсальная функция для создания кнопок с возможностью добавления кнопки назад
# async def create_buttons(
#     buttons_data: list, back_callback_data: str = None
# ) -> InlineKeyboardMarkup:
#     buttons = [
#         [InlineKeyboardButton(text=text, callback_data=callback_data)]
#         for text, callback_data in buttons_data
#     ]
#     if back_callback_data:
#         await add_back_button(buttons, callback_data=back_callback_data)
#     return await create_inline_keyboard(buttons)
# async def create_buttons(
#     buttons_data: list[tuple[str, str, str]] = [], back_callback_data: str = None
# ) -> InlineKeyboardMarkup:
#     """
#     Создает клавиатуру на основе переданных данных, поддерживая обычные, URL и WebApp кнопки.
#
#     Параметры:
#     - buttons_data: список кортежей с данными кнопок:
#       (текст кнопки, callback_data или URL, тип кнопки: "callback", "url", "webapp")
#     - back_callback_data: callback_data для кнопки "Назад".
#     """
#     buttons = []
#     for text, data, button_type in buttons_data:
#         if button_type == "url":
#             # URL кнопка
#             buttons.append([InlineKeyboardButton(text=text, url=data)])
#         elif button_type == "webapp":
#             # WebApp кнопка
#             buttons.append(
#                 [InlineKeyboardButton(text=text, web_app=WebAppInfo(url=data))]
#             )
#         else:
#             # Обычная кнопка
#             buttons.append([InlineKeyboardButton(text=text, callback_data=data)])
#
#     # Добавляем кнопку "Назад" и "Главное меню" в зависимости от условий
#     if not buttons_data:
#         buttons.append(
#             [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
#         )
#     else:
#         if back_callback_data and back_callback_data != "main_menu":
#             buttons.append(
#                 [InlineKeyboardButton(text="⬅️ Назад", callback_data=back_callback_data)]
#             )
#         buttons.append(
#             [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
#         )
#
#     return InlineKeyboardMarkup(inline_keyboard=buttons)
# async def create_buttons(
#     buttons_data: list[tuple[str, str, str]] = None,
#     back_callback_data: str = None,
#     main_menu: bool = True,
#     row_width: int = 1,
# ) -> InlineKeyboardMarkup:
#     """
#     Универсальная функция для создания клавиатур с разными типами кнопок.
#
#     Параметры:
#     - buttons_data: список кортежей с данными кнопок: (текст, callback_data или URL, тип кнопки).
#     - back_callback_data: callback_data для кнопки "Назад".
#     - main_menu: добавлять ли кнопку "Главное меню".
#     - row_width: количество кнопок в одной строке.
#     """
#     buttons = []
#     # Если переданы кнопки, создаем их
#     if buttons_data:
#         for text, data, button_type in buttons_data:
#             if button_type == "url":
#                 button = InlineKeyboardButton(text=text, url=data)
#             elif button_type == "webapp":
#                 button = InlineKeyboardButton(text=text, web_app=WebAppInfo(url=data))
#             else:
#                 button = InlineKeyboardButton(text=text, callback_data=data)
#             buttons.append(button)
#
#     # Разбиваем кнопки по строкам с указанным количеством кнопок в строке
#     rows = [buttons[i : i + row_width] for i in range(0, len(buttons), row_width)]
#
#     # Добавляем кнопку "Назад" при наличии back_callback_data
#     if back_callback_data and back_callback_data != "main_menu":
#         rows.append(
#             [InlineKeyboardButton(text="⬅️ Назад", callback_data=back_callback_data)]
#         )
#
#     # Добавляем кнопку "Главное меню" всегда, если main_menu=True
#     if main_menu:
#         rows.append(
#             [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
#         )
#
#     # Возвращаем объект InlineKeyboardMarkup с нужными кнопками
#     return InlineKeyboardMarkup(inline_keyboard=rows)


# async def create_buttons(
#     buttons_data: list[tuple[str, str, str]] = None,
#     back_callback_data: str = None,
#     main_menu: bool = True,
#     row_width: int = 1,
# ) -> InlineKeyboardMarkup:
#     """
#     Универсальная функция для создания клавиатур с разными типами кнопок.
#
#     Параметры:
#     - buttons_data: список кортежей с данными кнопок: (текст, callback_data или URL, тип кнопки).
#     - back_callback_data: callback_data для кнопки "Назад".
#     - main_menu: добавлять ли кнопку "Главное меню".
#     - row_width: количество кнопок в одной строке.
#     """
#     buttons = []
#     # Если переданы кнопки, создаем их
#     if buttons_data:
#         for text, data, button_type in buttons_data:
#             if button_type == "url":
#                 button = InlineKeyboardButton(text=text, url=data)
#             elif button_type == "webapp":
#                 button = InlineKeyboardButton(text=text, web_app=WebAppInfo(url=data))
#             else:
#                 button = InlineKeyboardButton(text=text, callback_data=data)
#             buttons.append(button)
#
#     # Разбиваем кнопки по строкам с указанным количеством кнопок в строке
#     rows = [buttons[i : i + row_width] for i in range(0, len(buttons), row_width)]
#
#     # Добавляем кнопку "Назад" при наличии back_callback_data
#     if back_callback_data and back_callback_data != "main_menu":
#         rows.append(
#             [InlineKeyboardButton(text="⬅️ Назад", callback_data=back_callback_data)]
#         )
#
#     # Добавляем кнопку "Главное меню" всегда, если main_menu=True
#     if main_menu:
#         rows.append(
#             [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
#         )
#
#     # Возвращаем объект InlineKeyboardMarkup с нужными кнопками
#     return InlineKeyboardMarkup(inline_keyboard=rows)


# async def create_inline_keyboard(
#     buttons: list[list[InlineKeyboardButton]],
# ) -> InlineKeyboardMarkup:
#     """Утилита для создания клавиатуры с кнопками."""
#     return InlineKeyboardMarkup(inline_keyboard=buttons)


# async def add_back_button(
#     buttons: list[list[InlineKeyboardButton]], callback_data: str
# ) -> None:
#     """Добавляет кнопку 'Назад' в список кнопок."""
#     buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=callback_data)])
#
#
# async def user_main() -> InlineKeyboardMarkup:
#     # Получаем все настройки за один запрос
#     # adjustments = await get_adjustments()
#     # printing_info = adjustments.get("printing_available")
#     # scanning_info = adjustments.get("scanning_available")
#     # quiz_info = adjustments.get("quiz_available")
#
#     """Создание клавиатуры для пользователя."""
#     buttons = [
#         # [
#         #     InlineKeyboardButton(text="📤 Новая заявка", callback_data="new_ticket"),
#         #     InlineKeyboardButton(text="📜 Все заявки", callback_data="all_tickets"),
#         # ],
#         [InlineKeyboardButton(text="🛠️ Helpdesk", callback_data="helpdesk")],
#         [InlineKeyboardButton(text="👥 Регистрация гостя", callback_data="reg_guest")],
#         [InlineKeyboardButton(text="📍 Забронировать", callback_data="booking")],
#         [
#             InlineKeyboardButton(
#                 text="🗿 Забронировать Переговорную",
#                 callback_data="booking_meeting_room",
#             )
#         ],
#         [
#             InlineKeyboardButton(
#                 text="🖨️ Печать(pdf, doc, docx)", callback_data="print_doc"
#             )
#         ],
#         [InlineKeyboardButton(text="🧠 Квиз", callback_data="start_quiz")],
#         [
#             InlineKeyboardButton(
#                 text="📄 Общие правила", web_app=WebAppInfo(url=RULES_URL)
#             )
#         ],
#         [InlineKeyboardButton(text="❔ Информация", callback_data="info_user")],
#     ]
#     # if printing_info["state"]:
#     # if scanning_info["state"]:
#     #     buttons.append([InlineKeyboardButton(text="📇 Сканирование", callback_data="scan_document")])
#     # if quiz_info["state"]:
#     return await create_inline_keyboard(buttons)


# async def user_main() -> InlineKeyboardMarkup:
#     # Данные для кнопок меню пользователя
#     buttons_data = [
#         ("🛠️ Helpdesk", "helpdesk", "callback"),
#         ("👥 Регистрация гостя", "reg_guest", "callback"),
#         ("📍 Забронировать", "booking", "callback"),
#         ("🗿 Забронировать Переговорную", "booking_meeting_room", "callback"),
#         ("🖨️ Печать(pdf, doc, docx)", "print_doc", "callback"),
#         ("🧠 Квиз", "start_quiz", "callback"),
#         (
#             "📄 Общие правила",
#             RULES_URL,
#             "webapp",
#         ),
#         ("❔ Информация", "info_user", "callback"),
#     ]
#     return await create_buttons(buttons_data)
#
#
# # async def back_button(callback_data="main_menu") -> InlineKeyboardMarkup:
# #     """Добавляет кнопку 'Назад'"""
# #     buttons = [[InlineKeyboardButton(text="⬅️ Назад", callback_data=callback_data)]]
# #     return await create_inline_keyboard(buttons)
#
#
# # async def locations() -> InlineKeyboardMarkup:
# #     all_locations = await get_all_locations()
# #     keyboard = InlineKeyboardBuilder()
# #     for location in all_locations:
# #         keyboard.add(
# #             InlineKeyboardButton(
# #                 text=location.name, callback_data=f"location_{location.id}"
# #             )
# #         )
# #
# #     keyboard.add(InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu"))
# #     return keyboard.adjust(2).as_markup()
# async def locations() -> InlineKeyboardMarkup:
#     # Получаем список всех локаций
#     all_locations = await get_all_locations()
#     # Формируем список данных для кнопок
#     buttons_data = [
#         (location.name, f"location_{location.id}", "callback")
#         for location in all_locations
#     ]
#     # Вызываем функцию для создания клавиатуры с кнопками локаций и кнопкой Назад
#     return await create_buttons(buttons_data)
#
#
# async def tickets_menu() -> InlineKeyboardMarkup:
#     buttons_data = [
#         ("📜 Все заявки", "all_tickets", "callback"),
#         ("📤 Новая заявка", "new_ticket", "callback"),
#     ]
#     return await create_buttons(buttons_data)
#
#
# async def tickets(
#     cd_next_prev, cd_back, page: int, tickets_list: int, page_size: int, end_index: int
# ) -> InlineKeyboardMarkup:
#     """Клавиатура для истории заявок с навигацией по страницам."""
#     buttons = []
#
#     if tickets_list > page_size:
#         navigation_buttons = []
#         if page > 1:
#             navigation_buttons.append(
#                 InlineKeyboardButton(
#                     text="🔙 Предыдущая", callback_data=f"{cd_next_prev}{page - 1}"
#                 )
#             )
#         if end_index < tickets_list:
#             navigation_buttons.append(
#                 InlineKeyboardButton(
#                     text="🔜 Следующая", callback_data=f"{cd_next_prev}{page + 1}"
#                 )
#             )
#
#         if navigation_buttons:
#             buttons.append(navigation_buttons)
#
#     await add_back_button(buttons, cd_back)
#     return await create_inline_keyboard(buttons)
#
#
# # async def tariffs(tg_id) -> InlineKeyboardMarkup:
# #     all_tariffs = await get_all_tariffs()
# #     user = await get_user_by_tg_id(
# #         tg_id,
# #     )
# #     keyboard = InlineKeyboardBuilder()
# #     for tariff in all_tariffs:
# #         # Проверяем, есть ли тариф "Тестовый день" и был ли он активирован у пользователя
# #         if tariff.name == "Тестовый день" and user and user.successful_bookings > 0:
# #             continue  # Пропускаем добавление кнопки
# #         keyboard.add(
# #             InlineKeyboardButton(
# #                 text=f"{tariff.name} ({tariff.price} руб.)",
# #                 callback_data=f"tariff_{tariff.id}",
# #             )
# #         )
# #
# #     keyboard.add(InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu"))
# #     return keyboard.adjust(1).as_markup()
# async def tariffs(tg_id) -> InlineKeyboardMarkup:
#     # Получаем список всех тарифов и данные пользователя
#     all_tariffs = await get_all_tariffs()
#     user = await get_user_by_tg_id(tg_id)
#     # Формируем список данных для кнопок
#     buttons_data = [
#         (f"{tariff.name} ({tariff.price} руб.)", f"tariff_{tariff.id}", "callback")
#         for tariff in all_tariffs
#         # Пропускаем добавление кнопки "Тестовый день", если у пользователя уже были успешные бронирования
#         if not (
#             tariff.name == "Тестовый день" and user and user.successful_bookings > 0
#         )
#     ]
#     # Вызываем функцию для создания клавиатуры с кнопками тарифов и кнопкой Назад
#     return await create_buttons(buttons_data)
#
#
# # async def payment(confirmation_url: str, amount: int) -> InlineKeyboardMarkup:
# #     """Клавиатура для оплаты."""
# #     buttons = [
# #         [InlineKeyboardButton(text=f"Оплатить {amount} рублей", url=confirmation_url)],
# #         [InlineKeyboardButton(text="Отмена", callback_data="cancel_pay")],
# #     ]
# #     return await create_inline_keyboard(buttons)
#
#
# async def payment(confirmation_url: str, amount: int) -> InlineKeyboardMarkup:
#     """Клавиатура для оплаты."""
#     buttons_data = [
#         (f"Оплатить {amount} рублей", confirmation_url, "url"),  # URL кнопка для оплаты
#         ("Отмена", "cancel_pay", "callback"),  # Обычная кнопка отмены
#     ]
#     return await create_buttons(buttons_data)
#
#
# async def time_intervals(current_date: datetime) -> InlineKeyboardMarkup:
#     """Создание клавиатуры для выбора времени с шагом в 1 час с учетом текущего времени и даты."""
#     now = datetime.now()
#     start_hour = 9
#     end_hour = 21
#     rows = []
#     # Определяем текущий час, если сегодня
#     current_hour = now.hour if current_date.date() == now.date() else start_hour
#     for hour in range(start_hour, end_hour + 1):
#         time_text = f"{hour:02}:00"
#         # Ограничиваем доступные кнопки текущим временем, если дата сегодня
#         if hour > current_hour:
#             button_text = time_text
#             callback_data = f"time:{time_text}"
#             rows.append(
#                 InlineKeyboardButton(text=button_text, callback_data=callback_data)
#             )
#
#     button_rows = [rows[i : i + 5] for i in range(0, len(rows), 5)]
#     await add_back_button(button_rows, "main_menu")
#     return await create_inline_keyboard(button_rows)
#
#
# # async def time_intervals(current_date: datetime) -> InlineKeyboardMarkup:
# #     """Создание клавиатуры для выбора времени с шагом в 1 час с учетом текущего времени и даты."""
# #     now = datetime.now()
# #     start_hour = 9
# #     end_hour = 21
# #     buttons_data = []
# #     # Определяем текущий час, если выбранная дата - сегодня
# #     current_hour = now.hour if current_date.date() == now.date() else start_hour
# #     # Генерация списка кнопок с интервалами времени
# #     for hour in range(start_hour, end_hour + 1):
# #         time_text = f"{hour:02}:00"
# #         # Ограничиваем доступные кнопки текущим временем, если дата сегодня
# #         if hour > current_hour:
# #             buttons_data.append((time_text, f"time:{time_text}", "callback"))
# #     # Вызываем универсальную функцию с кнопками и указываем "Назад" для возврата
# #     return await create_buttons(buttons_data)
#
#
# async def duration_options(current_value: int = 1):
#     buttons = [
#         [
#             InlineKeyboardButton(text="-", callback_data="duration:decrease"),
#             InlineKeyboardButton(
#                 text=f"{current_value} час(а)",
#                 callback_data=f"duration:{current_value}",
#             ),
#             InlineKeyboardButton(text="+", callback_data="duration:increase"),
#         ],
#         [
#             InlineKeyboardButton(
#                 text="Подтвердить", callback_data=f"confirm_duration:{current_value}"
#             )
#         ],
#     ]
#     return await create_inline_keyboard(buttons)
#
#
# async def printers_list(printers: dict[str, str]) -> InlineKeyboardMarkup:
#     """Клавиатура для выбора принтера."""
#     buttons = [
#         [
#             InlineKeyboardButton(
#                 text=printer_name.replace("_", " "),
#                 callback_data=f"select_printer:{printer_name}",
#             )
#         ]
#         for printer_name in printers.keys()
#     ]
#     await add_back_button(buttons, "main_menu")
#     return await create_inline_keyboard(buttons)
#
#
# # async def scan_list(scanners: dict[str, str]) -> InlineKeyboardMarkup:
# #     """Клавиатура для выбора сканера."""
# #     buttons = [[InlineKeyboardButton(text=scanner_name, callback_data=f"select_scanner:{scanner_name}")]
# #                for scanner_name in scanners.keys()]
# #     await add_back_button(buttons, "main_menu")
# #     return await create_inline_keyboard(buttons)
#
#
# async def quiz_list(quizzes) -> InlineKeyboardMarkup:
#     buttons = [
#         [InlineKeyboardButton(text=quiz["name"], callback_data=f"quiz_{quiz['id']}")]
#         for quiz in quizzes
#     ]
#     await add_back_button(buttons, "main_menu")
#     return await create_inline_keyboard(buttons)
#
#
# async def question(question_id, answer_options) -> InlineKeyboardMarkup:
#     # Создаем список с вариантами ответов и их индексами
#     indexed_options = list(enumerate(answer_options, start=1))
#     # Перемешиваем список
#     shuffle(indexed_options)
#     # Формируем кнопки с перемешанными вариантами ответов
#     buttons = [
#         [
#             InlineKeyboardButton(
#                 text=option, callback_data=f"answer_{question_id}_{index}"
#             )
#         ]
#         for index, option in indexed_options
#     ]
#     # Создаем клавиатуру
#     return await create_inline_keyboard(buttons)
async def user_main() -> InlineKeyboardMarkup:
    buttons_data = [
        ("🛠️ Helpdesk", "helpdesk", "callback"),
        ("👥 Регистрация гостя", "reg_guest", "callback"),
        ("📍 Забронировать", "booking", "callback"),
        # ("🗿 Забронировать Переговорную", "select_space", "callback"),
        ("🖨️ Печать(pdf, doc, docx)", "print_doc", "callback"),
        ("🧠 Квиз", "start_quiz", "callback"),
        ("📄 Общие правила", RULES_URL, "webapp"),
        ("❔ Информация", "info_user", "callback"),
    ]
    return await create_buttons(buttons_data)


async def locations() -> InlineKeyboardMarkup:
    all_locations = await get_all_locations()
    buttons_data = [
        (location.name, f"location_{location.id}", "callback")
        for location in all_locations
    ]
    return await create_buttons(buttons_data, back_callback_data="main_menu")


# async def spaces() -> InlineKeyboardMarkup:
#     # all_spaces = await get_all_spaces()
#     all_spaces = await get_all_tariffs()
#     buttons_data = [
#         (space.name, f"space_{space.id}", "callback") for space in all_spaces
#     ]
#     return await create_buttons(buttons_data, back_callback_data="main_menu")


async def tickets_menu() -> InlineKeyboardMarkup:
    buttons_data = [
        ("📜 Все заявки", "all_tickets", "callback"),
        ("📤 Новая заявка", "new_ticket", "callback"),
    ]
    return await create_buttons(buttons_data, back_callback_data="main_menu")


async def tickets(
    cd_next_prev, cd_back, page: int, tickets_list: int, page_size: int, end_index: int
) -> InlineKeyboardMarkup:
    buttons_data = []
    if tickets_list > page_size:
        if page > 1:
            buttons_data.append(
                ("🔙 Предыдущая", f"{cd_next_prev}{page - 1}", "callback")
            )
        if end_index < tickets_list:
            buttons_data.append(
                ("🔜 Следующая", f"{cd_next_prev}{page + 1}", "callback")
            )
    return await create_buttons(buttons_data, back_callback_data=cd_back)


# async def tariffs(tg_id) -> InlineKeyboardMarkup:
#     all_tariffs = await get_all_tariffs()
#     user = await get_user_by_tg_id(tg_id)
#     buttons_data = [
#         (f"{tariff.name} ({tariff.price} руб.)", f"tariff_{tariff.id}", "callback")
#         for tariff in all_tariffs
#         if not (
#             tariff.name == "Тестовый день" and user and user.successful_bookings > 0
#         )
#     ]
#     return await create_buttons(buttons_data, back_callback_data="main_menu")
async def tariffs(tg_id) -> InlineKeyboardMarkup:
    all_tariffs = await get_all_tariffs()
    user = await get_user_by_tg_id(tg_id)

    buttons_data = [
        (
            f"{tariff.name} ({tariff.price} руб.)",
            (
                f"space_{tariff.id}"
                if tariff.purpose in {"Переговорная", "Амфитеатр"}
                else f"tariff_{tariff.id}"
            ),
            "callback",
        )
        for tariff in all_tariffs
        if not (
            tariff.name == "Тестовый день" and user and user.successful_bookings > 0
        )
    ]
    return await create_buttons(buttons_data, back_callback_data="main_menu")


async def payment(confirmation_url: str, amount: int) -> InlineKeyboardMarkup:
    buttons_data = [
        (f"Оплатить {amount} рублей", confirmation_url, "url"),
        ("Отмена", "cancel_pay", "callback"),
    ]
    return await create_buttons(buttons_data)


# async def time_intervals(current_date: datetime) -> InlineKeyboardMarkup:
#     now = datetime.now()
#     start_hour = 9
#     end_hour = 21
#     current_hour = now.hour if current_date.date() == now.date() else start_hour
#     buttons_data = [
#         (f"{hour:02}:00", f"time:{hour:02}:00", "callback")
#         for hour in range(start_hour, end_hour + 1)
#         if hour > current_hour
#     ]
#     return await create_buttons(
#         buttons_data, back_callback_data="main_menu", row_width=5
async def time_intervals(current_date: datetime) -> InlineKeyboardMarkup:
    now = datetime.now()
    start_hour = 9
    end_hour = 21

    # Определяем начальное время для генерации кнопок
    if current_date.date() == now.date():
        # Если дата совпадает с текущей, округляем текущее время
        if now.minute > 30:
            start_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(
                hours=1
            )
        else:
            start_time = now.replace(minute=30, second=0, microsecond=0)
    else:
        # Для других дней стартуем с 9:00
        start_time = datetime.combine(
            current_date.date(), datetime.min.time()
        ) + timedelta(hours=start_hour)

    # Генерация кнопок с интервалом в 30 минут
    buttons_data = []
    current_time = start_time
    while current_time.hour < end_hour or (
        current_time.hour == end_hour and current_time.minute == 0
    ):
        time_label = current_time.strftime("%H:%M")
        callback_data = f"time_{time_label}"
        buttons_data.append((time_label, callback_data, "callback"))
        current_time += timedelta(minutes=30)

    return await create_buttons(
        buttons_data, back_callback_data="main_menu", row_width=5
    )


async def duration_options(current_value: int = 1) -> InlineKeyboardMarkup:
    buttons_data = [
        ("-", "duration:decrease", "callback"),
        (f"{current_value} час(а)", f"duration:{current_value}", "callback"),
        ("+", "duration:increase", "callback"),
        ("Подтвердить", f"confirm_duration:{current_value}", "callback"),
    ]
    return await create_buttons(buttons_data, row_width=3)


async def printers_list(printers: dict[str, str]) -> InlineKeyboardMarkup:
    buttons_data = [
        (printer_name.replace("_", " "), f"select_printer:{printer_name}", "callback")
        for printer_name in printers.keys()
    ]
    return await create_buttons(buttons_data, back_callback_data="main_menu")


async def quiz_list(quizzes) -> InlineKeyboardMarkup:
    buttons_data = [
        (quiz["name"], f"quiz_{quiz['id']}", "callback") for quiz in quizzes
    ]
    return await create_buttons(buttons_data, back_callback_data="main_menu")


async def question(question_id, answer_options) -> InlineKeyboardMarkup:
    indexed_options = list(enumerate(answer_options, start=1))
    shuffle(indexed_options)
    buttons_data = [
        (option, f"answer_{question_id}_{index}", "callback")
        for index, option in indexed_options
    ]
    return await create_buttons(buttons_data)
