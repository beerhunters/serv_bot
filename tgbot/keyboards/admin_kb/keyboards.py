# from aiogram.types import InlineKeyboardMarkup
# from fluent.runtime import FluentLocalization
#
# from tgbot.keyboards.general_keyboards import create_buttons
#
#
# # async def create_buttons(
# #     buttons_data: list[tuple[str, str]] = [], back_callback_data: str = None
# # ) -> InlineKeyboardMarkup:
# #     # Создаем кнопки на основе buttons_data
# #     buttons = [
# #         [InlineKeyboardButton(text=text, callback_data=callback_data)]
# #         for text, callback_data in buttons_data
# #     ]
# #
# #     # Если нет данных для кнопок, добавляем только "Главное меню"
# #     if not buttons_data:
# #         buttons.append(
# #             [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
# #         )
# #     else:
# #         # Если передан колбек для кнопки "Назад", добавляем её
# #         if back_callback_data and back_callback_data != "main_menu":
# #             buttons.append(
# #                 [InlineKeyboardButton(text="⬅️ Назад", callback_data=back_callback_data)]
# #             )
# #
# #         # В конце всегда добавляем кнопку "Главное меню"
# #         buttons.append(
# #             [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
# #         )
# #
# #     # Создаем клавиатуру и возвращаем её
# #     return InlineKeyboardMarkup(inline_keyboard=buttons)
# # async def create_buttons(
# #     buttons_data: list[tuple[str, str, str]] = None,
# #     back_callback_data: str = None,
# #     main_menu: bool = True,
# #     row_width: int = 1,
# # ) -> InlineKeyboardMarkup:
# #     """
# #     Универсальная функция для создания клавиатур с разными типами кнопок.
# #
# #     Параметры:
# #     - buttons_data: список кортежей с данными кнопок: (текст, callback_data или URL, тип кнопки).
# #     - back_callback_data: callback_data для кнопки "Назад".
# #     - main_menu: добавлять ли кнопку "Главное меню".
# #     - row_width: количество кнопок в одной строке.
# #     """
# #     buttons = []
# #     # Если переданы кнопки, создаем их
# #     if buttons_data:
# #         for text, data, button_type in buttons_data:
# #             if button_type == "url":
# #                 button = InlineKeyboardButton(text=text, url=data)
# #             elif button_type == "webapp":
# #                 button = InlineKeyboardButton(text=text, web_app=WebAppInfo(url=data))
# #             else:
# #                 button = InlineKeyboardButton(text=text, callback_data=data)
# #             buttons.append(button)
# #
# #     # Разбиваем кнопки по строкам с указанным количеством кнопок в строке
# #     rows = [buttons[i : i + row_width] for i in range(0, len(buttons), row_width)]
# #
# #     # Добавляем кнопку "Назад" при наличии back_callback_data
# #     if back_callback_data and back_callback_data != "main_menu":
# #         rows.append(
# #             [InlineKeyboardButton(text="⬅️ Назад", callback_data=back_callback_data)]
# #         )
# #
# #     # Добавляем кнопку "Главное меню" всегда, если main_menu=True
# #     if main_menu:
# #         rows.append(
# #             [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
# #         )
# #
# #     # Возвращаем объект InlineKeyboardMarkup с нужными кнопками
# #     return InlineKeyboardMarkup(inline_keyboard=rows)
#
#
# #
# # async def admin_main() -> InlineKeyboardMarkup:
# #     buttons_data = [
# #         ("🎟️ Все заявки", "all_tasks"),
# #         ("📄 Отчеты", "admin_report"),
# #         ("❔ Информация", "info_admin"),
# #     ]
# #     return await create_buttons(buttons_data)
# #
# #
# # async def tickets_menu() -> InlineKeyboardMarkup:
# #     buttons_data = [
# #         ("🗂️ Список открытых заявок", "open_tickets"),
# #         ("⚠️ Все мои заявки", "all_my_tickets"),
# #         ("✅ История заявок", "all_history"),
# #         ("📷 Заявки с фотографией", "photo_tickets"),
# #     ]
# #     return await create_buttons(buttons_data)
# #
# #
# # async def list_of_tickets(tickets) -> InlineKeyboardMarkup:
# #     # Создаем список кнопок на основе данных о заявках
# #     buttons_data = [
# #         (
# #             f"Заявка #{ticket.id} - {ticket.reg_time}",  # Текст кнопки
# #             f"ticket_{ticket.id}",  # Callback для кнопки
# #         )
# #         for ticket in tickets
# #     ]
# #
# #     # Генерируем клавиатуру с кнопками для заявок и добавляем кнопки Назад и Главное меню
# #     return await create_buttons(buttons_data, back_callback_data="all_tasks")
# #
# #
# # async def accept_ticket() -> InlineKeyboardMarkup:
# #     buttons_data = [
# #         ("➕ Принять заявку", "accept_ticket"),
# #         # ("🔰 Отправить инженеру", "send_to"),
# #     ]
# #     return await create_buttons(buttons_data, back_callback_data="open_tickets")
# #
# #
# # async def complete_ticket() -> InlineKeyboardMarkup:
# #     buttons_data = [
# #         ("☑️ Закрыть задачу сейчас", "complete_ticket"),
# #         # ("🔰 Отправить инженеру", "send_to"),
# #     ]
# #     return await create_buttons(buttons_data, back_callback_data="open_tickets")
# #
# #
# # async def close_ticket() -> InlineKeyboardMarkup:
# #     buttons_data = [
# #         ("✅ Завершить задачу", "close_ticket"),
# #     ]
# #     return await create_buttons(buttons_data, back_callback_data="open_tickets")
# #
# #
# # async def report_options() -> InlineKeyboardMarkup:
# #     buttons_data = [
# #         ("1. Заявки за месяц", "report_tickets"),
# #         ("2. Бронирования за месяц", "report_reservations"),
# #         ("3. Новые посетители", "new_visitors"),
# #     ]
# #     return await create_buttons(buttons_data, back_callback_data="main_menu")
# #
# #
# # async def period_option() -> InlineKeyboardMarkup:
# #     # Создаем список кнопок на основе данных о заявках
# #     buttons_data = [
# #         ("1. За день", "period:day"),
# #         ("2. За месяц", "period:month"),
# #     ]
# #     # Генерируем клавиатуру с кнопками для заявок и добавляем кнопки Назад и Главное меню
# #     return await create_buttons(buttons_data, back_callback_data="admin_report")
# #
# #
# # async def generate_report_button() -> InlineKeyboardMarkup:
# #     buttons_data = [
# #         ("Создать отчет", "generate_report"),
# #     ]
# #     return await create_buttons(buttons_data, back_callback_data="admin_report")
# #
# #
# # async def approval(booking_id: int):
# #     buttons_data = [
# #         ("✅ Подтвердить", f"approve_booking:{booking_id}"),
# #         ("❌ Отклонить", f"reject_booking:{booking_id}"),
# #     ]
# #     return await create_buttons(buttons_data)
# async def admin_main(l10n) -> InlineKeyboardMarkup:
#     buttons_data = [
#         ("👥 Список пользователей", "list_users", "callback"),
#         ("🎟️ Все заявки", "all_tasks", "callback"),
#         ("📋 Список бронирований", "list_booking", "callback"),
#         ("📄 Отчеты", "admin_report", "callback"),
#         ("❔ Информация", "info_admin", "callback"),
#     ]
#     return await create_buttons(buttons_data, l10n=l10n, main_menu=False)
#
#
# async def tickets_menu(l10n) -> InlineKeyboardMarkup:
#     buttons_data = [
#         ("🗂️ Список открытых заявок", "open_tickets", "callback"),
#         ("⚠️ Все мои заявки", "all_my_tickets", "callback"),
#         ("✅ История заявок", "all_history", "callback"),
#         ("📷 Заявки с фотографией", "photo_tickets", "callback"),
#     ]
#     return await create_buttons(buttons_data, l10n=l10n)
#
#
# async def list_of_tickets(tickets, l10n) -> InlineKeyboardMarkup:
#     buttons_data = [
#         (f"Заявка #{ticket.id} - {ticket.reg_time}", f"ticket_{ticket.id}", "callback")
#         for ticket in tickets
#     ]
#     return await create_buttons(buttons_data, back_callback_data="all_tasks", l10n=l10n)
#
#
# async def accept_ticket(l10n: FluentLocalization) -> InlineKeyboardMarkup:
#     buttons_data = [
#         ("➕ Принять заявку", "accept_ticket", "callback"),
#     ]
#     return await create_buttons(
#         buttons_data, back_callback_data="open_tickets", l10n=l10n
#     )
#
#
# async def complete_ticket(l10n) -> InlineKeyboardMarkup:
#     buttons_data = [
#         ("☑️ Закрыть задачу сейчас", "complete_ticket", "callback"),
#     ]
#     return await create_buttons(
#         buttons_data, back_callback_data="open_tickets", l10n=l10n
#     )
#
#
# async def close_ticket(l10n) -> InlineKeyboardMarkup:
#     buttons_data = [
#         ("✅ Завершить задачу", "close_ticket", "callback"),
#     ]
#     return await create_buttons(
#         buttons_data, back_callback_data="open_tickets", l10n=l10n
#     )
#
#
# async def report_options(l10n) -> InlineKeyboardMarkup:
#     buttons_data = [
#         ("1. Заявки за месяц", "report_tickets", "callback"),
#         ("2. Бронирования за месяц", "report_bookings", "callback"),
#         ("3. Новые посетители", "new_visitors", "callback"),
#     ]
#     return await create_buttons(buttons_data, back_callback_data="main_menu", l10n=l10n)
#
#
# async def period_option(l10n) -> InlineKeyboardMarkup:
#     buttons_data = [
#         ("1. За день", "period:day", "callback"),
#         ("2. За месяц", "period:month", "callback"),
#     ]
#     return await create_buttons(
#         buttons_data, back_callback_data="admin_report", l10n=l10n
#     )
#
#
# async def generate_report_button(l10n) -> InlineKeyboardMarkup:
#     buttons_data = [
#         ("Создать отчет", "generate_report", "callback"),
#     ]
#     return await create_buttons(
#         buttons_data, back_callback_data="admin_report", l10n=l10n
#     )
#
#
# async def approval(booking_id: int, l10n: FluentLocalization) -> InlineKeyboardMarkup:
#     buttons_data = [
#         ("✅ Подтвердить", f"approve_booking_{booking_id}", "callback"),
#         ("❌ Отклонить", f"reject_booking_{booking_id}", "callback"),
#     ]
#     return await create_buttons(buttons_data, l10n=l10n)
#
#
# async def users(
#     cd_next_prev,
#     cd_back,
#     page: int,
#     users_list: int,
#     page_size: int,
#     end_index: int,
#     l10n,
# ) -> InlineKeyboardMarkup:
#     buttons_data = []
#     if users_list > page_size:
#         if page > 1:
#             buttons_data.append(
#                 ("🔙 Предыдущая", f"{cd_next_prev}{page - 1}", "callback")
#             )
#         if end_index < users_list:
#             buttons_data.append(
#                 ("🔜 Следующая", f"{cd_next_prev}{page + 1}", "callback")
#             )
#     return await create_buttons(buttons_data, back_callback_data=cd_back, l10n=l10n)
#
#
# # # Список пользователей
# # async def list_users(users_list) -> InlineKeyboardMarkup:
# #     buttons_data = [
# #         (f"{i}. {user.name}", f"user_{user.id}", "callback")
# #         for i, user in enumerate(users_list, 1)
# #     ]
# #     return await create_buttons(buttons_data, "list_users")
from aiogram.types import InlineKeyboardMarkup
from fluent.runtime import FluentLocalization

from tgbot.keyboards.general_keyboards import create_buttons


# async def create_buttons(
#     buttons_data: list[tuple[str, str]] = [], back_callback_data: str = None
# ) -> InlineKeyboardMarkup:
#     # Создаем кнопки на основе buttons_data
#     buttons = [
#         [InlineKeyboardButton(text=text, callback_data=callback_data)]
#         for text, callback_data in buttons_data
#     ]
#
#     # Если нет данных для кнопок, добавляем только "Главное меню"
#     if not buttons_data:
#         buttons.append(
#             [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
#         )
#     else:
#         # Если передан колбек для кнопки "Назад", добавляем её
#         if back_callback_data and back_callback_data != "main_menu":
#             buttons.append(
#                 [InlineKeyboardButton(text="⬅️ Назад", callback_data=back_callback_data)]
#             )
#
#         # В конце всегда добавляем кнопку "Главное меню"
#         buttons.append(
#             [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
#         )
#
#     # Создаем клавиатуру и возвращаем её
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


#
# async def admin_main() -> InlineKeyboardMarkup:
#     buttons_data = [
#         ("🎟️ Все заявки", "all_tasks"),
#         ("📄 Отчеты", "admin_report"),
#         ("❔ Информация", "info_admin"),
#     ]
#     return await create_buttons(buttons_data)
#
#
# async def tickets_menu() -> InlineKeyboardMarkup:
#     buttons_data = [
#         ("🗂️ Список открытых заявок", "open_tickets"),
#         ("⚠️ Все мои заявки", "all_my_tickets"),
#         ("✅ История заявок", "all_history"),
#         ("📷 Заявки с фотографией", "photo_tickets"),
#     ]
#     return await create_buttons(buttons_data)
#
#
# async def list_of_tickets(tickets) -> InlineKeyboardMarkup:
#     # Создаем список кнопок на основе данных о заявках
#     buttons_data = [
#         (
#             f"Заявка #{ticket.id} - {ticket.reg_time}",  # Текст кнопки
#             f"ticket_{ticket.id}",  # Callback для кнопки
#         )
#         for ticket in tickets
#     ]
#
#     # Генерируем клавиатуру с кнопками для заявок и добавляем кнопки Назад и Главное меню
#     return await create_buttons(buttons_data, back_callback_data="all_tasks")
#
#
# async def accept_ticket() -> InlineKeyboardMarkup:
#     buttons_data = [
#         ("➕ Принять заявку", "accept_ticket"),
#         # ("🔰 Отправить инженеру", "send_to"),
#     ]
#     return await create_buttons(buttons_data, back_callback_data="open_tickets")
#
#
# async def complete_ticket() -> InlineKeyboardMarkup:
#     buttons_data = [
#         ("☑️ Закрыть задачу сейчас", "complete_ticket"),
#         # ("🔰 Отправить инженеру", "send_to"),
#     ]
#     return await create_buttons(buttons_data, back_callback_data="open_tickets")
#
#
# async def close_ticket() -> InlineKeyboardMarkup:
#     buttons_data = [
#         ("✅ Завершить задачу", "close_ticket"),
#     ]
#     return await create_buttons(buttons_data, back_callback_data="open_tickets")
#
#
# async def report_options() -> InlineKeyboardMarkup:
#     buttons_data = [
#         ("1. Заявки за месяц", "report_tickets"),
#         ("2. Бронирования за месяц", "report_reservations"),
#         ("3. Новые посетители", "new_visitors"),
#     ]
#     return await create_buttons(buttons_data, back_callback_data="main_menu")
#
#
# async def period_option() -> InlineKeyboardMarkup:
#     # Создаем список кнопок на основе данных о заявках
#     buttons_data = [
#         ("1. За день", "period:day"),
#         ("2. За месяц", "period:month"),
#     ]
#     # Генерируем клавиатуру с кнопками для заявок и добавляем кнопки Назад и Главное меню
#     return await create_buttons(buttons_data, back_callback_data="admin_report")
#
#
# async def generate_report_button() -> InlineKeyboardMarkup:
#     buttons_data = [
#         ("Создать отчет", "generate_report"),
#     ]
#     return await create_buttons(buttons_data, back_callback_data="admin_report")
#
#
# async def approval(booking_id: int):
#     buttons_data = [
#         ("✅ Подтвердить", f"approve_booking:{booking_id}"),
#         ("❌ Отклонить", f"reject_booking:{booking_id}"),
#     ]
#     return await create_buttons(buttons_data)
async def admin_main(l10n) -> InlineKeyboardMarkup:
    buttons_data = [
        ("👥 Список пользователей", "list_users", "callback"),
        ("🎟️ Все заявки", "all_tasks", "callback"),
        ("📋 Список бронирований", "list_booking", "callback"),
        ("📄 Отчеты", "admin_report", "callback"),
        ("❔ Информация", "info_admin", "callback"),
    ]
    return await create_buttons(buttons_data, l10n=l10n, main_menu=False)


async def tickets_menu(l10n) -> InlineKeyboardMarkup:
    buttons_data = [
        ("🗂️ Список открытых заявок", "open_tickets", "callback"),
        ("⚠️ Все мои заявки", "all_my_tickets", "callback"),
        ("✅ История заявок", "all_history", "callback"),
        ("📷 Заявки с фотографией", "photo_tickets", "callback"),
    ]
    return await create_buttons(buttons_data, l10n=l10n)


async def list_of_tickets(tickets, l10n) -> InlineKeyboardMarkup:
    buttons_data = [
        (f"Заявка #{ticket.id} - {ticket.reg_time}", f"ticket_{ticket.id}", "callback")
        for ticket in tickets
    ]
    return await create_buttons(buttons_data, back_callback_data="all_tasks", l10n=l10n)


async def accept_ticket(l10n: FluentLocalization) -> InlineKeyboardMarkup:
    buttons_data = [
        ("➕ Принять заявку", "accept_ticket", "callback"),
    ]
    return await create_buttons(
        buttons_data, back_callback_data="open_tickets", l10n=l10n
    )


async def complete_ticket(l10n) -> InlineKeyboardMarkup:
    buttons_data = [
        ("☑️ Закрыть задачу сейчас", "complete_ticket", "callback"),
    ]
    return await create_buttons(
        buttons_data, back_callback_data="open_tickets", l10n=l10n
    )


async def close_ticket(l10n) -> InlineKeyboardMarkup:
    buttons_data = [
        ("✅ Завершить задачу", "close_ticket", "callback"),
    ]
    return await create_buttons(
        buttons_data, back_callback_data="open_tickets", l10n=l10n
    )


async def report_options(l10n) -> InlineKeyboardMarkup:
    buttons_data = [
        ("1. Заявки за месяц", "report_tickets", "callback"),
        ("2. Бронирования за месяц", "report_bookings", "callback"),
        ("3. Новые посетители", "new_visitors", "callback"),
    ]
    return await create_buttons(buttons_data, back_callback_data="main_menu", l10n=l10n)


async def period_option(l10n) -> InlineKeyboardMarkup:
    buttons_data = [
        ("1. За день", "period:day", "callback"),
        ("2. За месяц", "period:month", "callback"),
    ]
    return await create_buttons(
        buttons_data, back_callback_data="admin_report", l10n=l10n
    )


async def generate_report_button(l10n) -> InlineKeyboardMarkup:
    buttons_data = [
        ("Создать отчет", "generate_report", "callback"),
    ]
    return await create_buttons(
        buttons_data, back_callback_data="admin_report", l10n=l10n
    )


async def approval(booking_id: int, l10n: FluentLocalization) -> InlineKeyboardMarkup:
    buttons_data = [
        ("✅ Подтвердить", f"approve_booking_{booking_id}", "callback"),
        ("❌ Отклонить", f"reject_booking_{booking_id}", "callback"),
    ]
    return await create_buttons(buttons_data, l10n=l10n)


async def users(
    cd_next_prev,
    cd_back,
    page: int,
    users_list: int,
    page_size: int,
    end_index: int,
    l10n,
) -> InlineKeyboardMarkup:
    buttons_data = []
    if users_list > page_size:
        if page > 1:
            buttons_data.append(
                ("🔙 Предыдущая", f"{cd_next_prev}{page - 1}", "callback")
            )
        if end_index < users_list:
            buttons_data.append(
                ("🔜 Следующая", f"{cd_next_prev}{page + 1}", "callback")
            )
    return await create_buttons(buttons_data, back_callback_data=cd_back, l10n=l10n)


# # Список пользователей
# async def list_users(users_list) -> InlineKeyboardMarkup:
#     buttons_data = [
#         (f"{i}. {user.name}", f"user_{user.id}", "callback")
#         for i, user in enumerate(users_list, 1)
#     ]
#     return await create_buttons(buttons_data, "list_users")
