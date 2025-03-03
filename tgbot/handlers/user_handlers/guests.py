# import re
# from datetime import datetime
# from typing import List, Dict
#
# from aiogram import Router, F, Bot
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import StatesGroup, State
# from aiogram.types import (
#     CallbackQuery,
#     Message,
#     InlineKeyboardMarkup,
#     InlineKeyboardButton,
# )
# from fluent.runtime import FluentLocalization
#
# from tgbot.database.requests import get_user_by_tg_id, create_guest
# from tgbot.config import BOT_ADMINS
# from tgbot.filters import IsUserFilter
# from tgbot.middlewares.custom_logging import logger
# from tgbot.tools.tools import send_localized_message
# import tgbot.keyboards.user_kb.keyboards as kb
# import tgbot.keyboards.calendar_keyboard.custom_calendar as cl
#
#
# guest_router = Router()
#
# # Ограничиваем доступ только для пользователей
# guest_router.message.filter(IsUserFilter(is_user=True))
# guest_router.callback_query.filter(IsUserFilter(is_user=True))
#
#
# class RegGuest(StatesGroup):
#     """Состояния для регистрации гостей."""
#
#     guest_count = State()  # Количество гостей
#     guest_name = State()  # Имя гостя
#     guest_phone = State()  # Телефон гостя
#     office_number = State()  # Номер офиса
#     visit_date = State()  # Дата визита
#
#
# @guest_router.callback_query(F.data == "reg_guest")
# async def reg_guest(
#     callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
# ) -> None:
#     """Начало процесса регистрации гостей."""
#     keyboard = InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(
#                     text=l10n.format_value("btn_back"), callback_data="main_menu"
#                 )
#             ]
#         ]
#     )
#     await send_localized_message(
#         callback, l10n, "msg_enter_guest_count", reply_markup=keyboard
#     )
#     await state.set_state(RegGuest.guest_count)
#
#
# @guest_router.message(RegGuest.guest_count)
# async def set_guest_count(
#     message: Message, state: FSMContext, l10n: FluentLocalization
# ) -> None:
#     """Установка количества гостей и начало ввода данных."""
#     if not message.text.isdigit() or int(message.text) <= 0:
#         await send_localized_message(
#             message, l10n, "msg_invalid_guest_count", show_alert=True
#         )
#         return
#
#     guest_count = int(message.text)
#     await state.update_data(guest_count=guest_count, current_guest=1, guests=[])
#     await send_localized_message(
#         message,
#         l10n,
#         "msg_enter_guest_data",
#         postfix=f"№{1} - {l10n.format_value('msg_enter_guest_name')}",
#     )
#     await state.set_state(RegGuest.guest_name)
#
#
# @guest_router.message(RegGuest.guest_name)
# async def set_guest_name(
#     message: Message, state: FSMContext, l10n: FluentLocalization
# ) -> None:
#     """Сохранение имени гостя и запрос телефона."""
#     data = await state.get_data()
#     current_guest = data["current_guest"]
#     guests: List[Dict[str, str]] = data.get("guests", [])
#
#     if len(guests) < current_guest:
#         guests.append({"name": message.text})
#     else:
#         guests[current_guest - 1]["name"] = message.text
#
#     await state.update_data(guests=guests)
#     await send_localized_message(message, l10n, "msg_enter_guest_phone")
#     await state.set_state(RegGuest.guest_phone)
#
#
# @guest_router.message(RegGuest.guest_phone)
# async def set_guest_phone(
#     message: Message, state: FSMContext, l10n: FluentLocalization
# ) -> None:
#     """Сохранение телефона гостя и переход к следующему шагу."""
#     # Регулярное выражение для проверки валидного номера после очистки
#     phone_pattern = re.compile(r"^(?:\+7|8)\d{10}$")  # +7 или 8 + 10 цифр = 11 всего
#
#     # Очищаем номер от пробелов, скобок и дефисов
#     cleaned_phone = re.sub(r"[ ()-]", "", message.text.strip())
#
#     # Проверяем очищенный номер
#     if not phone_pattern.match(cleaned_phone):
#         await send_localized_message(
#             message, l10n, "msg_invalid_phone", show_alert=True
#         )
#         return
#
#     data = await state.get_data()
#     current_guest = data["current_guest"]
#     guests = data["guests"]
#     guests[current_guest - 1]["phone"] = cleaned_phone
#     await state.update_data(guests=guests)
#
#     if current_guest == data["guest_count"]:
#         await send_localized_message(message, l10n, "msg_enter_office_number")
#         await state.set_state(RegGuest.office_number)
#     else:
#         await state.update_data(current_guest=current_guest + 1)
#         await send_localized_message(
#             message,
#             l10n,
#             "msg_enter_guest_data",
#             postfix=f"№{current_guest + 1} - {l10n.format_value('msg_enter_guest_name')}",
#         )
#         await state.set_state(RegGuest.guest_name)
#
#
# @guest_router.message(RegGuest.office_number)
# async def set_office_number(
#     message: Message, state: FSMContext, l10n: FluentLocalization
# ) -> None:
#     """Сохранение номера офиса и запрос даты визита."""
#     try:
#         logger.debug("Получен номер офиса: %s", message.text)
#         office_number = int(message.text) if message.text.isdigit() else 0
#         office_for_msg = message.text if not message.text.isdigit() else None
#         await state.update_data(
#             office_number=office_number, office_for_msg=office_for_msg
#         )
#
#         calendar = cl.CustomCalendar()
#         locale = message.from_user.language_code or "en"
#         if locale not in ["en", "ru"]:
#             locale = "en"
#         await message.answer(
#             l10n.format_value("msg_select_visit_date"),
#             reply_markup=await calendar.generate_calendar(
#                 datetime.now().year, datetime.now().month, "main_menu", locale=locale
#             ),
#         )
#         await state.set_state(RegGuest.visit_date)
#         logger.debug("Календарь отправлен пользователю %d", message.from_user.id)
#     except ValueError as e:
#         logger.error("Ошибка преобразования номера офиса: %s", str(e))
#         await message.answer(
#             l10n.format_value("msg_invalid_office"),
#             reply_markup=await kb.user_main(l10n),
#         )
#     except Exception as e:
#         logger.error("Ошибка в set_office_number: %s", str(e))
#         await message.answer(
#             l10n.format_value("msg_error"), reply_markup=await kb.user_main(l10n)
#         )
#
#
# async def notify_admins(
#     bot: Bot,
#     user_name: str,
#     user_tg_username: str,
#     guests: List[Dict[str, str]],
#     office_text: str,
#     visit_date: str,
#     l10n: FluentLocalization,
#     admins: List[int],
# ) -> None:
#     """Уведомление администраторов о новых гостях."""
#     try:
#         if len(guests) == 1:
#             guest_text = (
#                 f"👁️‍👥 Гости \n\nРезидент <b>{user_name}</b> (@{user_tg_username}) сообщает:\n"
#                 f"Придет <i>гость</i> в {office_text}.\n"
#                 f"<b>Данные гостя:</b>\n"
#                 f"<b>├ Дата :</b> {visit_date}\n"
#                 f"<b>├ ФИО :</b> {guests[0]['name']}\n"
#                 f"<b>└ Телефон :</b> {guests[0]['phone']}"
#             )
#         else:
#             guest_text = (
#                 f"👁️‍👥 Гости \n\nРезидент <b>{user_name}</b> (@{user_tg_username}) сообщает:\n"
#                 f"Придут <i>{len(guests)} гостя</i> в {office_text}.\n"
#                 f"<b>Данные гостей:</b>\n"
#             )
#             for i, guest in enumerate(guests, 1):
#                 guest_text += (
#                     f"<b>Гость #{i}:</b>\n"
#                     f"├ ФИО: {guest['name']}\n"
#                     f"└ Телефон: {guest['phone']}\n\n"
#                 )
#
#         for admin in admins:
#             await bot.send_message(admin, guest_text.strip(), parse_mode="HTML")
#             logger.debug("Уведомление отправлено администратору %d", admin)
#     except Exception as e:
#         logger.error("Ошибка отправки уведомления администраторам: %s", str(e))
#
#
# @guest_router.callback_query(F.data.startswith("calendar:"), RegGuest.visit_date)
# async def set_visit_date(
#     callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
# ) -> None:
#     """Сохранение даты визита и завершение регистрации гостей."""
#     try:
#         logger.debug("Обработка callback для выбора даты: %s", callback.data)
#         calendar = cl.CustomCalendar()
#         locale = callback.from_user.language_code or "en"
#         if locale not in ["en", "ru"]:
#             locale = "en"
#         selected_date = await calendar.handle_callback(
#             callback,
#             "main_menu",
#             locale=locale,
#         )
#
#         if selected_date:
#             logger.debug("Выбрана дата: %s", selected_date)
#             await state.update_data(visit_date=selected_date)
#             data = await state.get_data()
#
#             user_id = callback.from_user.id
#             guests = data["guests"]
#             office_number = int(data["office_number"])
#             office_for_msg = data.get("office_for_msg")
#             user = await get_user_by_tg_id(user_id)
#
#             for guest in guests:
#                 await create_guest(
#                     user_id=user_id,
#                     guest_name=guest["name"],
#                     guest_phone=guest["phone"],
#                     office_number=office_number,
#                     visit_date=data["visit_date"],
#                 )
#             visit_date_str = data["visit_date"].strftime("%d.%m.%Y")
#             office_text = (
#                 office_for_msg
#                 if office_number == 0
#                 else f"{l10n.format_value('msg_office')} # {office_number}"
#             )
#             await notify_admins(
#                 callback.bot,
#                 user.name,
#                 user.tg_username,
#                 guests,
#                 office_text,
#                 visit_date_str,
#                 l10n,
#                 BOT_ADMINS,
#             )
#
#             await send_localized_message(
#                 callback,
#                 l10n,
#                 "msg_all_guests_registered",
#                 reply_markup=await kb.user_main(l10n=l10n),
#             )
#             await state.clear()
#             logger.debug("Регистрация гостей завершена для пользователя %d", user_id)
#         # Убираем ветку else, так как handle_callback сам обновляет клавиатуру
#     except Exception as e:
#         logger.error("Ошибка в set_visit_date: %s", str(e))
#         await callback.answer(l10n.format_value("msg_error"), show_alert=True)
#         await state.clear()
import re
from datetime import datetime
from typing import List, Dict

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from fluent.runtime import FluentLocalization

from tgbot.database.requests import get_user_by_tg_id, create_guest
from tgbot.config import BOT_ADMINS
from tgbot.filters import IsUserFilter
from tgbot.middlewares.custom_logging import logger
from tgbot.tools.tools import send_localized_message
import tgbot.keyboards.user_kb.keyboards as kb
import tgbot.keyboards.calendar_keyboard.custom_calendar as cl


guest_router = Router()

# Ограничиваем доступ только для пользователей
guest_router.message.filter(IsUserFilter(is_user=True))
guest_router.callback_query.filter(IsUserFilter(is_user=True))


class RegGuest(StatesGroup):
    """Состояния для регистрации гостей."""

    guest_count = State()  # Количество гостей
    guest_name = State()  # Имя гостя
    guest_phone = State()  # Телефон гостя
    office_number = State()  # Номер офиса
    visit_date = State()  # Дата визита


# @guest_router.callback_query(F.data == "reg_guest")
# async def reg_guest(
#     callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
# ) -> None:
#     """Начало процесса регистрации гостей."""
#     await send_localized_message(callback, l10n, "msg_enter_guest_count")
#     await state.set_state(RegGuest.guest_count)
@guest_router.callback_query(F.data == "reg_guest")
async def reg_guest(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
) -> None:
    """Начало процесса регистрации гостей."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=l10n.format_value("btn_back"), callback_data="main_menu"
                )
            ]
        ]
    )
    await send_localized_message(
        callback, l10n, "msg_enter_guest_count", reply_markup=keyboard
    )
    await state.set_state(RegGuest.guest_count)


@guest_router.message(RegGuest.guest_count)
async def set_guest_count(
    message: Message, state: FSMContext, l10n: FluentLocalization
) -> None:
    """Установка количества гостей и начало ввода данных."""
    if not message.text.isdigit() or int(message.text) <= 0:
        await send_localized_message(
            message, l10n, "msg_invalid_guest_count", show_alert=True
        )
        return

    guest_count = int(message.text)
    await state.update_data(guest_count=guest_count, current_guest=1, guests=[])
    await send_localized_message(
        message,
        l10n,
        "msg_enter_guest_data",
        postfix=f"№{1} - {l10n.format_value('msg_enter_guest_name')}",
    )
    await state.set_state(RegGuest.guest_name)


@guest_router.message(RegGuest.guest_name)
async def set_guest_name(
    message: Message, state: FSMContext, l10n: FluentLocalization
) -> None:
    """Сохранение имени гостя и запрос телефона."""
    data = await state.get_data()
    current_guest = data["current_guest"]
    guests: List[Dict[str, str]] = data.get("guests", [])

    if len(guests) < current_guest:
        guests.append({"name": message.text})
    else:
        guests[current_guest - 1]["name"] = message.text

    await state.update_data(guests=guests)
    await send_localized_message(message, l10n, "msg_enter_guest_phone")
    await state.set_state(RegGuest.guest_phone)


@guest_router.message(RegGuest.guest_phone)
async def set_guest_phone(
    message: Message, state: FSMContext, l10n: FluentLocalization
) -> None:
    """Сохранение телефона гостя и переход к следующему шагу."""
    # Регулярное выражение для проверки валидного номера после очистки
    phone_pattern = re.compile(r"^(?:\+7|8)\d{10}$")  # +7 или 8 + 10 цифр = 11 всего

    # Очищаем номер от пробелов, скобок и дефисов
    cleaned_phone = re.sub(r"[ ()-]", "", message.text.strip())

    # Проверяем очищенный номер
    if not phone_pattern.match(cleaned_phone):
        await send_localized_message(
            message, l10n, "msg_invalid_phone", show_alert=True
        )
        return

    data = await state.get_data()
    current_guest = data["current_guest"]
    guests = data["guests"]
    guests[current_guest - 1]["phone"] = cleaned_phone
    await state.update_data(guests=guests)

    if current_guest == data["guest_count"]:
        await send_localized_message(message, l10n, "msg_enter_office_number")
        await state.set_state(RegGuest.office_number)
    else:
        await state.update_data(current_guest=current_guest + 1)
        await send_localized_message(
            message,
            l10n,
            "msg_enter_guest_data",
            postfix=f"№{current_guest + 1} - {l10n.format_value('msg_enter_guest_name')}",
        )
        await state.set_state(RegGuest.guest_name)


@guest_router.message(RegGuest.office_number)
async def set_office_number(
    message: Message, state: FSMContext, l10n: FluentLocalization
) -> None:
    """Сохранение номера офиса и запрос даты визита."""
    try:
        logger.debug("Получен номер офиса: %s", message.text)
        office_number = int(message.text) if message.text.isdigit() else 0
        office_for_msg = message.text if not message.text.isdigit() else None
        await state.update_data(
            office_number=office_number, office_for_msg=office_for_msg
        )

        calendar = cl.CustomCalendar()
        locale = message.from_user.language_code or "en"
        if locale not in ["en", "ru"]:
            locale = "en"
        await message.answer(
            l10n.format_value("msg_select_visit_date"),
            reply_markup=await calendar.generate_calendar(
                datetime.now().year, datetime.now().month, "main_menu", locale=locale
            ),
        )
        await state.set_state(RegGuest.visit_date)
        logger.debug("Календарь отправлен пользователю %d", message.from_user.id)
    except ValueError as e:
        logger.error("Ошибка преобразования номера офиса: %s", str(e))
        await message.answer(
            l10n.format_value("msg_invalid_office"),
            reply_markup=await kb.user_main(l10n),
        )
    except Exception as e:
        logger.error("Ошибка в set_office_number: %s", str(e))
        await message.answer(
            l10n.format_value("msg_error"), reply_markup=await kb.user_main(l10n)
        )


async def notify_admins(
    bot: Bot,
    user_name: str,
    user_tg_username: str,
    guests: List[Dict[str, str]],
    office_text: str,
    visit_date: str,
    l10n: FluentLocalization,
    admins: List[int],
) -> None:
    """Уведомление администраторов о новых гостях."""
    try:
        if len(guests) == 1:
            guest_text = (
                f"👁️‍👥 Гости \n\nРезидент <b>{user_name}</b> (@{user_tg_username}) сообщает:\n"
                f"Придет <i>гость</i> в {office_text}.\n"
                f"<b>Данные гостя:</b>\n"
                f"<b>├ Дата :</b> {visit_date}\n"
                f"<b>├ ФИО :</b> {guests[0]['name']}\n"
                f"<b>└ Телефон :</b> {guests[0]['phone']}"
            )
        else:
            guest_text = (
                f"👁️‍👥 Гости \n\nРезидент <b>{user_name}</b> (@{user_tg_username}) сообщает:\n"
                f"Придут <i>{len(guests)} гостя</i> в {office_text}.\n"
                f"<b>Данные гостей:</b>\n"
            )
            for i, guest in enumerate(guests, 1):
                guest_text += (
                    f"<b>Гость #{i}:</b>\n"
                    f"├ ФИО: {guest['name']}\n"
                    f"└ Телефон: {guest['phone']}\n\n"
                )

        for admin in admins:
            await bot.send_message(admin, guest_text.strip(), parse_mode="HTML")
            logger.debug("Уведомление отправлено администратору %d", admin)
    except Exception as e:
        logger.error("Ошибка отправки уведомления администраторам: %s", str(e))


@guest_router.callback_query(F.data.startswith("calendar:"), RegGuest.visit_date)
async def set_visit_date(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
) -> None:
    """Сохранение даты визита и завершение регистрации гостей."""
    try:
        logger.debug("Обработка callback для выбора даты: %s", callback.data)
        calendar = cl.CustomCalendar()
        locale = callback.from_user.language_code or "en"
        if locale not in ["en", "ru"]:
            locale = "en"
        selected_date = await calendar.handle_callback(
            callback, "main_menu", locale=locale, l10n=l10n
        )

        if selected_date:
            logger.debug("Выбрана дата: %s", selected_date)
            await state.update_data(visit_date=selected_date)
            data = await state.get_data()

            user_id = callback.from_user.id
            guests = data["guests"]
            office_number = int(data["office_number"])
            office_for_msg = data.get("office_for_msg")
            user = await get_user_by_tg_id(user_id)

            for guest in guests:
                await create_guest(
                    user_id=user_id,
                    guest_name=guest["name"],
                    guest_phone=guest["phone"],
                    office_number=office_number,
                    visit_date=data["visit_date"],
                )
            visit_date_str = data["visit_date"].strftime("%d.%m.%Y")
            office_text = (
                office_for_msg
                if office_number == 0
                else f"{l10n.format_value('msg_office')} # {office_number}"
            )
            await notify_admins(
                callback.bot,
                user.name,
                user.tg_username,
                guests,
                office_text,
                visit_date_str,
                l10n,
                BOT_ADMINS,
            )

            await send_localized_message(
                callback,
                l10n,
                "msg_all_guests_registered",
                reply_markup=await kb.user_main(l10n=l10n),
            )
            await state.clear()
            logger.debug("Регистрация гостей завершена для пользователя %d", user_id)
        # Убираем ветку else, так как handle_callback сам обновляет клавиатуру
    except Exception as e:
        logger.error("Ошибка в set_visit_date: %s", str(e))
        await callback.answer(l10n.format_value("msg_error"), show_alert=True)
        await state.clear()
