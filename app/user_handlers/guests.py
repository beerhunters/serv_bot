# from datetime import datetime
#
# from aiogram import Router, F
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import StatesGroup, State
# from aiogram.types import CallbackQuery, Message
#
# import app.user_kb.keyboards as kb
#
# # import app.admin_kb.keyboards as admin_kb
#
# import app.calendar_keyboard.custom_calendar as cl
# from app.database.requests import create_guest, get_user_by_tg_id
# from config import BOT_ADMINS
# from filters import IsUserFilter
#
# guest_router = Router()
# # Применяем фильтр для всех хэндлеров на уровне роутера
# guest_router.message.filter(IsUserFilter(is_user=True))
# guest_router.callback_query.filter(IsUserFilter(is_user=True))
#
#
# # Константы для сообщений
# MSG_ENTER_GUEST_NAME = "Введите ФИО гостя:\n"
# MSG_ENTER_GUEST_PHONE = "Введите телефон гостя:\n"
# MSG_ENTER_OFFICE_NUMBER = "Введите номер офиса:\n"
# MSG_SELECT_VISIT_DATE = "Выберите дату визита гостя:\n"
# MSG_GUEST_REGISTERED = "Гость зарегистрирован!\n"
# MSG_ERROR_SENDING_REQUEST = "Ошибка при отправке запроса."
# MSG_ERROR_SAVING_GUEST = "Ошибка при сохранении данных гостя."
# MSG_DATA_MISSING = "Некоторые данные гостя отсутствуют. Пожалуйста, проверьте ввод."
# MSG_INVALID_PHONE = "Введите корректный номер телефона.\n"
# MSG_INVALID_OFFICE = "Введите корректный номер офиса.\n"
#
#
# class RegGuest(StatesGroup):
#     guest_name = State()
#     guest_phone = State()
#     office_number = State()
#     visit_date = State()
#
#
# @guest_router.callback_query(F.data == "reg_guest")
# async def reg_guest(callback: CallbackQuery, state: FSMContext):
#     await callback.message.edit_text(MSG_ENTER_GUEST_NAME)
#     await state.set_state(RegGuest.guest_name)
#
#
# @guest_router.message(RegGuest.guest_name)
# async def set_guest_name(message: Message, state: FSMContext):
#     await state.update_data(guest_name=message.text)
#     await message.answer(MSG_ENTER_GUEST_PHONE)
#     await state.set_state(RegGuest.guest_phone)
#
#
# @guest_router.message(RegGuest.guest_phone)
# async def set_guest_phone(message: Message, state: FSMContext):
#     # Валидация номера телефона
#     if not message.text.isdigit():
#         await message.answer(MSG_INVALID_PHONE)
#         return
#
#     await state.update_data(guest_phone=message.text)
#     await message.answer(MSG_ENTER_OFFICE_NUMBER)
#     await state.set_state(RegGuest.office_number)
#
#
# @guest_router.message(RegGuest.office_number)
# async def set_office_number(message: Message, state: FSMContext):
#     if not message.text.isdigit():
#         await message.answer(MSG_INVALID_OFFICE)
#         return
#
#     await state.update_data(office_number=message.text)
#     # Создаем кастомный календарь
#     calendar = cl.CustomCalendar()
#     await message.answer(
#         MSG_SELECT_VISIT_DATE,
#         reply_markup=await calendar.generate_calendar(
#             datetime.now().year, datetime.now().month, "main_menu", locale="ru"
#         ),
#     )
#     await state.set_state(RegGuest.visit_date)
#
#
# @guest_router.callback_query(F.data.startswith("calendar:"), RegGuest.visit_date)
# async def set_visit_date(callback: CallbackQuery, state: FSMContext):
#     calendar = cl.CustomCalendar()
#     selected_date = await calendar.handle_callback(callback, "main_menu", locale="ru")
#
#     if selected_date:
#         await state.update_data(visit_date=selected_date.strftime("%d.%m.%Y"))
#         data = await state.get_data()
#
#         user_id = callback.from_user.id
#         guest_name = data.get("guest_name")
#         guest_phone = data.get("guest_phone")
#         office_number = data.get("office_number")
#         visit_date = data.get("visit_date")
#
#         # Проверка на наличие всех данных
#         if not guest_name or not guest_phone or not office_number:
#             await callback.answer(MSG_DATA_MISSING, show_alert=True)
#             return
#
#         # Сохранение данных гостя и обработка ошибок
#         try:
#             await create_guest(
#                 user_id, guest_name, guest_phone, office_number, visit_date
#             )
#         except Exception as e:
#             print(e)
#             await callback.answer(MSG_ERROR_SAVING_GUEST, show_alert=True)
#             return
#
#         # Получение информации о пользователе
#         user = await get_user_by_tg_id(
#             user_id,
#         )
#
#         # Формирование сообщения для админов
#         guest_text = (
#             f"👁️‍👥\n\nРезидент <b>{user.name}</b> (@{user.tg_username}) сообщает:\n"
#             f"Придет <i>гость</i> в офис {office_number}.\n"
#             f"<b>Данные гостя:</b>\n"
#             f"<b>├ Дата :</b> {visit_date}\n"
#             f"<b>├ ФИО :</b> {guest_name}\n"
#             f"<b>└ Телефон :</b> {guest_phone}"
#         )
#
#         # Отправка сообщения админам и обработка ошибок
#         try:
#             for admin in BOT_ADMINS:
#                 # await callback.bot.send_message(admin, guest_text, parse_mode="HTML", reply_markup=await admin_kb.back_button("main_menu"))
#                 await callback.bot.send_message(
#                     admin,
#                     guest_text,
#                     parse_mode="HTML",
#                     reply_markup=await kb.create_buttons(),
#                 )
#         except Exception as e:
#             await callback.answer(MSG_ERROR_SENDING_REQUEST, show_alert=True)
#             return
#
#         await callback.message.edit_text(
#             MSG_GUEST_REGISTERED, reply_markup=await kb.user_main()
#         )
#         await state.clear()
#     else:
#         # Если выбран не день, а навигация, просто обновляем календарь
#         await callback.message.edit_reply_markup(reply_markup=selected_date)
from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from fluent.runtime import FluentLocalization

import app.user_kb.keyboards as kb
import app.calendar_keyboard.custom_calendar as cl
from app.database.requests import create_guest, get_user_by_tg_id
from config import BOT_ADMINS
from filters import IsUserFilter
from tools.tools import send_localized_message

guest_router = Router()
# Применяем фильтр для всех хэндлеров на уровне роутера
guest_router.message.filter(IsUserFilter(is_user=True))
guest_router.callback_query.filter(IsUserFilter(is_user=True))


# # Константы для сообщений
# MSG_ENTER_GUEST_COUNT = "Сколько гостей вы хотите зарегистрировать?\n"
# MSG_ENTER_GUEST_DATA = "Гость #{0}: {1}"
# MSG_ENTER_GUEST_NAME = "Введите ФИО гостя:"
# MSG_ENTER_GUEST_PHONE = "Введите телефон гостя:"
# MSG_ENTER_OFFICE_NUMBER = "Введите номер офиса:"
# MSG_SELECT_VISIT_DATE = "Выберите дату визита гостей:"
# MSG_ALL_GUESTS_REGISTERED = "Все гости успешно зарегистрированы!"
# MSG_ERROR_SENDING_REQUEST = "Ошибка при отправке запроса."
# MSG_ERROR_SAVING_GUEST = "Ошибка при сохранении данных гостя."
# MSG_INVALID_GUEST_COUNT = "Введите корректное количество гостей (число > 0)."
# MSG_INVALID_PHONE = "Введите корректный номер телефона."
# MSG_INVALID_OFFICE = "Введите корректный номер офиса."


class RegGuest(StatesGroup):
    guest_count = State()
    guest_name = State()
    guest_phone = State()
    office_number = State()
    visit_date = State()


# @guest_router.callback_query(F.data == "reg_guest")
# async def reg_guest(callback: CallbackQuery, state: FSMContext):
#     await callback.message.edit_text(MSG_ENTER_GUEST_COUNT)
#     await state.set_state(RegGuest.guest_count)
@guest_router.callback_query(F.data == "reg_guest")
async def reg_guest(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    await send_localized_message(
        callback,
        l10n,
        "msg_enter_guest_count",  # Ключ для локализованного текста регистрации
    )
    await state.set_state(RegGuest.guest_count)


# @guest_router.message(RegGuest.guest_count)
# async def set_guest_count(message: Message, state: FSMContext):
#     if not message.text.isdigit() or int(message.text) < 0:
#         await message.answer(MSG_INVALID_GUEST_COUNT)
#         return
#
#     guest_count = int(message.text)
#     await state.update_data(guest_count=guest_count, current_guest=1, guests=[])
#
#     # Начинаем ввод данных для гостей
#     await message.answer(MSG_ENTER_GUEST_DATA.format(1, MSG_ENTER_GUEST_NAME))
#     await state.set_state(RegGuest.guest_name)
@guest_router.message(RegGuest.guest_count)
async def set_guest_count(
    message: Message, state: FSMContext, l10n: FluentLocalization
):
    if not message.text.isdigit() or int(message.text) < 0:
        await send_localized_message(
            message,
            l10n,
            "msg_invalid_guest_count",  # Ключ для локализованного текста регистрации
            show_alert=True,
        )
        return

    guest_count = int(message.text)
    await state.update_data(guest_count=guest_count, current_guest=1, guests=[])
    current_guest = 1
    guest_data_text = l10n.format_value("msg_enter_guest_data")
    guest_data_text += f"{current_guest} - {l10n.format_value("msg_enter_guest_name")}"
    # Начинаем ввод данных для гостей
    await message.answer(guest_data_text)
    await state.set_state(RegGuest.guest_name)


# @guest_router.message(RegGuest.guest_name)
# async def set_guest_name(message: Message, state: FSMContext):
#     data = await state.get_data()
#     current_guest = data.get("current_guest")
#     guests = data.get("guests", [])
#
#     # Добавляем имя текущего гостя в список
#     if len(guests) < current_guest:
#         guests.append({"name": message.text})
#     else:
#         guests[current_guest - 1]["name"] = message.text
#
#     await state.update_data(guests=guests)
#     await message.answer(MSG_ENTER_GUEST_PHONE)
#     await state.set_state(RegGuest.guest_phone)
@guest_router.message(RegGuest.guest_name)
async def set_guest_name(message: Message, state: FSMContext, l10n: FluentLocalization):
    data = await state.get_data()
    current_guest = data.get("current_guest")
    guests = data.get("guests", [])

    # Добавляем имя текущего гостя в список
    if len(guests) < current_guest:
        guests.append({"name": message.text})
    else:
        guests[current_guest - 1]["name"] = message.text

    await state.update_data(guests=guests)
    await send_localized_message(
        message,
        l10n,
        "msg_enter_guest_phone",  # Ключ для локализованного текста регистрации
    )
    await state.set_state(RegGuest.guest_phone)


# @guest_router.message(RegGuest.guest_phone)
# async def set_guest_phone(message: Message, state: FSMContext):
#     if not message.text.isdigit():
#         await message.answer(MSG_INVALID_PHONE)
#         return
#
#     data = await state.get_data()
#     current_guest = data.get("current_guest")
#     guests = data.get("guests")
#
#     # Добавляем телефон к текущему гостю
#     guests[current_guest - 1]["phone"] = message.text
#     await state.update_data(guests=guests)
#
#     # Переход к следующему гостю или завершение сбора данных
#     if current_guest == data.get("guest_count"):
#         await message.answer(MSG_ENTER_OFFICE_NUMBER)
#         await state.set_state(RegGuest.office_number)
#     else:
#         await state.update_data(current_guest=current_guest + 1)
#         await message.answer(
#             MSG_ENTER_GUEST_DATA.format(current_guest + 1, MSG_ENTER_GUEST_NAME)
#         )
#         await state.set_state(RegGuest.guest_name)
@guest_router.message(RegGuest.guest_phone)
async def set_guest_phone(
    message: Message, state: FSMContext, l10n: FluentLocalization
):
    if not message.text.isdigit():
        await send_localized_message(
            message,
            l10n,
            "msg_invalid_phone",  # Ключ для локализованного текста регистрации
            show_alert=True,
        )
        return

    data = await state.get_data()
    current_guest = data.get("current_guest")
    guests = data.get("guests")

    # Добавляем телефон к текущему гостю
    guests[current_guest - 1]["phone"] = message.text
    await state.update_data(guests=guests)

    # Переход к следующему гостю или завершение сбора данных
    if current_guest == data.get("guest_count"):
        await send_localized_message(
            message,
            l10n,
            "msg_enter_office_number",  # Ключ для локализованного текста регистрации
        )
        await state.set_state(RegGuest.office_number)
    else:
        await state.update_data(current_guest=current_guest + 1)
        guest_data_text = l10n.format_value("msg_enter_guest_data")
        guest_data_text += (
            f"{current_guest + 1} - {l10n.format_value("msg_enter_guest_name")}"
        )
        await message.answer(guest_data_text)
        await state.set_state(RegGuest.guest_name)


# @guest_router.message(RegGuest.office_number)
# async def set_office_number(message: Message, state: FSMContext):
#     if not message.text.isdigit():
#         # await message.answer(MSG_INVALID_OFFICE)
#         # return
#         await state.update_data(office_number=0, office_for_msg=message.text)
#     else:
#         await state.update_data(office_number=message.text)
#
#     # Создаем кастомный календарь для выбора даты
#     calendar = cl.CustomCalendar()
#     await message.answer(
#         MSG_SELECT_VISIT_DATE,
#         reply_markup=await calendar.generate_calendar(
#             datetime.now().year, datetime.now().month, "main_menu", locale="ru"
#         ),
#     )
#     await state.set_state(RegGuest.visit_date)
@guest_router.message(RegGuest.office_number)
async def set_office_number(
    message: Message, state: FSMContext, l10n: FluentLocalization
):
    if not message.text.isdigit():
        await state.update_data(office_number=0, office_for_msg=message.text)
    else:
        await state.update_data(office_number=message.text)

    # Создаем кастомный календарь для выбора даты
    calendar = cl.CustomCalendar()
    locale = message.from_user.language_code
    if locale not in ["en", "ru"]:
        locale = "en"
    await message.answer(
        l10n.format_value("msg_select_visit_date"),
        reply_markup=await calendar.generate_calendar(
            datetime.now().year, datetime.now().month, "main_menu", locale=locale
        ),
    )
    await state.set_state(RegGuest.visit_date)


# @guest_router.callback_query(F.data.startswith("calendar:"), RegGuest.visit_date)
# async def set_visit_date(callback: CallbackQuery, state: FSMContext):
#     calendar = cl.CustomCalendar()
#     selected_date = await calendar.handle_callback(callback, "main_menu", locale="ru")
#
#     if selected_date:
#         await state.update_data(visit_date=selected_date.strftime("%d.%m.%Y"))
#         data = await state.get_data()
#
#         user_id = callback.from_user.id
#         guests = data.get("guests")
#         office_number = data.get("office_number")
#         office_for_msg = data.get("office_for_msg")
#         visit_date = data.get("visit_date")
#
#         user = await get_user_by_tg_id(user_id)
#
#         # Сохраняем каждого гостя в базу данных
#         try:
#             for guest in guests:
#                 await create_guest(
#                     user_id, guest["name"], guest["phone"], office_number, visit_date
#                 )
#         except Exception as e:
#             print(e)
#             await callback.answer(MSG_ERROR_SAVING_GUEST, show_alert=True)
#             return
#         if int(office_number) == 0:
#             office_text = office_for_msg
#         else:
#             office_text = f"офис # {office_number}"
#         # Формируем сообщение для администраторов
#         if len(guests) == 1:
#             guest_text = (
#                 f"👁️‍👥 Гости \n\nРезидент <b>{user.name}</b> (@{user.tg_username}) сообщает:\n"
#                 # f"Придет <i>гость</i> в офис {office_for_msg}.\n"
#                 f"Придет <i>гость</i> в {office_text}.\n"
#                 f"<b>Данные гостя:</b>\n"
#                 f"<b>├ Дата :</b> {visit_date}\n"
#                 f"<b>├ ФИО :</b> {guests[0]['name']}\n"
#                 f"<b>└ Телефон :</b> {guests[0]['phone']}"
#             )
#         else:
#             guest_text = (
#                 f"👁️‍👥 Гости \n\nРезидент <b>{user.name}</b> (@{user.tg_username}) сообщает:\n"
#                 # f"Придут <i>{len(guests)} гостя</i> в офис {office_for_msg}.\n"
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
#         # Отправляем сообщение администраторам
#         try:
#             for admin in BOT_ADMINS:
#                 await callback.bot.send_message(admin, guest_text, parse_mode="HTML")
#         except Exception as e:
#             print(e)
#             await callback.answer(MSG_ERROR_SENDING_REQUEST, show_alert=True)
#             return
#
#         await callback.message.edit_text(
#             MSG_ALL_GUESTS_REGISTERED, reply_markup=await kb.user_main()
#         )
#         await state.clear()
#     else:
#         # Если выбран не день, а навигация, просто обновляем календарь
#         await callback.message.edit_reply_markup(reply_markup=selected_date)
@guest_router.callback_query(F.data.startswith("calendar:"), RegGuest.visit_date)
async def set_visit_date(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    calendar = cl.CustomCalendar()
    locale = callback.from_user.language_code
    if locale not in ["en", "ru"]:
        locale = "en"
    selected_date = await calendar.handle_callback(callback, "main_menu", locale=locale)

    if selected_date:
        await state.update_data(visit_date=selected_date.strftime("%d.%m.%Y"))
        data = await state.get_data()

        user_id = callback.from_user.id
        guests = data.get("guests")
        office_number = data.get("office_number")
        office_for_msg = data.get("office_for_msg")
        visit_date = data.get("visit_date")

        user = await get_user_by_tg_id(user_id)

        # Сохраняем каждого гостя в базу данных
        try:
            for guest in guests:
                await create_guest(
                    user_id, guest["name"], guest["phone"], office_number, visit_date
                )
        except Exception:
            await send_localized_message(
                callback,
                l10n,
                "msg_error_saving_guest",  # Ключ для локализованного текста регистрации
                show_alert=True,
            )
            return
        if int(office_number) == 0:
            office_text = office_for_msg
        else:
            office_text = f"{l10n.format_value('msg_office')} # {office_number}"
        # Формируем сообщение для администраторов
        if len(guests) == 1:
            guest_text = (
                f"👁️‍👥 Гости \n\nРезидент <b>{user.name}</b> (@{user.tg_username}) сообщает:\n"
                f"Придет <i>гость</i> в {office_text}.\n"
                f"<b>Данные гостя:</b>\n"
                f"<b>├ Дата :</b> {visit_date}\n"
                f"<b>├ ФИО :</b> {guests[0]['name']}\n"
                f"<b>└ Телефон :</b> {guests[0]['phone']}"
            )
        else:
            guest_text = (
                f"👁️‍👥 Гости \n\nРезидент <b>{user.name}</b> (@{user.tg_username}) сообщает:\n"
                f"Придут <i>{len(guests)} гостя</i> в {office_text}.\n"
                f"<b>Данные гостей:</b>\n"
            )
            for i, guest in enumerate(guests, 1):
                guest_text += (
                    f"<b>Гость #{i}:</b>\n"
                    f"├ ФИО: {guest['name']}\n"
                    f"└ Телефон: {guest['phone']}\n\n"
                )

        # Отправляем сообщение администраторам
        try:
            for admin in BOT_ADMINS:
                await callback.bot.send_message(admin, guest_text, parse_mode="HTML")
        except Exception:
            await send_localized_message(
                callback,
                l10n,
                "msg_error_sending_request",  # Ключ для локализованного текста регистрации
                show_alert=True,
            )
            return
        await send_localized_message(
            callback,
            l10n,
            "msg_all_guests_registered",  # Ключ для локализованного текста регистрации
            # reply_markup=await kb.user_main(l10n),
            reply_markup=await kb.user_main(),
        )
        await state.clear()
    else:
        # Если выбран не день, а навигация, просто обновляем календарь
        await callback.message.edit_reply_markup(reply_markup=selected_date)
