# from datetime import datetime, timedelta
#
# from aiogram import Router, F
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import StatesGroup, State
# from aiogram.types import CallbackQuery
# from fluent.runtime import FluentLocalization
#
# import tgbot.keyboards.user_kb.keyboards as kb
# import tgbot.keyboards.admin_kb.keyboards as admin_kb
#
# import tgbot.keyboards.calendar_keyboard.custom_calendar as cl
# from tgbot.database.requests import (
#     get_user_by_tg_id,
#     is_time_available,
#     get_tariff_by_id,
#     create_booking,
# )
#
# # from app.rubitime import rubitime
# from tgbot.handlers.user_handlers.booking import BookingTariff
# from tgbot.config import BOT_ADMINS
# from tgbot.filters import IsUserFilter
# from tgbot.tools.tools import send_localized_message
#
# meeting_room_router = Router()
# # Применяем фильтр для всех хэндлеров на уровне роутера
# meeting_room_router.message.filter(IsUserFilter(is_user=True))
# meeting_room_router.callback_query.filter(IsUserFilter(is_user=True))
#
#
# class RegMeetingRoom(StatesGroup):
#     visit_date = State()
#     visit_time = State()
#     duration = State()
#
#
# # @meeting_room_router.callback_query(F.data == "select_space")
# # async def booking_meeting_room(callback: CallbackQuery, state: FSMContext):
# #     await callback.message.edit_text(
# #         "Выберите место для бронирования:\n",
# #         reply_markup=await kb.tariffs(callback.from_user.id),
# #     )
# #     await state.set_state(RegMeetingRoom.space)
#
#
# # @meeting_room_router.callback_query(F.data == "booking_meeting_room")
# # @meeting_room_router.callback_query(F.data.startswith("space_"), RegMeetingRoom.space)
# # @meeting_room_router.callback_query(F.data.startswith("space_"), BookingTariff.tariff)
# # async def booking_meeting_room(callback: CallbackQuery, state: FSMContext):
# #     # print(callback.data)
# #     tariff_id = callback.data.split("_")[1]
# #     await state.update_data(tariff_id=tariff_id)
# #     calendar = cl.CustomCalendar()
# #     locale = callback.from_user.language_code
# #     if locale not in ["en", "ru"]:
# #         locale = "en"
# #     await callback.message.edit_text(
# #         f"Выберите дату бронирования:\n",
# #         reply_markup=await calendar.generate_calendar(
# #             datetime.now().year, datetime.now().month, "main_menu", locale=locale
# #         ),
# #     )
# #     await state.set_state(RegMeetingRoom.visit_date)
# @meeting_room_router.callback_query(F.data.startswith("space_"), BookingTariff.tariff)
# async def booking_meeting_room(
#     callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
# ):
#     # print(callback.data)
#     tariff_id = callback.data.split("_")[1]
#     await state.update_data(tariff_id=tariff_id)
#     calendar = cl.CustomCalendar()
#     locale = callback.from_user.language_code
#     if locale not in ["en", "ru"]:
#         locale = "en"
#     await callback.message.edit_text(
#         f"{l10n.format_value('select_date')}\n",
#         reply_markup=await calendar.generate_calendar(
#             datetime.now().year, datetime.now().month, "main_menu", locale=locale
#         ),
#     )
#     await state.set_state(RegMeetingRoom.visit_date)
#
#
# # @meeting_room_router.callback_query(
# #     F.data.startswith("calendar:"), RegMeetingRoom.visit_date
# # )
# # async def set_visit_date(callback: CallbackQuery, state: FSMContext):
# #     calendar = cl.CustomCalendar()
# #     locale = callback.from_user.language_code
# #     if locale not in ["en", "ru"]:
# #         locale = "en"
# #     selected_date = await calendar.handle_callback(callback, "main_menu", locale=locale)
# #
# #     if selected_date:
# #         await state.update_data(visit_date=selected_date.strftime("%d.%m.%Y"))
# #         await callback.message.edit_text(
# #             "Bыберите время:\n", reply_markup=await kb.time_intervals(selected_date)
# #         )
# #         await state.set_state(RegMeetingRoom.visit_time)
# @meeting_room_router.callback_query(
#     F.data.startswith("calendar:"), RegMeetingRoom.visit_date
# )
# async def set_visit_date(
#     callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
# ):
#     calendar = cl.CustomCalendar()
#     locale = callback.from_user.language_code
#     if locale not in ["en", "ru"]:
#         locale = "en"
#     selected_date = await calendar.handle_callback(callback, "main_menu", locale=locale)
#
#     if selected_date:
#         await state.update_data(visit_date=selected_date.strftime("%d.%m.%Y"))
#         await send_localized_message(
#             callback,
#             l10n,
#             "select_time",
#             reply_markup=await kb.time_intervals(selected_date, l10n=l10n),
#         )
#         await state.set_state(RegMeetingRoom.visit_time)
#
#
# # @meeting_room_router.callback_query(
# #     F.data.startswith("time_"), RegMeetingRoom.visit_time
# # )
# # async def process_time_selection(callback: CallbackQuery, state: FSMContext):
# #     selected_time = callback.data.split("_")[1]
# #
# #     await state.update_data(start_time=selected_time)
# #
# #     # Запрашиваем длительность брони
# #     await callback.message.edit_text(
# #         "Выберите длительность брони:\n", reply_markup=await kb.duration_options()
# #     )
# #     await state.set_state(RegMeetingRoom.duration)
# @meeting_room_router.callback_query(
#     F.data.startswith("time_"), RegMeetingRoom.visit_time
# )
# async def process_time_selection(
#     callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
# ):
#     selected_time = callback.data.split("_")[1]
#
#     await state.update_data(start_time=selected_time)
#
#     await send_localized_message(
#         callback,
#         l10n,
#         "select_duration",
#         reply_markup=await kb.duration_options(l10n=l10n),
#     )
#     await state.set_state(RegMeetingRoom.duration)
#
#
# # @meeting_room_router.callback_query(
# #     F.data.startswith("duration:"), RegMeetingRoom.duration
# # )
# # async def change_duration(callback: CallbackQuery, state: FSMContext):
# #     data = callback.data.split(":")[1]
# #
# #     # Получаем текущее значение из состояния
# #     state_data = await state.get_data()
# #     current_value = state_data.get("duration", 1)  # По умолчанию 1
# #
# #     # Обработка увеличения и уменьшения
# #     if data == "increase":
# #         current_value += 1
# #     elif data == "decrease" and current_value > 1:
# #         current_value -= 1
# #     elif data == "decrease" and current_value == 1:
# #         await callback.answer("Значение не может быть меньше 1.", show_alert=True)
# #         return
# #
# #     # Обновляем состояние
# #     await state.update_data(duration=current_value)
# #
# #     # try:
# #     # Изменение клавиатуры с актуальным значением длительности
# #     await callback.message.edit_reply_markup(
# #         reply_markup=await kb.duration_options(current_value)
# #     )
# #     # except Exception as e:
# #     #     print(f"Ошибка валидации: {e}")
# @meeting_room_router.callback_query(
#     F.data.startswith("duration:"), RegMeetingRoom.duration
# )
# async def change_duration(
#     callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
# ):
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
#         await send_localized_message(
#             callback,
#             l10n,
#             "error_duration",
#             show_alert=True,
#         )
#         return
#
#     # Обновляем состояние
#     await state.update_data(duration=current_value)
#
#     # Изменение клавиатуры с актуальным значением длительности
#     await callback.message.edit_reply_markup(
#         reply_markup=await kb.duration_options(current_value=current_value, l10n=l10n)
#     )
#
#
# # @meeting_room_router.callback_query(F.data.startswith("confirm_duration:"))
# # async def confirm_duration(callback: CallbackQuery, state: FSMContext):
# #     duration_hours = int(callback.data.split(":")[1])
# #
# #     # Сохраняем выбранную продолжительность в состояние
# #     await state.update_data(duration=duration_hours)
# #
# #     # Получаем данные состояния (дата и начальное время)
# #     data = await state.get_data()
# #     visit_date = data.get("visit_date")
# #     formatted_date = datetime.strptime(visit_date, "%d.%m.%Y").strftime(
# #         "%Y-%m-%d %H:%M:%S"
# #     )
# #     start_time_str = data.get("start_time")  # Начальное время в формате HH:MM
# #     tariff_id = data.get("tariff_id")
# #     user_id = callback.from_user.id
# #     # room = await get_space_by_id(room_id)
# #     # room_name = room.name
# #     # service_id = room.service_id
# #     # Преобразуем start_time в datetime для расчета end_time
# #     start_time = datetime.strptime(start_time_str, "%H:%M")
# #     end_time = start_time + timedelta(hours=duration_hours)
# #
# #     # Преобразуем обратно в строку
# #     end_time_str = end_time.strftime("%H:%M")
# #
# #     # Проверка пересечений бронирований
# #     if await is_time_available(tariff_id, formatted_date, start_time_str, end_time_str):
# #         # Добавляем бронирование в БД
# #         # booking_id = await add_meeting_room_booking(
# #         #     user_id, room_id, visit_date, start_time_str, end_time_str, duration_hours
# #         # )
# #         booking = await create_booking(
# #             user_id,
# #             tariff_id,
# #             formatted_date,
# #             start_time_str,
# #             end_time_str,
# #             duration_hours,
# #         )
# #
# #         # Генерируем сообщение для администраторов
# #         booking_text = await generate_booking_message(
# #             callback,
# #             tariff_id,
# #             visit_date,
# #             start_time_str,
# #             duration_hours,
# #             booking.id,
# #         )
# #         for admin in BOT_ADMINS:
# #             await callback.bot.send_message(
# #                 admin,
# #                 booking_text,
# #                 parse_mode="HTML",
# #                 reply_markup=await admin_kb.approval(booking.id),
# #             )
# #
# #         # Подтверждение пользователю
# #         await callback.message.edit_text(
# #             "Ваш запрос отправлен администратору!", reply_markup=await kb.user_main()
# #         )
# #         await state.clear()
# #     else:
# #         # Если время занято, сообщаем об этом и возвращаем в главное меню
# #         await callback.message.edit_text(
# #             "Извините, выбранное время уже занято. Выберите другое время.",
# #             reply_markup=await kb.user_main(),
# #         )
# #         await state.clear()
# # @meeting_room_router.callback_query(F.data.startswith("confirm_duration:"))
# # async def confirm_duration(
# #     callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
# # ):
# #     duration_hours = int(callback.data.split(":")[1])
# #
# #     # Сохраняем выбранную продолжительность в состояние
# #     await state.update_data(duration=duration_hours)
# #
# #     # Получаем данные состояния (дата и начальное время)
# #     data = await state.get_data()
# #     visit_date = data.get("visit_date")
# #     formatted_date = datetime.strptime(visit_date, "%d.%m.%Y").strftime(
# #         "%Y-%m-%d %H:%M:%S"
# #     )
# #     start_time_str = data.get("start_time")  # Начальное время в формате HH:MM
# #     tariff_id = data.get("tariff_id")
# #     user_id = callback.from_user.id
# #     # Преобразуем start_time в datetime для расчета end_time
# #     start_time = datetime.strptime(start_time_str, "%H:%M")
# #     end_time = start_time + timedelta(hours=duration_hours)
# #
# #     # Преобразуем обратно в строку
# #     end_time_str = end_time.strftime("%H:%M")
# #
# #     # Проверка пересечений бронирований
# #     if await is_time_available(tariff_id, formatted_date, start_time_str, end_time_str):
# #         # Добавляем бронирование в БД
# #         booking = await create_booking(
# #             user_id,
# #             tariff_id,
# #             formatted_date,
# #             start_time_str,
# #             end_time_str,
# #             duration_hours,
# #         )
# #
# #         # Генерируем сообщение для администраторов
# #         booking_text = await generate_booking_message(
# #             callback,
# #             tariff_id,
# #             visit_date,
# #             start_time_str,
# #             duration_hours,
# #             booking.id,
# #         )
# #         for admin in BOT_ADMINS:
# #             await callback.bot.send_message(
# #                 admin,
# #                 booking_text,
# #                 parse_mode="HTML",
# #                 reply_markup=await admin_kb.approval(booking.id, l10n=l10n),
# #             )
# #         # Подтверждение пользователю
# #         await send_localized_message(
# #             callback,
# #             l10n,
# #             "request_send",  # Ключ для локализованного текста регистрации
# #             reply_markup=await kb.user_main(l10n=l10n),
# #         )
# #         await state.clear()
# #     else:
# #         # Если время занято, сообщаем об этом и возвращаем в главное меню
# #         await send_localized_message(
# #             callback,
# #             l10n,
# #             "time_is_already_taken",  # Ключ для локализованного текста регистрации
# #             reply_markup=await kb.user_main(l10n=l10n),
# #         )
# #         await state.clear()
# @meeting_room_router.callback_query(lambda c: c.data.startswith("confirm_duration:"))
# async def confirm_duration(
#     callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
# ):
#     duration_hours = int(callback.data.split(":")[1])
#
#     # Сохраняем выбранную продолжительность в состояние
#     await state.update_data(duration=duration_hours)
#
#     # Получаем данные состояния
#     data = await state.get_data()
#     visit_date_str = data.get("visit_date")  # строка формата "dd.mm.yyyy"
#     start_time_str = data.get("start_time")  # строка формата "HH:MM"
#     tariff_id = data.get("tariff_id")
#     user_id = callback.from_user.id
#
#     # Преобразуем дату визита в объект datetime
#     visit_date = datetime.strptime(visit_date_str, "%d.%m.%Y")
#
#     # Комбинируем дату с временем начала
#     start_time = datetime.strptime(start_time_str, "%H:%M")
#     start_datetime = visit_date.replace(
#         hour=start_time.hour, minute=start_time.minute, second=0, microsecond=0
#     )
#
#     # Вычисляем время окончания
#     end_datetime = start_datetime + timedelta(hours=duration_hours)
#
#     # Форматируем для проверки пересечений (если требуется строка)
#     formatted_date = visit_date.strftime("%Y-%m-%d %H:%M:%S")
#     start_time_str = start_datetime.strftime("%H:%M")
#     end_time_str = end_datetime.strftime("%H:%M")
#
#     # Проверка пересечений бронирований
#     if await is_time_available(tariff_id, formatted_date, start_time_str, end_time_str):
#         # Добавляем бронирование в БД (передаем datetime объекты)
#         booking = await create_booking(
#             user_tg_id=user_id,
#             tariff_id=tariff_id,
#             visit_date=start_datetime,  # Полный datetime вместо строки
#             start_time=start_datetime,  # Полный datetime
#             end_time=end_datetime,  # Полный datetime
#             duration=duration_hours,
#         )
#
#         # Генерируем сообщение для администраторов
#         booking_text = await generate_booking_message(
#             callback,
#             tariff_id,
#             visit_date_str,
#             start_time_str,
#             duration_hours,
#             booking.id,
#         )
#         for admin in BOT_ADMINS:
#             await callback.bot.send_message(
#                 admin,
#                 booking_text,
#                 parse_mode="HTML",
#                 reply_markup=await admin_kb.approval(booking.id, l10n=l10n),
#             )
#
#         # Подтверждение пользователю
#         await send_localized_message(
#             callback,
#             l10n,
#             "request_send",
#             reply_markup=await kb.user_main(l10n=l10n),
#         )
#         await state.clear()
#     else:
#         # Если время занято, сообщаем об этом и возвращаем в главное меню
#         await send_localized_message(
#             callback,
#             l10n,
#             "time_is_already_taken",
#             reply_markup=await kb.user_main(l10n=l10n),
#         )
#         await state.clear()
#
#
# async def generate_booking_message(
#     callback: CallbackQuery,
#     tariff_id,
#     visit_date,
#     start_time,
#     duration_hours,
#     booking_id,
# ) -> str:
#     user_id = callback.from_user.id
#     user = await get_user_by_tg_id(
#         user_id,
#     )
#     # room = await get_space_by_id(room_id)
#     tariff = await get_tariff_by_id(tariff_id)
#     text = (
#         f"✅ Поступил новый запрос на переговорную: \n\n"
#         f"├ <b>Имя:</b> {user.name}\n"
#         f"├ <b>Телефон:</b> {user.contact}\n"
#         f"├ <b>Email:</b> {user.email}\n"
#         f"├ <b>Пользователь TG:</b> @{user.tg_username}\n"
#         f"├ <b>Место:</b> {tariff.name}\n"
#         f"├ <b>Дата посещения:</b> {visit_date}\n"
#         f"├ <b>Время посещения:</b> {start_time}\n"
#         f"└ <b>Продолжительность:</b> {duration_hours} ч.\n"
#     )
#     # # Объединяем дату и время в одну строку и преобразуем в объект datetime
#     # combined_datetime = datetime.strptime(
#     #     f"{visit_date} {start_time}", "%d.%m.%Y %H:%M"
#     # )
#     #
#     # # Форматируем объект datetime в нужный формат
#     # formatted_datetime = combined_datetime.strftime("%Y-%m-%d %H:%M:%S")
#     # method = "create_record"
#     # rubitime_id = await rubitime(
#     #     method,
#     #     {
#     #         "service_id": tariff.service_id,
#     #         "name": user.name,
#     #         "email": user.email,
#     #         "phone": user.contact,
#     #         "record": formatted_datetime,
#     #         "duration": duration_hours * 60,
#     #     },
#     # )
#     # # await update_booking_mr_rubitime(booking_id, rubitime_id)
#     # await update_booking_fields(booking_id=booking_id, rubitime_id=rubitime_id)
#     return text
# import logging
# from datetime import datetime, timedelta, timezone
# from typing import Any
#
# from aiogram import Router, F, Bot
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import StatesGroup, State
# from aiogram.types import CallbackQuery
# from fluent.runtime import FluentLocalization
#
# from app.user_kb import keyboards as kb
# from app.admin_kb import keyboards as admin_kb
# from app.calendar_keyboard import custom_calendar as cl
# from app.database.requests import (
#     get_user_by_tg_id,
#     is_time_available,
#     get_tariff_by_id,
#     create_booking,
# )
# from app.user_handlers.booking import BookingTariff
# from config import BOT_ADMINS
# from filters import IsUserFilter
# from tools.tools import send_localized_message
#
# logger = logging.getLogger(__name__)
#
# meeting_room_router = Router()
#
# # Ограничиваем доступ только для пользователей
# meeting_room_router.message.filter(IsUserFilter(is_user=True))
# meeting_room_router.callback_query.filter(IsUserFilter(is_user=True))
#
#
# class RegMeetingRoom(StatesGroup):
#     """Состояния для бронирования переговорной комнаты."""
#
#     visit_date = State()  # Выбор даты визита
#     visit_time = State()  # Выбор времени начала
#     duration = State()  # Выбор продолжительности
#
#
# @meeting_room_router.callback_query(F.data.startswith("space_"), BookingTariff.tariff)
# async def booking_meeting_room(
#     callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
# ) -> None:
#     """Начало бронирования переговорной комнаты."""
#     try:
#         tariff_id = int(callback.data.split("_")[1])  # Преобразуем в int
#     except ValueError:
#         logger.error(f"Неверный tariff_id: {callback.data}")
#         await send_localized_message(callback, l10n, "invalid_tariff", show_alert=True)
#         return
#     await state.update_data(tariff_id=tariff_id)
#     calendar = cl.CustomCalendar()
#     locale = callback.from_user.language_code or "en"
#     if locale not in ["en", "ru"]:
#         locale = "en"
#     await send_localized_message(
#         callback,
#         l10n,
#         "select_date",
#         reply_markup=await calendar.generate_calendar(
#             datetime.now().year, datetime.now().month, "main_menu", locale=locale
#         ),
#     )
#     await state.set_state(RegMeetingRoom.visit_date)
#
#
# @meeting_room_router.callback_query(
#     F.data.startswith("calendar:"), RegMeetingRoom.visit_date
# )
# async def set_visit_date(
#     callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
# ) -> None:
#     """Выбор даты бронирования."""
#     calendar = cl.CustomCalendar()
#     locale = callback.from_user.language_code or "en"
#     if locale not in ["en", "ru"]:
#         locale = "en"
#     selected_date = await calendar.handle_callback(callback, "main_menu", locale=locale)
#
#     if selected_date:
#         if selected_date.date() < datetime.now().date():
#             await send_localized_message(
#                 callback, l10n, "date_in_past", show_alert=True
#             )
#             return
#         await state.update_data(visit_date=selected_date.strftime("%d.%m.%Y"))
#         await send_localized_message(
#             callback,
#             l10n,
#             "select_time",
#             reply_markup=await kb.time_intervals(selected_date, l10n=l10n),
#         )
#         await state.set_state(RegMeetingRoom.visit_time)
#
#
# @meeting_room_router.callback_query(
#     F.data.startswith("time_"), RegMeetingRoom.visit_time
# )
# async def process_time_selection(
#     callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
# ) -> None:
#     """Выбор времени начала бронирования."""
#     selected_time = callback.data.split("_")[1]
#     await state.update_data(start_time=selected_time)
#     await send_localized_message(
#         callback,
#         l10n,
#         "select_duration",
#         reply_markup=await kb.duration_options(l10n=l10n),
#     )
#     await state.set_state(RegMeetingRoom.duration)
#
#
# @meeting_room_router.callback_query(
#     F.data.startswith("duration:"), RegMeetingRoom.duration
# )
# async def change_duration(
#     callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
# ) -> None:
#     """Изменение продолжительности бронирования."""
#     action = callback.data.split(":")[1]
#     data = await state.get_data()
#     current_value = data.get("duration", 1)
#
#     if action == "increase":
#         current_value += 1
#     elif action == "decrease":
#         if current_value <= 1:
#             await send_localized_message(
#                 callback, l10n, "error_duration", show_alert=True
#             )
#             return
#         current_value -= 1
#
#     await state.update_data(duration=current_value)
#     await callback.message.edit_reply_markup(
#         reply_markup=await kb.duration_options(current_value=current_value, l10n=l10n)
#     )
#
#
# async def create_meeting_booking(
#     user_id: int,
#     tariff_id: str,
#     visit_date: str,  # Оставляем строку для отображения
#     start_time: str,
#     duration_hours: int,
#     l10n: FluentLocalization,
# ) -> Any:
#     """Создание бронирования переговорной комнаты."""
#     visit_date_dt = datetime.strptime(visit_date, "%d.%m.%Y").replace(
#         tzinfo=timezone.utc
#     )
#     start_dt = datetime.strptime(start_time, "%H:%M").replace(
#         year=visit_date_dt.year,
#         month=visit_date_dt.month,
#         day=visit_date_dt.day,
#         tzinfo=timezone.utc,
#     )
#     end_dt = start_dt + timedelta(hours=duration_hours)
#
#     booking = await create_booking(
#         user_tg_id=user_id,
#         tariff_id=tariff_id,
#         visit_date=visit_date_dt,
#         start_time=start_dt,
#         end_time=end_dt,
#         duration=duration_hours,
#     )
#     return booking
#
#
# async def notify_meeting_admins(
#     bot: Bot,
#     booking_id: int,
#     # user_name: str,
#     # user_tg_username: str,
#     tariff_id: str,  # Меняем tariff_name на tariff_id
#     visit_date: str,
#     start_time: str,
#     duration_hours: int,
#     admins: list[int],
#     l10n: FluentLocalization,
#     callback: CallbackQuery,
# ) -> None:
#     """Уведомление администраторов о новом бронировании."""
#     text = await generate_booking_message(
#         callback,
#         tariff_id=tariff_id,
#         visit_date=visit_date,
#         start_time=start_time,
#         duration_hours=duration_hours,
#         # booking_id=booking_id,
#     )
#     for admin in admins:
#         try:
#             await bot.send_message(
#                 admin,
#                 text,
#                 parse_mode="HTML",
#                 reply_markup=await admin_kb.approval(booking_id, l10n=l10n),
#             )
#         except Exception as e:
#             logger.error(f"Ошибка отправки администратору {admin}: {e}")
#
#
# @meeting_room_router.callback_query(F.data.startswith("confirm_duration:"))
# async def confirm_duration(
#     callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
# ) -> None:
#     """Подтверждение бронирования переговорной комнаты."""
#     duration_hours = int(callback.data.split(":")[1])
#     await state.update_data(duration=duration_hours)
#
#     data = await state.get_data()
#     visit_date_str = data["visit_date"]  # '22.02.2025'
#     start_time_str = data["start_time"]  # '15:00'
#     tariff_id = data["tariff_id"]
#     user_id = callback.from_user.id
#
#     # Преобразуем данные в datetime с часовым поясом
#     visit_date = datetime.strptime(visit_date_str, "%d.%m.%Y").replace(
#         tzinfo=timezone.utc
#     )
#     start_time = datetime.strptime(start_time_str, "%H:%M").replace(
#         year=visit_date.year,
#         month=visit_date.month,
#         day=visit_date.day,
#         tzinfo=timezone.utc,
#     )
#     end_time = start_time + timedelta(hours=duration_hours)
#
#     if await is_time_available(tariff_id, visit_date, start_time, end_time):
#         booking = await create_meeting_booking(
#             user_id, tariff_id, visit_date_str, start_time_str, duration_hours, l10n
#         )
#         await notify_meeting_admins(
#             callback.bot,
#             booking.id,
#             tariff_id,  # Передаем tariff_id вместо tariff.name
#             visit_date_str,
#             start_time_str,
#             duration_hours,
#             BOT_ADMINS,
#             l10n,
#             callback,
#         )
#         await send_localized_message(
#             callback,
#             l10n,
#             "request_send",
#             reply_markup=await kb.user_main(l10n=l10n),
#         )
#     else:
#         await send_localized_message(
#             callback,
#             l10n,
#             "time_is_already_taken",
#             reply_markup=await kb.user_main(l10n=l10n),
#         )
#     await state.clear()
#
#
# async def generate_booking_message(
#     callback: CallbackQuery,
#     tariff_id: str,
#     visit_date: str,
#     start_time: str,
#     duration_hours: int,
# ) -> str:
#     """Генерация сообщения о бронировании для администраторов."""
#     user = await get_user_by_tg_id(callback.from_user.id)
#     tariff = await get_tariff_by_id(tariff_id)
#     return (
#         f"✅ <b>Поступил новый запрос на переговорную:</b>\n\n"
#         f"├ <b>Имя:</b> {user.name}\n"
#         f"├ <b>Телефон:</b> {user.contact}\n"
#         f"├ <b>Email:</b> {user.email}\n"
#         f"├ <b>Пользователь TG:</b> @{user.tg_username}\n"
#         f"├ <b>Место:</b> {tariff.name}\n"
#         f"├ <b>Дата:</b> {visit_date}\n"
#         f"├ <b>Время:</b> {start_time}\n"
#         f"└ <b>Продолжительность:</b> {duration_hours} ч."
#     )
import logging
from datetime import timezone
from typing import Any

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery
from fluent.runtime import FluentLocalization

import tgbot.keyboards.user_kb.keyboards as kb
import tgbot.keyboards.admin_kb.keyboards as admin_kb

import tgbot.keyboards.calendar_keyboard.custom_calendar as cl
from tgbot.database.requests import (
    get_user_by_tg_id,
    is_time_available,
    get_tariff_by_id,
    create_booking,
)

# from app.rubitime import rubitime
from tgbot.handlers.user_handlers.booking import BookingTariff
from tgbot.config import BOT_ADMINS
from tgbot.filters import IsUserFilter
from tgbot.tools.tools import send_localized_message

logger = logging.getLogger(__name__)

meeting_room_router = Router()

# Ограничиваем доступ только для пользователей
meeting_room_router.message.filter(IsUserFilter(is_user=True))
meeting_room_router.callback_query.filter(IsUserFilter(is_user=True))


class RegMeetingRoom(StatesGroup):
    """Состояния для бронирования переговорной комнаты."""

    visit_date = State()  # Выбор даты визита
    visit_time = State()  # Выбор времени начала
    duration = State()  # Выбор продолжительности


@meeting_room_router.callback_query(F.data.startswith("space_"), BookingTariff.tariff)
async def booking_meeting_room(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
) -> None:
    """Начало бронирования переговорной комнаты."""
    await callback.answer()
    try:
        tariff_id = int(callback.data.split("_")[1])  # Преобразуем в int
    except ValueError:
        logger.error("Неверный tariff_id: %s", callback.data)
        await send_localized_message(callback, l10n, "invalid_tariff", show_alert=True)
        return
    await state.update_data(tariff_id=tariff_id)
    calendar = cl.CustomCalendar()
    locale = callback.from_user.language_code or "en"
    if locale not in ["en", "ru"]:
        locale = "en"
    try:
        await send_localized_message(
            callback,
            l10n,
            "select_date",
            reply_markup=await calendar.generate_calendar(
                datetime.now().year, datetime.now().month, "main_menu", locale=locale
            ),
        )
    except TelegramBadRequest as e:
        logger.error(
            "Не удалось отправить сообщение в booking_meeting_room: %s", str(e)
        )
        return
    await state.set_state(RegMeetingRoom.visit_date)


@meeting_room_router.callback_query(
    F.data.startswith("calendar:"), RegMeetingRoom.visit_date
)
async def set_visit_date(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
) -> None:
    """Выбор даты бронирования."""
    calendar = cl.CustomCalendar()
    locale = callback.from_user.language_code or "en"
    if locale not in ["en", "ru"]:
        locale = "en"
    selected_date = await calendar.handle_callback(callback, "main_menu", locale=locale)
    if selected_date and selected_date.date() < datetime.now().date():
        await send_localized_message(callback, l10n, "date_in_past", show_alert=True)
        return
    if selected_date:
        await state.update_data(visit_date=selected_date.strftime("%d.%m.%Y"))
        try:
            await send_localized_message(
                callback,
                l10n,
                "select_time",
                reply_markup=await kb.time_intervals(selected_date, l10n=l10n),
            )
        except TelegramBadRequest as e:
            logger.error("Не удалось отправить сообщение в set_visit_date: %s", str(e))
            return
        await state.set_state(RegMeetingRoom.visit_time)


@meeting_room_router.callback_query(
    F.data.startswith("time_"), RegMeetingRoom.visit_time
)
async def process_time_selection(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
) -> None:
    """Выбор времени начала бронирования."""
    selected_time = callback.data.split("_")[1]
    try:
        # Проверка формата HH:MM
        datetime.strptime(selected_time, "%H:%M")
    except ValueError:
        logger.error("Некорректный формат времени: %s", selected_time)
        await send_localized_message(callback, l10n, "invalid_time", show_alert=True)
        return
    await state.update_data(start_time=selected_time)
    try:
        await send_localized_message(
            callback,
            l10n,
            "select_duration",
            reply_markup=await kb.duration_options(l10n=l10n),
        )
    except TelegramBadRequest as e:
        logger.error(
            "Не удалось отправить сообщение в process_time_selection: %s", str(e)
        )
        return
    await state.set_state(RegMeetingRoom.duration)


@meeting_room_router.callback_query(
    F.data.startswith("duration:"), RegMeetingRoom.duration
)
async def change_duration(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
) -> None:
    """Изменение продолжительности бронирования."""
    action = callback.data.split(":")[1]
    data = await state.get_data()
    current_value = data.get("duration", 1)

    if action == "increase":
        current_value += 1
    elif action == "decrease":
        if current_value <= 1:
            await send_localized_message(
                callback, l10n, "error_duration", show_alert=True
            )
            return
        current_value -= 1

    await state.update_data(duration=current_value)
    try:
        await callback.message.edit_reply_markup(
            reply_markup=await kb.duration_options(
                current_value=current_value, l10n=l10n
            )
        )
    except TelegramBadRequest as e:
        logger.error("Не удалось обновить клавиатуру в change_duration: %s", str(e))


async def create_meeting_booking(
    user_id: int,
    tariff_id: str,
    visit_date: str,
    start_time: str,
    duration_hours: int,
    # l10n: FluentLocalization,
) -> Any:
    """Создание бронирования переговорной комнаты."""
    try:
        tariff_id_int = int(tariff_id)
        visit_date_dt = datetime.strptime(visit_date, "%d.%m.%Y").replace(
            tzinfo=timezone.utc
        )
        start_dt = datetime.strptime(start_time, "%H:%M").replace(
            year=visit_date_dt.year,
            month=visit_date_dt.month,
            day=visit_date_dt.day,
            tzinfo=timezone.utc,
        )
        end_dt = start_dt + timedelta(hours=duration_hours)
    except ValueError as e:
        logger.error(
            "Ошибка преобразования даты/времени в create_meeting_booking: %s", str(e)
        )
        raise
    try:
        booking = await create_booking(
            user_tg_id=user_id,
            tariff_id=tariff_id_int,
            visit_date=visit_date_dt,
            start_time=start_dt,
            end_time=end_dt,
            duration=duration_hours,
        )
    except Exception as e:
        logger.error("Ошибка создания бронирования: %s", str(e))
        raise
    return booking


async def notify_meeting_admins(
    bot: Bot,
    booking_id: int,
    tariff_id: str,
    visit_date: str,
    start_time: str,
    duration_hours: int,
    admins: list[int],
    l10n: FluentLocalization,
    callback: CallbackQuery,
) -> None:
    """Уведомление администраторов о новом бронировании."""
    text = await generate_booking_message(
        callback, tariff_id, visit_date, start_time, duration_hours
    )
    for admin in admins:
        try:
            await bot.send_message(
                admin,
                text,
                parse_mode="HTML",
                reply_markup=await admin_kb.approval(booking_id, l10n=l10n),
            )
            logger.debug("Уведомление отправлено администратору %s", admin)
        except Exception as e:
            logger.error("Ошибка отправки администратору %s: %s", admin, str(e))


@meeting_room_router.callback_query(F.data.startswith("confirm_duration:"))
async def confirm_duration(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
) -> None:
    """Подтверждение бронирования переговорной комнаты."""
    await callback.answer()
    try:
        duration_hours = int(callback.data.split(":")[1])
    except ValueError:
        logger.error("Некорректная длительность: %s", callback.data)
        await send_localized_message(
            callback, l10n, "invalid_duration", show_alert=True
        )
        return
    await state.update_data(duration=duration_hours)
    data = await state.get_data()
    visit_date_str = data["visit_date"]
    start_time_str = data["start_time"]
    tariff_id = data["tariff_id"]
    user_id = callback.from_user.id

    try:
        visit_date = datetime.strptime(visit_date_str, "%d.%m.%Y").replace(
            tzinfo=timezone.utc
        )
        start_time = datetime.strptime(start_time_str, "%H:%M").replace(
            year=visit_date.year,
            month=visit_date.month,
            day=visit_date.day,
            tzinfo=timezone.utc,
        )
        end_time = start_time + timedelta(hours=duration_hours)
    except ValueError as e:
        logger.error(
            "Ошибка преобразования даты/времени в confirm_duration: %s", str(e)
        )
        await send_localized_message(
            callback, l10n, "invalid_date_time", show_alert=True
        )
        return
    now = datetime.now(timezone.utc)
    if start_time < now:
        logger.debug(
            "Время в прошлом: visit_date=%s, start_time=%s, now=%s",
            visit_date,
            start_time,
            now,
        )
        await send_localized_message(
            callback,
            l10n,
            "time_in_past",
            reply_markup=await kb.user_main(l10n=l10n),
        )
        await state.clear()
        return

    if await is_time_available(tariff_id, visit_date, start_time, end_time):
        try:
            booking = await create_meeting_booking(
                user_id, tariff_id, visit_date_str, start_time_str, duration_hours
            )
            await notify_meeting_admins(
                callback.bot,
                booking.id,
                tariff_id,
                visit_date_str,
                start_time_str,
                duration_hours,
                BOT_ADMINS,
                l10n,
                callback,
            )
            await send_localized_message(
                callback,
                l10n,
                "request_send",
                reply_markup=await kb.user_main(l10n=l10n),
            )
        except Exception as e:
            logger.error("Ошибка создания бронирования в confirm_duration: %s", str(e))
            await send_localized_message(
                callback, l10n, "booking_error", show_alert=True
            )
    else:
        await send_localized_message(
            callback,
            l10n,
            "time_is_already_taken",
            reply_markup=await kb.user_main(l10n=l10n),
        )
    await state.clear()


async def generate_booking_message(
    callback: CallbackQuery,
    tariff_id: str,
    visit_date: str,
    start_time: str,
    duration_hours: int,
) -> str:
    """Генерация сообщения о бронировании для администраторов."""
    user = await get_user_by_tg_id(callback.from_user.id)
    tariff = await get_tariff_by_id(tariff_id)
    if not user or not tariff:
        logger.error(
            "Не удалось получить данные пользователя или тарифа: user=%s, tariff=%s",
            user,
            tariff,
        )
        return "Ошибка: данные недоступны"
    return (
        f"✅ <b>Поступил новый запрос на переговорную:</b>\n\n"
        f"├ <b>Имя:</b> {user.name}\n"
        f"├ <b>Телефон:</b> {user.contact}\n"
        f"├ <b>Email:</b> {user.email}\n"
        f"├ <b>Пользователь TG:</b> @{user.tg_username}\n"
        f"├ <b>Место:</b> {tariff.name}\n"
        f"├ <b>Дата:</b> {visit_date}\n"
        f"├ <b>Время:</b> {start_time}\n"
        f"└ <b>Продолжительность:</b> {duration_hours} ч."
    )
