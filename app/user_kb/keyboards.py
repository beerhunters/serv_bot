from datetime import datetime, timedelta
from random import shuffle

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    # InlineKeyboardButton,
    InlineKeyboardMarkup,
    # WebAppInfo,
)
from fluent.runtime import FluentLocalization

# from fluent.runtime import FluentLocalization

# from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.requests import (
    get_all_locations,
    get_all_tariffs,
    get_user_by_tg_id,
    # get_all_spaces,
)
from app.general_keyboards import create_buttons
from config import RULES_URL, ADMIN_URL


# contact = ReplyKeyboardMarkup(
#     keyboard=[[KeyboardButton(text="📲Отправить контакт", request_contact=True)]],
#     resize_keyboard=True,
#     input_field_placeholder="Нажмите кнопку ниже.",
#     one_time_keyboard=True,
# )
async def create_contact_button(l10n: FluentLocalization):
    """
    Функция для создания клавиатуры с кнопкой для отправки контакта с локализованным текстом.

    Параметры:
    - l10n: объект локализации для перевода текста на выбранный язык.
    """
    contact_button_text = (
        l10n.format_value("btn_contact") if l10n else "📲Отправить контакт"
    )
    input_placeholder_text = (
        l10n.format_value("contact_input_placeholder")
        if l10n
        else "Нажмите кнопку ниже."
    )

    contact = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=contact_button_text, request_contact=True)]],
        resize_keyboard=True,
        input_field_placeholder=input_placeholder_text,
        one_time_keyboard=True,
    )

    return contact


# async def user_main() -> InlineKeyboardMarkup:
#     buttons_data = [
#         ("🛠️ Helpdesk", "helpdesk", "callback"),
#         ("👥 Регистрация гостя", "reg_guest", "callback"),
#         ("📍 Забронировать", "booking", "callback"),
#         # ("🗿 Забронировать Переговорную", "select_space", "callback"),
#         ("🖨️ Печать(pdf, doc, docx)", "print_doc", "callback"),
#         ("🧠 Квиз", "start_quiz", "callback"),
#         ("📄 Общие правила", RULES_URL, "webapp"),
#         ("❔ Информация", "info_user", "callback"),
#         ("📞 Связаться с Администратором", ADMIN_URL, "url"),
#     ]
#     return await create_buttons(buttons_data, main_menu=False)


async def user_main(l10n: FluentLocalization) -> InlineKeyboardMarkup:
    buttons_data = [
        (l10n.format_value("helpdesk_button"), "helpdesk", "callback"),
        (l10n.format_value("register_guest_button"), "reg_guest", "callback"),
        (l10n.format_value("booking_button"), "booking", "callback"),
        (l10n.format_value("print_button"), "print_doc", "callback"),
        # (l10n.format_value("quiz_button"), "start_quiz", "callback"),
        (l10n.format_value("rules_button"), RULES_URL, "webapp"),
        (l10n.format_value("info_button"), "info_user", "callback"),
        (l10n.format_value("contact_admin_button"), ADMIN_URL, "url"),
    ]
    return await create_buttons(buttons_data, main_menu=False, l10n=l10n)


# async def locations() -> InlineKeyboardMarkup:
#     all_locations = await get_all_locations()
#     buttons_data = [
#         (location.name, f"location_{location.id}", "callback")
#         for location in all_locations
#     ]
#     return await create_buttons(buttons_data, back_callback_data="main_menu")


async def locations(l10n: FluentLocalization) -> InlineKeyboardMarkup:
    all_locations = await get_all_locations()
    buttons_data = [
        (location.name, f"location_{location.id}", "callback")
        for location in all_locations
    ]
    return await create_buttons(buttons_data, back_callback_data="main_menu", l10n=l10n)


# async def tickets_menu() -> InlineKeyboardMarkup:
#     buttons_data = [
#         ("📜 Все заявки", "all_tickets", "callback"),
#         ("📤 Новая заявка", "new_ticket", "callback"),
#     ]
#     return await create_buttons(buttons_data, back_callback_data="main_menu")


async def tickets_menu(l10n: FluentLocalization) -> InlineKeyboardMarkup:
    buttons_data = [
        (l10n.format_value("all_tickets_button"), "all_tickets", "callback"),
        (l10n.format_value("new_ticket_button"), "new_ticket", "callback"),
    ]
    return await create_buttons(buttons_data, back_callback_data="main_menu", l10n=l10n)


# async def tickets(
#     cd_next_prev, cd_back, page: int, tickets_list: int, page_size: int, end_index: int
# ) -> InlineKeyboardMarkup:
#     buttons_data = []
#     if tickets_list > page_size:
#         if page > 1:
#             buttons_data.append(
#                 ("🔙 Предыдущая", f"{cd_next_prev}{page - 1}", "callback")
#             )
#         if end_index < tickets_list:
#             buttons_data.append(
#                 ("🔜 Следующая", f"{cd_next_prev}{page + 1}", "callback")
#             )
#     return await create_buttons(buttons_data, back_callback_data=cd_back)


async def tickets(
    cd_next_prev,
    cd_back,
    page: int,
    tickets_list: int,
    page_size: int,
    end_index: int,
    l10n: FluentLocalization,
) -> InlineKeyboardMarkup:
    buttons_data = []
    if tickets_list > page_size:
        if page > 1:
            buttons_data.append(
                (l10n.format_value("prev_btn"), f"{cd_next_prev}{page - 1}", "callback")
            )
        if end_index < tickets_list:
            buttons_data.append(
                (l10n.format_value("next_btn"), f"{cd_next_prev}{page + 1}", "callback")
            )
    return await create_buttons(buttons_data, back_callback_data=cd_back, l10n=l10n)


# async def tariffs(tg_id) -> InlineKeyboardMarkup:
#     all_tariffs = await get_all_tariffs()
#     user = await get_user_by_tg_id(tg_id)
#
#     buttons_data = [
#         (
#             f"{tariff.name} ({tariff.price} руб.)",
#             (
#                 f"space_{tariff.id}"
#                 if tariff.purpose in {"Переговорная", "Амфитеатр"}
#                 else f"tariff_{tariff.id}"
#             ),
#             "callback",
#         )
#         for tariff in all_tariffs
#         if not (
#             tariff.name == "Тестовый день" and user and user.successful_bookings > 0
#         )
#     ]
#     return await create_buttons(buttons_data, back_callback_data="main_menu")


async def tariffs(tg_id, l10n: FluentLocalization) -> InlineKeyboardMarkup:
    all_tariffs = await get_all_tariffs()
    user = await get_user_by_tg_id(tg_id)

    buttons_data = [
        (
            f"{tariff.name} ({tariff.price} руб.)",
            (
                f"space_{tariff.id}"
                if tariff.purpose
                in {
                    l10n.format_value("meeting_room"),
                    l10n.format_value("amphitheater"),
                }
                else f"tariff_{tariff.id}"
            ),
            "callback",
        )
        for tariff in all_tariffs
        if not (
            tariff.name == l10n.format_value("test_day")
            and user
            and user.successful_bookings > 0
        )
    ]
    return await create_buttons(buttons_data, back_callback_data="main_menu", l10n=l10n)


# async def payment(confirmation_url: str, amount: int) -> InlineKeyboardMarkup:
#     buttons_data = [
#         (f"Оплатить {amount} рублей", confirmation_url, "url"),
#         ("Отмена", "cancel_pay", "callback"),
#     ]
#     return await create_buttons(buttons_data)


async def payment(
    confirmation_url: str, amount: int, l10n: FluentLocalization
) -> InlineKeyboardMarkup:
    buttons_data = [
        (f"Оплатить {amount} рублей", confirmation_url, "url"),
        ("Отмена", "cancel_pay", "callback"),
    ]
    return await create_buttons(buttons_data, l10n=l10n)


# async def time_intervals(current_date: datetime) -> InlineKeyboardMarkup:
#     now = datetime.now()
#     start_hour = 9
#     end_hour = 21
#
#     # Определяем начальное время для генерации кнопок
#     if current_date.date() == now.date():
#         # Если дата совпадает с текущей, округляем текущее время
#         if now.minute > 30:
#             start_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(
#                 hours=1
#             )
#         else:
#             start_time = now.replace(minute=30, second=0, microsecond=0)
#     else:
#         # Для других дней стартуем с 9:00
#         start_time = datetime.combine(
#             current_date.date(), datetime.min.time()
#         ) + timedelta(hours=start_hour)
#
#     # Генерация кнопок с интервалом в 30 минут
#     buttons_data = []
#     current_time = start_time
#     while current_time.hour < end_hour or (
#         current_time.hour == end_hour and current_time.minute == 0
#     ):
#         time_label = current_time.strftime("%H:%M")
#         callback_data = f"time_{time_label}"
#         buttons_data.append((time_label, callback_data, "callback"))
#         current_time += timedelta(minutes=30)
#
#     return await create_buttons(
#         buttons_data, back_callback_data="main_menu", row_width=5
#     )


async def time_intervals(
    current_date: datetime, l10n: FluentLocalization
) -> InlineKeyboardMarkup:
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
        buttons_data, back_callback_data="main_menu", row_width=5, l10n=l10n
    )


# async def duration_options(current_value: int = 1) -> InlineKeyboardMarkup:
#     buttons_data = [
#         ("-", "duration:decrease", "callback"),
#         (f"{current_value} час(а)", f"duration:{current_value}", "callback"),
#         ("+", "duration:increase", "callback"),
#         ("Подтвердить", f"confirm_duration:{current_value}", "callback"),
#     ]
#     return await create_buttons(buttons_data, row_width=3)


async def duration_options(
    l10n: FluentLocalization, current_value: int = 1
) -> InlineKeyboardMarkup:
    buttons_data = [
        ("-", "duration:decrease", "callback"),
        (f"{current_value} час(а)", f"duration:{current_value}", "callback"),
        ("+", "duration:increase", "callback"),
        (
            l10n.format_value("confirm_btn"),
            f"confirm_duration:{current_value}",
            "callback",
        ),
    ]
    return await create_buttons(buttons_data, row_width=3, l10n=l10n)


# async def printers_list(printers: dict[str, str]) -> InlineKeyboardMarkup:
#     buttons_data = [
#         (printer_name.replace("_", " "), f"select_printer:{printer_name}", "callback")
#         for printer_name in printers.keys()
#     ]
#     return await create_buttons(buttons_data, back_callback_data="main_menu")


async def printers_list(
    printers: dict[str, str], l10n: FluentLocalization
) -> InlineKeyboardMarkup:
    buttons_data = [
        (printer_name.replace("_", " "), f"select_printer:{printer_name}", "callback")
        for printer_name in printers.keys()
    ]
    return await create_buttons(buttons_data, back_callback_data="main_menu", l10n=l10n)


# async def quiz_list(quizzes) -> InlineKeyboardMarkup:
#     buttons_data = [
#         (quiz["name"], f"quiz_{quiz['id']}", "callback") for quiz in quizzes
#     ]
#     return await create_buttons(buttons_data, back_callback_data="main_menu")


async def quiz_list(quizzes, l10n: FluentLocalization) -> InlineKeyboardMarkup:
    buttons_data = [
        (quiz["name"], f"quiz_{quiz['id']}", "callback") for quiz in quizzes
    ]
    return await create_buttons(buttons_data, back_callback_data="main_menu", l10n=l10n)


# async def question(question_id, answer_options) -> InlineKeyboardMarkup:
#     indexed_options = list(enumerate(answer_options, start=1))
#     shuffle(indexed_options)
#     buttons_data = [
#         (option, f"answer_{question_id}_{index}", "callback")
#         for index, option in indexed_options
#     ]
#     return await create_buttons(buttons_data)


async def question(
    question_id, answer_options, l10n: FluentLocalization
) -> InlineKeyboardMarkup:
    indexed_options = list(enumerate(answer_options, start=1))
    shuffle(indexed_options)
    buttons_data = [
        (option, f"answer_{question_id}_{index}", "callback")
        for index, option in indexed_options
    ]
    return await create_buttons(buttons_data, l10n=l10n)
