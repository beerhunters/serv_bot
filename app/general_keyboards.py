from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# from fluent.runtime import FluentLocalization
#
#
# async def create_buttons(
#     buttons_data: list[tuple[str, str, str]] = None,
#     back_callback_data: str = None,
#     main_menu: bool = True,
#     row_width: int = 1,
#     l10n: FluentLocalization = None,
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
#             [
#                 InlineKeyboardButton(
#                     text=l10n.format_value("btn_back"), callback_data=back_callback_data
#                 )
#             ]
#         )
#     # Добавляем кнопку "Главное меню" всегда, если main_menu=True
#     if main_menu:
#         rows.append(
#             [
#                 InlineKeyboardButton(
#                     text=l10n.format_value("btn_main_menu"), callback_data="main_menu"
#                 )
#             ]
#         )
#
#     # Возвращаем объект InlineKeyboardMarkup с нужными кнопками
#     return InlineKeyboardMarkup(inline_keyboard=rows)


async def create_buttons(
    buttons_data: list[tuple[str, str, str]] = None,
    back_callback_data: str = None,
    main_menu: bool = True,
    row_width: int = 1,
) -> InlineKeyboardMarkup:
    """
    Универсальная функция для создания клавиатур с разными типами кнопок.

    Параметры:
    - buttons_data: список кортежей с данными кнопок: (текст, callback_data или URL, тип кнопки).
    - back_callback_data: callback_data для кнопки "Назад".
    - main_menu: добавлять ли кнопку "Главное меню".
    - row_width: количество кнопок в одной строке.
    """
    buttons = []
    # Если переданы кнопки, создаем их
    if buttons_data:
        for text, data, button_type in buttons_data:
            if button_type == "url":
                button = InlineKeyboardButton(text=text, url=data)
            elif button_type == "webapp":
                button = InlineKeyboardButton(text=text, web_app=WebAppInfo(url=data))
            else:
                button = InlineKeyboardButton(text=text, callback_data=data)
            buttons.append(button)

    # Разбиваем кнопки по строкам с указанным количеством кнопок в строке
    rows = [buttons[i : i + row_width] for i in range(0, len(buttons), row_width)]

    # Добавляем кнопку "Назад" при наличии back_callback_data
    if back_callback_data and back_callback_data != "main_menu":
        rows.append(
            [InlineKeyboardButton(text="⬅️ Назад", callback_data=back_callback_data)]
        )
    # Добавляем кнопку "Главное меню" всегда, если main_menu=True
    if main_menu:
        rows.append(
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
        )

    # Возвращаем объект InlineKeyboardMarkup с нужными кнопками
    return InlineKeyboardMarkup(inline_keyboard=rows)
