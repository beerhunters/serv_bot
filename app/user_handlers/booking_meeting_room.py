from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery
from fluent.runtime import FluentLocalization

import app.user_kb.keyboards as kb
import app.admin_kb.keyboards as admin_kb

import app.calendar_keyboard.custom_calendar as cl
from app.database.requests import (
    get_user_by_tg_id,
    is_time_available,
    get_tariff_by_id,
    create_booking,
)
from app.rubitime import rubitime
from app.user_handlers.booking import BookingTariff
from config import BOT_ADMINS
from filters import IsUserFilter
from tools.tools import send_localized_message

meeting_room_router = Router()
# Применяем фильтр для всех хэндлеров на уровне роутера
meeting_room_router.message.filter(IsUserFilter(is_user=True))
meeting_room_router.callback_query.filter(IsUserFilter(is_user=True))


class RegMeetingRoom(StatesGroup):
    visit_date = State()
    visit_time = State()
    duration = State()


# @meeting_room_router.callback_query(F.data == "select_space")
# async def booking_meeting_room(callback: CallbackQuery, state: FSMContext):
#     await callback.message.edit_text(
#         "Выберите место для бронирования:\n",
#         reply_markup=await kb.tariffs(callback.from_user.id),
#     )
#     await state.set_state(RegMeetingRoom.space)


# @meeting_room_router.callback_query(F.data == "booking_meeting_room")
# @meeting_room_router.callback_query(F.data.startswith("space_"), RegMeetingRoom.space)
# @meeting_room_router.callback_query(F.data.startswith("space_"), BookingTariff.tariff)
# async def booking_meeting_room(callback: CallbackQuery, state: FSMContext):
#     # print(callback.data)
#     tariff_id = callback.data.split("_")[1]
#     await state.update_data(tariff_id=tariff_id)
#     calendar = cl.CustomCalendar()
#     locale = callback.from_user.language_code
#     if locale not in ["en", "ru"]:
#         locale = "en"
#     await callback.message.edit_text(
#         f"Выберите дату бронирования:\n",
#         reply_markup=await calendar.generate_calendar(
#             datetime.now().year, datetime.now().month, "main_menu", locale=locale
#         ),
#     )
#     await state.set_state(RegMeetingRoom.visit_date)
@meeting_room_router.callback_query(F.data.startswith("space_"), BookingTariff.tariff)
async def booking_meeting_room(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    # print(callback.data)
    tariff_id = callback.data.split("_")[1]
    await state.update_data(tariff_id=tariff_id)
    calendar = cl.CustomCalendar()
    locale = callback.from_user.language_code
    if locale not in ["en", "ru"]:
        locale = "en"
    await callback.message.edit_text(
        f"{l10n.format_value('select_date')}\n",
        reply_markup=await calendar.generate_calendar(
            datetime.now().year, datetime.now().month, "main_menu", locale=locale
        ),
    )
    await state.set_state(RegMeetingRoom.visit_date)


# @meeting_room_router.callback_query(
#     F.data.startswith("calendar:"), RegMeetingRoom.visit_date
# )
# async def set_visit_date(callback: CallbackQuery, state: FSMContext):
#     calendar = cl.CustomCalendar()
#     locale = callback.from_user.language_code
#     if locale not in ["en", "ru"]:
#         locale = "en"
#     selected_date = await calendar.handle_callback(callback, "main_menu", locale=locale)
#
#     if selected_date:
#         await state.update_data(visit_date=selected_date.strftime("%d.%m.%Y"))
#         await callback.message.edit_text(
#             "Bыберите время:\n", reply_markup=await kb.time_intervals(selected_date)
#         )
#         await state.set_state(RegMeetingRoom.visit_time)
@meeting_room_router.callback_query(
    F.data.startswith("calendar:"), RegMeetingRoom.visit_date
)
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
        await send_localized_message(
            callback,
            l10n,
            "select_time",
            reply_markup=await kb.time_intervals(selected_date, l10n=l10n),
        )
        await state.set_state(RegMeetingRoom.visit_time)


# @meeting_room_router.callback_query(
#     F.data.startswith("time_"), RegMeetingRoom.visit_time
# )
# async def process_time_selection(callback: CallbackQuery, state: FSMContext):
#     selected_time = callback.data.split("_")[1]
#
#     await state.update_data(start_time=selected_time)
#
#     # Запрашиваем длительность брони
#     await callback.message.edit_text(
#         "Выберите длительность брони:\n", reply_markup=await kb.duration_options()
#     )
#     await state.set_state(RegMeetingRoom.duration)
@meeting_room_router.callback_query(
    F.data.startswith("time_"), RegMeetingRoom.visit_time
)
async def process_time_selection(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    selected_time = callback.data.split("_")[1]

    await state.update_data(start_time=selected_time)

    await send_localized_message(
        callback,
        l10n,
        "select_duration",
        reply_markup=await kb.duration_options(l10n=l10n),
    )
    await state.set_state(RegMeetingRoom.duration)


# @meeting_room_router.callback_query(
#     F.data.startswith("duration:"), RegMeetingRoom.duration
# )
# async def change_duration(callback: CallbackQuery, state: FSMContext):
#     data = callback.data.split(":")[1]
#
#     # Получаем текущее значение из состояния
#     state_data = await state.get_data()
#     current_value = state_data.get("duration", 1)  # По умолчанию 1
#
#     # Обработка увеличения и уменьшения
#     if data == "increase":
#         current_value += 1
#     elif data == "decrease" and current_value > 1:
#         current_value -= 1
#     elif data == "decrease" and current_value == 1:
#         await callback.answer("Значение не может быть меньше 1.", show_alert=True)
#         return
#
#     # Обновляем состояние
#     await state.update_data(duration=current_value)
#
#     # try:
#     # Изменение клавиатуры с актуальным значением длительности
#     await callback.message.edit_reply_markup(
#         reply_markup=await kb.duration_options(current_value)
#     )
#     # except Exception as e:
#     #     print(f"Ошибка валидации: {e}")
@meeting_room_router.callback_query(
    F.data.startswith("duration:"), RegMeetingRoom.duration
)
async def change_duration(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    data = callback.data.split(":")[1]

    # Получаем текущее значение из состояния
    state_data = await state.get_data()
    current_value = state_data.get("duration", 1)  # По умолчанию 1

    # Обработка увеличения и уменьшения
    if data == "increase":
        current_value += 1
    elif data == "decrease" and current_value > 1:
        current_value -= 1
    elif data == "decrease" and current_value == 1:
        await send_localized_message(
            callback,
            l10n,
            "error_duration",
            show_alert=True,
        )
        return

    # Обновляем состояние
    await state.update_data(duration=current_value)

    # Изменение клавиатуры с актуальным значением длительности
    await callback.message.edit_reply_markup(
        reply_markup=await kb.duration_options(current_value=current_value, l10n=l10n)
    )


# @meeting_room_router.callback_query(F.data.startswith("confirm_duration:"))
# async def confirm_duration(callback: CallbackQuery, state: FSMContext):
#     duration_hours = int(callback.data.split(":")[1])
#
#     # Сохраняем выбранную продолжительность в состояние
#     await state.update_data(duration=duration_hours)
#
#     # Получаем данные состояния (дата и начальное время)
#     data = await state.get_data()
#     visit_date = data.get("visit_date")
#     formatted_date = datetime.strptime(visit_date, "%d.%m.%Y").strftime(
#         "%Y-%m-%d %H:%M:%S"
#     )
#     start_time_str = data.get("start_time")  # Начальное время в формате HH:MM
#     tariff_id = data.get("tariff_id")
#     user_id = callback.from_user.id
#     # room = await get_space_by_id(room_id)
#     # room_name = room.name
#     # service_id = room.service_id
#     # Преобразуем start_time в datetime для расчета end_time
#     start_time = datetime.strptime(start_time_str, "%H:%M")
#     end_time = start_time + timedelta(hours=duration_hours)
#
#     # Преобразуем обратно в строку
#     end_time_str = end_time.strftime("%H:%M")
#
#     # Проверка пересечений бронирований
#     if await is_time_available(tariff_id, formatted_date, start_time_str, end_time_str):
#         # Добавляем бронирование в БД
#         # booking_id = await add_meeting_room_booking(
#         #     user_id, room_id, visit_date, start_time_str, end_time_str, duration_hours
#         # )
#         booking = await create_booking(
#             user_id,
#             tariff_id,
#             formatted_date,
#             start_time_str,
#             end_time_str,
#             duration_hours,
#         )
#
#         # Генерируем сообщение для администраторов
#         booking_text = await generate_booking_message(
#             callback,
#             tariff_id,
#             visit_date,
#             start_time_str,
#             duration_hours,
#             booking.id,
#         )
#         for admin in BOT_ADMINS:
#             await callback.bot.send_message(
#                 admin,
#                 booking_text,
#                 parse_mode="HTML",
#                 reply_markup=await admin_kb.approval(booking.id),
#             )
#
#         # Подтверждение пользователю
#         await callback.message.edit_text(
#             "Ваш запрос отправлен администратору!", reply_markup=await kb.user_main()
#         )
#         await state.clear()
#     else:
#         # Если время занято, сообщаем об этом и возвращаем в главное меню
#         await callback.message.edit_text(
#             "Извините, выбранное время уже занято. Выберите другое время.",
#             reply_markup=await kb.user_main(),
#         )
#         await state.clear()
@meeting_room_router.callback_query(F.data.startswith("confirm_duration:"))
async def confirm_duration(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    duration_hours = int(callback.data.split(":")[1])

    # Сохраняем выбранную продолжительность в состояние
    await state.update_data(duration=duration_hours)

    # Получаем данные состояния (дата и начальное время)
    data = await state.get_data()
    visit_date = data.get("visit_date")
    formatted_date = datetime.strptime(visit_date, "%d.%m.%Y").strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    start_time_str = data.get("start_time")  # Начальное время в формате HH:MM
    tariff_id = data.get("tariff_id")
    user_id = callback.from_user.id
    # Преобразуем start_time в datetime для расчета end_time
    start_time = datetime.strptime(start_time_str, "%H:%M")
    end_time = start_time + timedelta(hours=duration_hours)

    # Преобразуем обратно в строку
    end_time_str = end_time.strftime("%H:%M")

    # Проверка пересечений бронирований
    if await is_time_available(tariff_id, formatted_date, start_time_str, end_time_str):
        # Добавляем бронирование в БД
        booking = await create_booking(
            user_id,
            tariff_id,
            formatted_date,
            start_time_str,
            end_time_str,
            duration_hours,
        )

        # Генерируем сообщение для администраторов
        booking_text = await generate_booking_message(
            callback,
            tariff_id,
            visit_date,
            start_time_str,
            duration_hours,
            booking.id,
        )
        for admin in BOT_ADMINS:
            await callback.bot.send_message(
                admin,
                booking_text,
                parse_mode="HTML",
                reply_markup=await admin_kb.approval(booking.id, l10n=l10n),
            )
        # Подтверждение пользователю
        await send_localized_message(
            callback,
            l10n,
            "request_send",  # Ключ для локализованного текста регистрации
            reply_markup=await kb.user_main(l10n=l10n),
        )
        await state.clear()
    else:
        # Если время занято, сообщаем об этом и возвращаем в главное меню
        await send_localized_message(
            callback,
            l10n,
            "time_is_already_taken",  # Ключ для локализованного текста регистрации
            reply_markup=await kb.user_main(l10n=l10n),
        )
        await state.clear()


async def generate_booking_message(
    callback: CallbackQuery,
    tariff_id,
    visit_date,
    start_time,
    duration_hours,
    booking_id,
) -> str:
    user_id = callback.from_user.id
    user = await get_user_by_tg_id(
        user_id,
    )
    # room = await get_space_by_id(room_id)
    tariff = await get_tariff_by_id(tariff_id)
    text = (
        f"✅ Поступил новый запрос на переговорную: \n\n"
        f"├ <b>Имя:</b> {user.name}\n"
        f"├ <b>Телефон:</b> {user.contact}\n"
        f"├ <b>Email:</b> {user.email}\n"
        f"├ <b>Пользователь TG:</b> @{user.tg_username}\n"
        f"├ <b>Место:</b> {tariff.name}\n"
        f"├ <b>Дата посещения:</b> {visit_date}\n"
        f"├ <b>Время посещения:</b> {start_time}\n"
        f"└ <b>Продолжительность:</b> {duration_hours} ч.\n"
    )
    # # Объединяем дату и время в одну строку и преобразуем в объект datetime
    # combined_datetime = datetime.strptime(
    #     f"{visit_date} {start_time}", "%d.%m.%Y %H:%M"
    # )
    #
    # # Форматируем объект datetime в нужный формат
    # formatted_datetime = combined_datetime.strftime("%Y-%m-%d %H:%M:%S")
    # method = "create_record"
    # rubitime_id = await rubitime(
    #     method,
    #     {
    #         "service_id": tariff.service_id,
    #         "name": user.name,
    #         "email": user.email,
    #         "phone": user.contact,
    #         "record": formatted_datetime,
    #         "duration": duration_hours * 60,
    #     },
    # )
    # # await update_booking_mr_rubitime(booking_id, rubitime_id)
    # await update_booking_fields(booking_id=booking_id, rubitime_id=rubitime_id)
    return text
