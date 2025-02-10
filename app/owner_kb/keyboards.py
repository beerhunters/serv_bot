from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    KeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButtonRequestUser,
)

from app.general_keyboards import create_buttons

# from app.user_kb.keyboards import create_inline_keyboard


# # Универсальная функция для создания кнопок
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


# Универсальная функция для создания кнопок пагинации
# async def create_pagination_buttons(
#     cd_next_prev, cd_back, page, total_items, page_size, end_index, select_callback=None
# ):
#     buttons = []
#     if total_items > page_size:
#         navigation_buttons = []
#         if page > 1:
#             navigation_buttons.append(
#                 InlineKeyboardButton(
#                     text="🔙 Предыдущая", callback_data=f"{cd_next_prev}{page - 1}"
#                 )
#             )
#         if end_index < total_items:
#             navigation_buttons.append(
#                 InlineKeyboardButton(
#                     text="🔜 Следующая", callback_data=f"{cd_next_prev}{page + 1}"
#                 )
#             )
#         buttons.append(navigation_buttons)
#     if select_callback is not None:
#         buttons.append(
#             [InlineKeyboardButton(text="Выбрать", callback_data=select_callback)]
#         )
#     await add_back_button(buttons, cd_back)
#     return await create_inline_keyboard(buttons)


# # Пример функции для клавиатуры управления (общий подход для админов, промокодов и т.д.)
# async def manage_entity(
#     entity: str, list_callback: str, add_callback: str, delete_callback: str
# ) -> InlineKeyboardMarkup:
#     buttons_data = [
#         (f"📋 Список {entity}", list_callback),
#         (f"➕ Добавить {entity}", add_callback),
#         (f"➖ Удалить {entity}", delete_callback),
#     ]
#     return await create_buttons(buttons_data, "main_menu")
#
#
# # Функции для создания списков
# async def list_items(
#     items, callback_prefix, back_callback_data
# ) -> InlineKeyboardMarkup:
#     buttons_data = [
#         (f"{i}. {item.name}", f"{callback_prefix}_{item.id}")
#         for i, item in enumerate(items, 1)
#     ]
#     return await create_buttons(buttons_data, back_callback_data)


# Главная клавиатура владельца
# async def owner_main() -> InlineKeyboardMarkup:
#     buttons_data = [
#         ("⚙️ Управление администраторами", "manage_admin"),
#         ("👥 Управление пользователями", "manage_users"),
#         ("💸 Управление промокодами", "manage_promocodes"),
#         ("🖨️ Управление печатью", "manage_printing"),
#         ("📊 Управление тарифами", "manage_tariffs"),
#         ("📅 Управление бронированием ПГ", "manage_booking_mr"),
#         ("🏢 Управление локациями", "manage_locations"),
#         ("🧠 Управление квизами", "manage_quizzes"),
#         ("❔ Информация", "info_owner"),
#     ]
#     return await create_buttons(buttons_data)
async def owner_main(l10n) -> InlineKeyboardMarkup:
    buttons_data = [
        ("⚙️ Управление администраторами", "manage_admin", "callback"),
        ("👥 Управление пользователями", "manage_users", "callback"),
        ("💸 Управление промокодами", "manage_promocodes", "callback"),
        ("🖨️ Управление печатью", "manage_printing", "callback"),
        ("📊 Управление тарифами", "manage_tariffs", "callback"),
        ("📅 Управление бронированием ПГ", "manage_booking", "callback"),
        ("🏢 Управление локациями", "manage_locations", "callback"),
        ("🧠 Управление квизами", "manage_quizzes", "callback"),
        ("❔ Информация", "info_owner", "callback"),
    ]
    return await create_buttons(buttons_data, l10n=l10n, main_menu=False)


# Управление администраторами
# async def manage_admin() -> InlineKeyboardMarkup:
#     buttons_data = [
#         ("📋 Список администраторов", "list_admins"),
#         ("➕ Добавить админа", "add_admin"),
#         ("➖ Удалить админа", "delete_admin"),
#     ]
#     return await create_buttons(buttons_data, "main_menu")
async def manage_admin(l10n) -> InlineKeyboardMarkup:
    buttons_data = [
        ("📋 Список администраторов", "list_admins", "callback"),
        ("➕ Добавить админа", "add_admin", "callback"),
        ("➖ Удалить админа", "delete_admin", "callback"),
    ]
    return await create_buttons(buttons_data, l10n=l10n)


# async def manage_admin() -> InlineKeyboardMarkup:
#     return await manage_entity("admins", "list_admins", "add_admin", "delete_admin")


# Кнопка для выбора пользователя
async def request_user_button() -> ReplyKeyboardMarkup:
    request_button = KeyboardButton(
        text="Выбрать пользователя",
        request_user=KeyboardButtonRequestUser(request_id=1, user_is_bot=False),
    )
    return ReplyKeyboardMarkup(
        keyboard=[[request_button]], resize_keyboard=True, one_time_keyboard=True
    )


# Список администраторов
# async def list_of_admins(admins) -> InlineKeyboardMarkup:
#     buttons_data = [
#         (f"{i}. {tg_username}", f"admin_{admin_id}")
#         for i, (admin_id, tg_id, tg_username, name) in enumerate(admins, 1)
#     ]
#     return await create_buttons(buttons_data, "main_menu")
async def list_of_admins(admins, l10n) -> InlineKeyboardMarkup:
    buttons_data = [
        (f"{i}. {tg_username}", f"admin_{admin_id}", "callback")
        for i, (admin_id, tg_id, tg_username, name) in enumerate(admins, 1)
    ]
    return await create_buttons(buttons_data, l10n=l10n)


# async def list_of_admins(admins) -> InlineKeyboardMarkup:
#     return await list_items(admins, "admin", "main_menu")


# Управление промокодами
# async def manage_promo() -> InlineKeyboardMarkup:
#     buttons_data = [
#         ("📋 Список промокодов", "list_promocodes"),
#         ("➕ Добавить код", "add_promo"),
#         ("➖ Удалить код", "delete_promo"),
#     ]
#     return await create_buttons(buttons_data, "main_menu")
async def manage_promo(l10n) -> InlineKeyboardMarkup:
    buttons_data = [
        ("📋 Список промокодов", "list_promocodes", "callback"),
        ("➕ Добавить код", "add_promo", "callback"),
        ("➖ Удалить код", "delete_promo", "callback"),
    ]
    return await create_buttons(buttons_data, l10n=l10n)


# async def manage_promo() -> InlineKeyboardMarkup:
#     return await manage_entity("promo", "list_promocodes", "add_promo", "delete_promo")


# Промокоды с навигацией
# async def promocodes(
#     cd_next_prev,
#     cd_back,
#     page: int,
#     promocodes_list: int,
#     page_size: int,
#     end_index: int,
# ) -> InlineKeyboardMarkup:
#     return await create_pagination_buttons(
#         cd_next_prev,
#         cd_back,
#         page,
#         promocodes_list,
#         page_size,
#         end_index,
#         select_callback="select_promo",
#     )
#     # return await pagination_buttons_with_select(
#     #     cd_next_prev,
#     #     cd_back,
#     #     "select_promo",
#     #     page,
#     #     promocodes_list,
#     #     page_size,
#     #     end_index,
#     # )
# async def promocodes(
#     cd_next_prev,
#     cd_back,
#     page: int,
#     promocodes_list: int,
#     page_size: int,
#     end_index: int,
# ) -> InlineKeyboardMarkup:
#     buttons = []
#     if promocodes_list > page_size:
#         navigation_buttons = []
#         if page > 1:
#             navigation_buttons.append(
#                 InlineKeyboardButton(
#                     text="🔙 Предыдущая", callback_data=f"{cd_next_prev}{page - 1}"
#                 )
#             )
#         if end_index < promocodes_list:
#             navigation_buttons.append(
#                 InlineKeyboardButton(
#                     text="🔜 Следующая", callback_data=f"{cd_next_prev}{page + 1}"
#                 )
#             )
#         buttons.append(navigation_buttons)
#     # buttons.append([InlineKeyboardButton(text="Выбрать", callback_data="select_promo")])
#     await add_back_button(buttons, cd_back)
#     return await create_inline_keyboard(buttons)


async def promocodes(
    cd_next_prev,
    cd_back,
    page: int,
    promocodes_list: int,
    page_size: int,
    end_index: int,
    l10n,
) -> InlineKeyboardMarkup:
    buttons_data = []
    if promocodes_list > page_size:
        if page > 1:
            buttons_data.append(
                ("🔙 Предыдущая", f"{cd_next_prev}{page - 1}", "callback")
            )
        if end_index < promocodes_list:
            buttons_data.append(
                ("🔜 Следующая", f"{cd_next_prev}{page + 1}", "callback")
            )
    return await create_buttons(buttons_data, back_callback_data=cd_back, l10n=l10n)


# Список промокодов
# async def list_promocodes(list_of_promocodes) -> InlineKeyboardMarkup:
#     buttons_data = [
#         (f"{i}. {promocode.name}", f"promocode_{promocode.id}")
#         for i, promocode in enumerate(list_of_promocodes, 1)
#     ]
#     return await create_buttons(buttons_data, "list_promocodes")
async def list_promocodes(list_of_promocodes, l10n) -> InlineKeyboardMarkup:
    buttons_data = [
        (f"{i}. {promocode.name}", f"promocode_{promocode.id}", "callback")
        for i, promocode in enumerate(list_of_promocodes, 1)
    ]
    return await create_buttons(buttons_data, "list_promocodes", l10n=l10n)


# async def list_promocodes(list_of_promocodes) -> InlineKeyboardMarkup:
#     return await list_items(list_of_promocodes, "promocode", "main_menu")


# Изменение промокода
# async def promo_changes(is_active) -> InlineKeyboardMarkup:
#     status_button_text = "Отключить промокод" if is_active else "Включить промокод"
#     status_callback_text = "switch_off" if is_active else "switch_on"
#     buttons_data = [
#         (status_button_text, status_callback_text),
#         ("Продлить срок", "extend_promo"),
#     ]
#     return await create_buttons(buttons_data, "list_promocodes")
async def promo_changes(is_active, l10n) -> InlineKeyboardMarkup:
    status_button_text = "Отключить промокод" if is_active else "Включить промокод"
    status_callback_text = "switch_off" if is_active else "switch_on"
    buttons_data = [
        (status_button_text, status_callback_text, "callback"),
        ("Продлить срок", "extend_promo", "callback"),
    ]
    return await create_buttons(buttons_data, "list_promocodes", l10n=l10n)


# Сохранение изменений
async def save_changes(cancel_callback, l10n) -> InlineKeyboardMarkup:
    buttons_data = [
        ("Сохранить", "save_new_date", "callback"),
        ("Отменить", cancel_callback, "callback"),
    ]
    return await create_buttons(buttons_data, l10n=l10n)


# Управление печатью
# async def manage_printing(
#     printing_info, scanning_info, free_printing_info
# ) -> InlineKeyboardMarkup:
#     buttons_data = [
#         (
#             (
#                 "💸 Выключить бесплатную печать 🟢"
#                 if free_printing_info["state"]
#                 else "💸 Включить бесплатную печать 🔴"
#             ),
#             "toggle_free_printing",
#         ),
#         ("💰 Изменить стоимость печати", "change_price_printing"),
#         (
#             "🖨️ Выключить печать" if printing_info["state"] else "🖨️ Включить печать",
#             "toggle_printing",
#         ),
#         (
#             (
#                 "📇 Выключить сканирования"
#                 if scanning_info["state"]
#                 else "📇 Включить сканирование"
#             ),
#             "toggle_scanning",
#         ),
#     ]
#     return await create_buttons(buttons_data, "main_menu")
async def manage_printing(
    printing_info, scanning_info, free_printing_info, l10n
) -> InlineKeyboardMarkup:
    buttons_data = [
        (
            (
                "💸 Выключить бесплатную печать 🟢"
                if free_printing_info["state"]
                else "💸 Включить бесплатную печать 🔴"
            ),
            "toggle_free_printing",
            "callback",
        ),
        ("💰 Изменить стоимость печати", "change_price_printing", "callback"),
        (
            "🖨️ Выключить печать" if printing_info["state"] else "🖨️ Включить печать",
            "toggle_printing",
            "callback",
        ),
        (
            (
                "📇 Выключить сканирования"
                if scanning_info["state"]
                else "📇 Включить сканирование"
            ),
            "toggle_scanning",
            "callback",
        ),
    ]
    return await create_buttons(buttons_data, l10n=l10n)


# Управление тарифами
# async def manage_tariffs() -> InlineKeyboardMarkup:
#     buttons_data = [
#         ("📋 Список всех тарифов", "list_tariffs"),
#         ("➕ Добавить тариф", "add_tariff"),
#         ("➖ Удалить тариф", "delete_tariff"),
#     ]
#     return await create_buttons(buttons_data, "main_menu")
async def manage_tariffs(l10n) -> InlineKeyboardMarkup:
    buttons_data = [
        ("📋 Список всех тарифов", "list_tariffs", "callback"),
        ("➕ Добавить тариф", "add_tariff", "callback"),
        # ("➖ Удалить тариф", "delete_tariff", "callback"),
    ]
    return await create_buttons(buttons_data, l10n=l10n)


# async def manage_tariffs() -> InlineKeyboardMarkup:
#     return await manage_entity("tariffs", "list_tariffs", "add_tariff", "delete_tariff")


# Тарифы с навигацией
# async def tariffs(
#     cd_next_prev,
#     cd_back,
#     page: int,
#     list_of_tariffs: int,
#     page_size: int,
#     end_index: int,
# ) -> InlineKeyboardMarkup:
#     return await create_pagination_buttons(
#         cd_next_prev,
#         cd_back,
#         page,
#         list_of_tariffs,
#         page_size,
#         end_index,
#         select_callback="select_tariff",
#     )
#     # return await pagination_buttons_with_select(
#     #     cd_next_prev,
#     #     cd_back,
#     #     "select_tariff",
#     #     page,
#     #     list_of_tariffs,
#     #     page_size,
#     #     end_index,
#     # )
# async def tariffs(
#     cd_next_prev,
#     cd_back,
#     page: int,
#     list_of_tariffs: int,
#     page_size: int,
#     end_index: int,
# ) -> InlineKeyboardMarkup:
#     buttons = []
#     if list_of_tariffs > page_size:
#         navigation_buttons = []
#         if page > 1:
#             navigation_buttons.append(
#                 InlineKeyboardButton(
#                     text="🔙 Предыдущая", callback_data=f"{cd_next_prev}{page - 1}"
#                 )
#             )
#         if end_index < list_of_tariffs:
#             navigation_buttons.append(
#                 InlineKeyboardButton(
#                     text="🔜 Следующая", callback_data=f"{cd_next_prev}{page + 1}"
#                 )
#             )
#         buttons.append(navigation_buttons)
#     buttons.append(
#         [InlineKeyboardButton(text="Выбрать", callback_data="select_tariff")]
#     )
#     await add_back_button(buttons, cd_back)
#     return await create_inline_keyboard(buttons)
async def tariffs(
    cd_next_prev,
    cd_back,
    page: int,
    list_of_tariffs: int,
    page_size: int,
    end_index: int,
    l10n,
) -> InlineKeyboardMarkup:
    buttons_data = []
    if list_of_tariffs > page_size:
        if page > 1:
            buttons_data.append(
                ("🔙 Предыдущая", f"{cd_next_prev}{page - 1}", "callback")
            )
        if end_index < list_of_tariffs:
            buttons_data.append(
                ("🔜 Следующая", f"{cd_next_prev}{page + 1}", "callback")
            )
    return await create_buttons(buttons_data, back_callback_data=cd_back, l10n=l10n)


# Список тарифов
async def list_tariffs(list_of_tariffs, l10n) -> InlineKeyboardMarkup:
    buttons_data = [
        (f"{i}. {tariff.name}", f"tariff_{tariff.id}", "callback")
        for i, tariff in enumerate(list_of_tariffs, 1)
    ]
    return await create_buttons(buttons_data, "list_tariffs", l10n=l10n)


# async def list_tariffs(list_of_tariffs) -> InlineKeyboardMarkup:
#     return await list_items(list_of_tariffs, "tariff", "main_menu")


# Изменение тарифа
async def tariff_changes(is_active, l10n) -> InlineKeyboardMarkup:
    status_button_text = "Отключить тариф" if is_active else "Включить тариф"
    status_callback_text = "switch_off" if is_active else "switch_on"
    buttons_data = [
        (status_button_text, status_callback_text, "callback"),
        ("Изменить цену", "change_price_tariff", "callback"),
    ]
    return await create_buttons(buttons_data, "list_tariffs", l10n=l10n)


# Управление пользователями
async def manage_users(l10n) -> InlineKeyboardMarkup:
    buttons_data = [
        ("📋 Список всех пользователей", "list_users", "callback"),
        ("🔎 Найти пользователя", "find_user", "callback"),
        ("🗣️ Редактировать пользователя", "find_id", "callback"),
        ("🗃️ Скачать список пользователей", "download_users", "callback"),
    ]
    return await create_buttons(buttons_data, l10n=l10n)


# Поиск инструментов
async def search_tools(l10n) -> InlineKeyboardMarkup:
    buttons_data = [
        ("📍 Поиск по ID", "find_id", "callback"),
        ("📱 Поиск по номеру телефона", "find_phone", "callback"),
        ("👤 Поиск по фамилии", "find_name", "callback"),
    ]
    return await create_buttons(buttons_data, "manage_users", l10n=l10n)


# Пагинация пользователей
# async def users(
#     cd_next_prev, cd_back, page: int, users_list: int, page_size: int, end_index: int
# ) -> InlineKeyboardMarkup:
#     return await create_pagination_buttons(
#         cd_next_prev,
#         cd_back,
#         page,
#         users_list,
#         page_size,
#         end_index,
#     )
#     # return await pagination_buttons(
#     #     cd_next_prev, cd_back, page, users_list, page_size, end_index
#     # )


# async def users(
#     cd_next_prev, cd_back, page: int, users_list: int, page_size: int, end_index: int
# ) -> InlineKeyboardMarkup:
#     buttons = []
#     if users_list > page_size:
#         navigation_buttons = []
#         if page > 1:
#             navigation_buttons.append(
#                 InlineKeyboardButton(
#                     text="🔙 Предыдущая", callback_data=f"{cd_next_prev}{page - 1}"
#                 )
#             )
#         if end_index < users_list:
#             navigation_buttons.append(
#                 InlineKeyboardButton(
#                     text="🔜 Следующая", callback_data=f"{cd_next_prev}{page + 1}"
#                 )
#             )
#         buttons.append(navigation_buttons)
#     await add_back_button(buttons, cd_back)
#     return await create_inline_keyboard(buttons)
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


# Список пользователей
async def list_users(users_list, l10n) -> InlineKeyboardMarkup:
    buttons_data = [
        (f"{i}. {user.name}", f"user_{user.id}", "callback")
        for i, user in enumerate(users_list, 1)
    ]
    return await create_buttons(buttons_data, "list_users", l10n=l10n)


# async def list_users(users_list) -> InlineKeyboardMarkup:
#     return await list_items(users_list, "user", "main_menu")


# Управление локациями
async def manage_locations(l10n) -> InlineKeyboardMarkup:
    buttons_data = [
        ("📋 Список всех локаций", "list_locations", "callback"),
        ("➕ Добавить локацию", "add_location", "callback"),
        ("➖ Удалить локацию", "delete_location", "callback"),
    ]
    return await create_buttons(buttons_data, l10n=l10n)


# async def manage_locations() -> InlineKeyboardMarkup:
#     return await manage_entity(
#         "locations", "list_locations", "add_location", "delete_location"
#     )


# Локации с навигацией
# async def locations(
#     cd_next_prev,
#     cd_back,
#     page: int,
#     locations_list: int,
#     page_size: int,
#     end_index: int,
# ) -> InlineKeyboardMarkup:
#     return await create_pagination_buttons(
#         cd_next_prev,
#         cd_back,
#         page,
#         locations_list,
#         page_size,
#         end_index,
#     )
#     # return await pagination_buttons(
#     #     cd_next_prev, cd_back, page, locations_list, page_size, end_index
#     # )
# async def locations(
#     cd_next_prev,
#     cd_back,
#     page: int,
#     locations_list: int,
#     page_size: int,
#     end_index: int,
# ) -> InlineKeyboardMarkup:
#     buttons = []
#     if locations_list > page_size:
#         navigation_buttons = []
#         if page > 1:
#             navigation_buttons.append(
#                 InlineKeyboardButton(
#                     text="🔙 Предыдущая", callback_data=f"{cd_next_prev}{page - 1}"
#                 )
#             )
#         if end_index < locations_list:
#             navigation_buttons.append(
#                 InlineKeyboardButton(
#                     text="🔜 Следующая", callback_data=f"{cd_next_prev}{page + 1}"
#                 )
#             )
#         buttons.append(navigation_buttons)
#     await add_back_button(buttons, cd_back)
#     return await create_inline_keyboard(buttons)
async def locations(
    cd_next_prev,
    cd_back,
    page: int,
    locations_list: int,
    page_size: int,
    end_index: int,
    l10n,
) -> InlineKeyboardMarkup:
    buttons_data = []
    if locations_list > page_size:
        if page > 1:
            buttons_data.append(
                ("🔙 Предыдущая", f"{cd_next_prev}{page - 1}", "callback")
            )
        if end_index < locations_list:
            buttons_data.append(
                ("🔜 Следующая", f"{cd_next_prev}{page + 1}", "callback")
            )
    return await create_buttons(buttons_data, back_callback_data=cd_back, l10n=l10n)


# Список локаций
async def list_locations(locations_list, l10n) -> InlineKeyboardMarkup:
    buttons_data = [
        (f"{i}. {location.name}", f"location_{location.id}", "callback")
        for i, location in enumerate(locations_list, 1)
    ]
    return await create_buttons(buttons_data, "list_locations", l10n=l10n)


# async def list_locations(locations_list) -> InlineKeyboardMarkup:
#     return await list_items(locations_list, "location", "main_menu")


# Управление квизами
async def manage_quizzes(quiz_available, l10n) -> InlineKeyboardMarkup:
    buttons_data = [
        (
            (
                "🧠 Выключить квиз 🟢"
                if quiz_available["state"]
                else "🧠 Включить квиз 🔴"
            ),
            "quiz_toggle_free",
            "callback",
        ),
        ("📝 Загрузить квиз", "upload_quiz", "callback"),
        ("🏆 Результаты квиза", "quiz_results_for_display", "callback"),
    ]
    return await create_buttons(buttons_data, l10n=l10n)


# Клавиатура для выбора конкретного поля для редактирования
async def edit_user(l10n) -> InlineKeyboardMarkup:
    buttons_data = [
        ("✏️ Изменить ФИО", "current_edit_name", "callback"),
        ("📞 Изменить Телефон", "current_edit_phone", "callback"),
        ("📧 Изменить Email", "current_edit_email", "callback"),
        ("🗓️ Изменить Посещения", "current_edit_visits", "callback"),
    ]
    return await create_buttons(buttons_data, "manage_users", l10n=l10n)


# Основная клавиатура управления для действия над пользователем
async def edit_keyboard(user_id: int, l10n) -> InlineKeyboardMarkup:
    buttons_data = [
        ("✏️ Редактировать", f"edit_user_{user_id}", "callback"),
        ("❌ Удалить", f"delete_user_{user_id}", "callback"),
    ]
    return await create_buttons(buttons_data, "list_users", l10n=l10n)


# async def manage_booking_mr() -> InlineKeyboardMarkup:
#     return await manage_entity(
#         "booking", "list_booking_mr", "add_booking_mr", "delete_booking_mr"
#     )


async def manage_booking(l10n) -> InlineKeyboardMarkup:
    buttons_data = [
        ("📋 Список бронирований", "list_booking", "callback"),
        # ("❌ Удалить запись", "delete_booking_mr"),
        # ("🗣️ Редактировать пользователя", "find_id"),
        # ("🗃️ Скачать список пользователей", "download_users"),
    ]
    return await create_buttons(buttons_data, l10n=l10n)


# async def booking_mr_list(
#     cd_next_prev,
#     cd_back,
#     page: int,
#     booking_mr_list: int,
#     page_size: int,
#     end_index: int,
# ) -> InlineKeyboardMarkup:
#     return await create_pagination_buttons(
#         cd_next_prev,
#         cd_back,
#         page,
#         booking_mr_list,
#         page_size,
#         end_index,
#     )
# async def booking_mr_list(
#     cd_next_prev,
#     cd_back,
#     page: int,
#     booking_mr_list: int,
#     page_size: int,
#     end_index: int,
# ) -> InlineKeyboardMarkup:
#     buttons = []
#     if booking_mr_list > page_size:
#         navigation_buttons = []
#         if page > 1:
#             navigation_buttons.append(
#                 InlineKeyboardButton(
#                     text="🔙 Предыдущая", callback_data=f"{cd_next_prev}{page - 1}"
#                 )
#             )
#         if end_index < booking_mr_list:
#             navigation_buttons.append(
#                 InlineKeyboardButton(
#                     text="🔜 Следующая", callback_data=f"{cd_next_prev}{page + 1}"
#                 )
#             )
#         buttons.append(navigation_buttons)
#     await add_back_button(buttons, cd_back)
#     return await create_inline_keyboard(buttons)
async def booking_list(
    cd_next_prev,
    cd_back,
    page: int,
    bookings_list: int,
    page_size: int,
    end_index: int,
    l10n,
) -> InlineKeyboardMarkup:
    buttons_data = []
    if bookings_list > page_size:
        if page > 1:
            buttons_data.append(
                ("🔙 Предыдущая", f"{cd_next_prev}{page - 1}", "callback")
            )
        if end_index < bookings_list:
            buttons_data.append(
                ("🔜 Следующая", f"{cd_next_prev}{page + 1}", "callback")
            )
    return await create_buttons(buttons_data, back_callback_data=cd_back, l10n=l10n)


# async def back_button(callback_data="main_menu") -> InlineKeyboardMarkup:
#     """Добавляет кнопку 'Назад'"""
#     buttons = [[InlineKeyboardButton(text="⬅️ Назад", callback_data=callback_data)]]
#     return await create_inline_keyboard(buttons)
