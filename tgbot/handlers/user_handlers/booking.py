# import asyncio
# from datetime import datetime
# from typing import Any
#
# from aiogram import Router, F
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import StatesGroup, State
# from aiogram.types import CallbackQuery, Message
# from fluent.runtime import FluentLocalization
# from yookassa import Payment
#
# import tgbot.keyboards.user_kb.keyboards as kb
#
# import tgbot.keyboards.admin_kb.keyboards as admin_kb
#
# import tgbot.keyboards.calendar_keyboard.custom_calendar as cl
# from tgbot.database.requests import (
#     get_tariff_by_id,
#     check_promocode,
#     create_booking,
#     increment_user_successful_bookings,
#     increase_usage_of_promocodes,
#     update_booking_fields,
#     get_user_by_tg_id,
# )
# from tgbot.rubitime import rubitime
# from tgbot.handlers.user_handlers.payment import create_payment, cancel_payment_handler
# from concurrent.futures import ThreadPoolExecutor
#
# from tgbot.config import BOT_ADMINS
# from tgbot.filters import IsUserFilter
# from tgbot.tools.tools import send_localized_message
#
# executor = ThreadPoolExecutor(max_workers=5)  # Определяем пул потоков
#
# booking_router = Router()
# # Применяем фильтр для всех хэндлеров на уровне роутера
# booking_router.message.filter(IsUserFilter(is_user=True))
# booking_router.callback_query.filter(IsUserFilter(is_user=True))
#
#
# class BookingTariff(StatesGroup):
#     tariff = State()
#     date = State()
#     promocode = State()
#     payment = State()
#     status_payment = State()
#
#
# @booking_router.callback_query(F.data == "booking")
# async def show_tariffs(
#     callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
# ):
#     await state.set_state(BookingTariff.tariff)
#     await send_localized_message(
#         callback,
#         l10n,
#         "select_tariff",
#         reply_markup=await kb.tariffs(callback.from_user.id, l10n=l10n),
#     )
#
#
# @booking_router.callback_query(F.data.startswith("tariff_"), BookingTariff.tariff)
# async def set_tariff(
#     callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
# ):
#     await send_localized_message(
#         callback,
#         l10n,
#         "choice_made",
#         show_alert=True,
#     )
#     await state.update_data(tariff=callback.data.split("_")[1])
#     tariff = await get_tariff_by_id(callback.data.split("_")[1])
#     description_text = tariff.description
#     calendar = cl.CustomCalendar()
#     locale = callback.from_user.language_code
#     if locale not in ["en", "ru"]:
#         locale = "en"
#     await callback.message.edit_text(
#         f"{description_text}\n\n" f"{l10n.format_value('select_date')}\n",
#         reply_markup=await calendar.generate_calendar(
#             datetime.now().year, datetime.now().month, "main_menu", locale=locale
#         ),
#     )
#     await state.set_state(BookingTariff.date)
#
#
# @booking_router.callback_query(F.data.startswith("calendar:"), BookingTariff.date)
# async def set_date(
#     callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
# ):
#     calendar = cl.CustomCalendar()
#     locale = callback.from_user.language_code
#     if locale not in ["en", "ru"]:
#         locale = "en"
#     selected_date = await calendar.handle_callback(callback, "main_menu", locale=locale)
#
#     if selected_date:
#         await state.update_data(visit_date=selected_date)
#         await send_localized_message(
#             callback,
#             l10n,
#             "enter_promo",
#         )
#         await state.set_state(BookingTariff.promocode)
#
#
# @booking_router.message(BookingTariff.promocode)
# async def set_promocode(message: Message, state: FSMContext, l10n: FluentLocalization):
#     if message.text == "/skip_promo":
#         await state.update_data(discount=0, promocode_id=None)
#         # Продолжить обработку без промокода
#         promocode_text = l10n.format_value("promo_skipped")
#         await state.set_state(BookingTariff.payment)
#         await get_payment(message, promocode_text, state, l10n=l10n)
#         return
#     # Получаем введённый промокод
#     entered_promocode = message.text.strip()
#     # Проверяем промокод
#     promocode_discount, promocode_id = await check_promocode(entered_promocode)
#     if promocode_discount is not None:
#         await state.update_data(
#             discount=promocode_discount,
#             promocode_id=promocode_id,
#             promocode_name=entered_promocode,
#         )
#         promocode_text = f"{l10n.format_value('promo_accepted')} {promocode_discount}%!"
#         await state.set_state(BookingTariff.payment)
#         await get_payment(message, promocode_text, state, l10n)
#     else:
#         # Предлагаем пользователю пропустить или попробовать ввести промокод еще раз
#         await send_localized_message(
#             message,
#             l10n,
#             "promo_not_active",
#         )
#
#
# # @booking_router.message(BookingTariff.payment)
# # async def get_payment(message: Message, promocode_text: str, state: FSMContext):
# #     data = await state.get_data()
# #     user_tg_id = message.from_user.id
# #     visit_date = data.get("visit_date")
# #     tariff_id = data.get("tariff")
# #     discount = data.get("discount", 0)
# #     promocode_id = data.get("promocode_id")
# #     # promocode_name = data.get("promocode_name")
# #
# #     # Получаем тариф для расчета суммы
# #     tariff = await get_tariff_by_id(tariff_id)
# #     amount_wo_discount = tariff.price
# #     amount_w_discount = amount_wo_discount * (1 - (discount / 100))
# #
# #     await state.update_data(amount_w_discount=amount_w_discount)
# #
# #     # first_line = tariff.description.split('\n')[0]
# #     # formatted_description = f"{first_line}({visit_date}) за {amount_w_discount} рублей"
# #     formatted_visit_date = visit_date.strftime("%d.%m.%Y")
# #     formatted_description = (
# #         f"{tariff.name}({formatted_visit_date}) за {amount_w_discount} рублей"
# #     )
# #
# #     # reservation = await create_reservation(
# #     #     user_id=user_id,
# #     #     visit_date=visit_date,
# #     #     tariff_name=tariff.name,
# #     #     amount_wo_discount=amount_wo_discount,
# #     #     amount_w_discount=amount_w_discount,
# #     #     promocode_name=promocode_name,
# #     # )
# #     booking = await create_booking(
# #         user_tg_id=user_tg_id,
# #         visit_date=visit_date,
# #         tariff_id=tariff_id,
# #         amount_wo_discount=amount_wo_discount,
# #         amount_w_discount=amount_w_discount,
# #         promocode_id=promocode_id,
# #     )
# #
# #     if amount_w_discount == 0:
# #         await state.update_data(payment_status="succeeded")
# #         await message.answer(
# #             f"{promocode_text}\n\n"
# #             f"Бронь успешно подтверждена! Ждём вас в назначенный день.",
# #             reply_markup=await kb.user_main(),
# #         )
# #         # await update_reservation_fields(reservation_id=reservation.id, paid=True, rubitime_id=rubitime_id)
# #         await increment_user_successful_bookings(
# #             message.from_user.id,
# #         )
# #         await increase_usage_of_promocodes(promocode_id)
# #
# #         booking_text, rubitime_id = await generate_booking_message(message, state)
# #         # await update_reservation_fields(
# #         #     reservation_id=reservation.id, paid=True, rubitime_id=rubitime_id
# #         # )
# #         await update_booking_fields(
# #             booking_id=booking.id, paid=True, confirmed=True, rubitime_id=rubitime_id
# #         )
# #         for admin in BOT_ADMINS:
# #             await message.bot.send_message(
# #                 admin,
# #                 booking_text,
# #                 parse_mode="HTML",
# #                 reply_markup=await admin_kb.create_buttons(),
# #             )
# #
# #         await state.clear()
# #         return
# #     else:
# #
# #         payment_id, confirmation_url = await create_payment(
# #             formatted_description, amount=amount_w_discount
# #         )
# #         # await update_reservation_fields(
# #         #     reservation_id=reservation.id, payment_id=payment_id
# #         # )
# #         await update_booking_fields(booking_id=booking.id, payment_id=payment_id)
# #         # Сохраняем ID бронирования в FSM
# #         await state.update_data(booking_id=booking.id, payment_id=payment_id)
# #         try:
# #             # Отправляем сообщение о платеже и сохраняем его объект
# #             payment_message = await message.answer(
# #                 text=f"{promocode_text}\n\n{tariff.description}",
# #                 reply_markup=await kb.payment(
# #                     confirmation_url, amount=amount_w_discount
# #                 ),
# #             )
# #             # Сохраняем объект сообщения в состоянии
# #             await state.update_data(payment_message_id=payment_message.message_id)
# #             await state.set_state(BookingTariff.status_payment)
# #             # print(payment_message)
# #
# #             # Начинаем процесс проверки статуса платежа
# #             await asyncio.create_task(
# #                 poll_payment_status(message, promocode_text, state)
# #             )
# #         except Exception as e:
# #             await message.answer(
# #                 "Произошла ошибка при создании платежа. Попробуйте позже."
# #             )
# @booking_router.message(BookingTariff.payment)
# async def get_payment(
#     message: Message, promocode_text: str, state: FSMContext, l10n: FluentLocalization
# ):
#     data = await state.get_data()
#     user_tg_id = message.from_user.id
#     visit_date = data.get("visit_date")
#     tariff_id = data.get("tariff")
#     discount = data.get("discount", 0)
#     promocode_id = data.get("promocode_id")
#     # Получаем тариф для расчета суммы
#     tariff = await get_tariff_by_id(tariff_id)
#     amount_wo_discount = tariff.price
#     amount_w_discount = amount_wo_discount * (1 - (discount / 100))
#     await state.update_data(amount_w_discount=amount_w_discount)
#     formatted_visit_date = visit_date.strftime("%d.%m.%Y")
#     formatted_description = (
#         f"{tariff.name}({formatted_visit_date}) за {amount_w_discount} рублей"
#     )
#     booking = await create_booking(
#         user_tg_id=user_tg_id,
#         visit_date=visit_date,
#         tariff_id=tariff_id,
#         amount_wo_discount=amount_wo_discount,
#         amount_w_discount=amount_w_discount,
#         promocode_id=promocode_id,
#     )
#     if amount_w_discount == 0:
#         await state.update_data(payment_status="succeeded")
#         await message.answer(
#             f"{promocode_text}\n\n"
#             f"{l10n.format_value('reservation_successfully_confirmed')}",
#             reply_markup=await kb.user_main(l10n=l10n),
#         )
#         await increment_user_successful_bookings(
#             message.from_user.id,
#         )
#         await increase_usage_of_promocodes(promocode_id)
#         booking_text, rubitime_id = await generate_booking_message(message, state)
#         await update_booking_fields(
#             booking_id=booking.id, paid=True, confirmed=True, rubitime_id=rubitime_id
#         )
#         for admin in BOT_ADMINS:
#             await message.bot.send_message(
#                 admin,
#                 booking_text,
#                 parse_mode="HTML",
#                 reply_markup=await admin_kb.create_buttons(l10n=l10n),
#             )
#         await state.clear()
#         return
#     else:
#         payment_id, confirmation_url = await create_payment(
#             formatted_description, amount=amount_w_discount, l10n=l10n
#         )
#         await update_booking_fields(booking_id=booking.id, payment_id=payment_id)
#         # Сохраняем ID бронирования в FSM
#         await state.update_data(booking_id=booking.id, payment_id=payment_id)
#         # try:
#         # Отправляем сообщение о платеже и сохраняем его объект
#         payment_message = await message.answer(
#             text=f"{promocode_text}\n\n{tariff.description}",
#             reply_markup=await kb.payment(
#                 confirmation_url, amount=amount_w_discount, l10n=l10n
#             ),
#         )
#         # Сохраняем объект сообщения в состоянии
#         await state.update_data(payment_message_id=payment_message.message_id)
#         await state.set_state(BookingTariff.status_payment)
#
#         # Начинаем процесс проверки статуса платежа
#         await asyncio.create_task(
#             poll_payment_status(message, promocode_text, state, l10n)
#         )
#         # except Exception:
#         #     await send_localized_message(
#         #         message,
#         #         l10n,
#         #         "error",  # Ключ для локализованного текста регистрации
#         #     )
#
#
# async def check_payment_status(payment_id: str) -> bool:
#     loop = asyncio.get_event_loop()
#     # try:
#     # Запускаем синхронный метод в пуле потоков
#     payment = await loop.run_in_executor(executor, Payment.find_one, payment_id)
#     return payment.status == "succeeded"
#     # except Exception:
#     #     return False
#
#
# # async def poll_payment_status(message: Message, promocode_text: str, state: FSMContext):
# #     delay = 5
# #     data = await state.get_data()
# #     booking_id = data.get("booking_id")
# #     payment_id = data.get("payment_id")
# #     payment_message_id = data.get("payment_message_id")
# #     promocode_id = data.get("promocode_id")
# #     while True:
# #         payment_status = (await state.get_data()).get("payment_status")
# #         if payment_status == "cancelled":
# #             await state.clear()
# #             break
# #         if await check_payment_status(payment_id):
# #             await message.bot.edit_message_text(
# #                 text=f"{promocode_text}\n\nБронь успешно подтверждена! Ждём вас в назначенный день.",
# #                 chat_id=message.chat.id,
# #                 message_id=payment_message_id,
# #                 reply_markup=await kb.user_main(),
# #             )
# #             await increment_user_successful_bookings(
# #                 message.from_user.id,
# #             )
# #             await increase_usage_of_promocodes(promocode_id)
# #             booking_text, rubitime_id = await generate_booking_message(message, state)
# #             await update_booking_fields(
# #                 booking_id=booking_id,
# #                 paid=True,
# #                 confirmed=True,
# #                 rubitime_id=rubitime_id,
# #             )
# #             for admin in BOT_ADMINS:
# #                 await message.bot.send_message(
# #                     admin,
# #                     booking_text,
# #                     parse_mode="HTML",
# #                     # reply_markup=await admin_kb.back_button("main_menu"),
# #                     reply_markup=await admin_kb.create_buttons(),
# #                 )
# #
# #             await state.clear()
# #             break
# #
# #         await asyncio.sleep(delay)
# async def poll_payment_status(
#     message: Message, promocode_text: str, state: FSMContext, l10n: FluentLocalization
# ):
#     delay = 5
#     data = await state.get_data()
#     booking_id = data.get("booking_id")
#     payment_id = data.get("payment_id")
#     payment_message_id = data.get("payment_message_id")
#     promocode_id = data.get("promocode_id")
#     while True:
#         payment_status = (await state.get_data()).get("payment_status")
#         if payment_status == "cancelled":
#             await state.clear()
#             break
#         if await check_payment_status(payment_id):
#             await message.bot.edit_message_text(
#                 text=f"{promocode_text}\n\n{l10n.format_value('reservation_successfully_confirmed')}",
#                 chat_id=message.chat.id,
#                 message_id=payment_message_id,
#                 reply_markup=await kb.user_main(l10n=l10n),
#             )
#             await increment_user_successful_bookings(
#                 message.from_user.id,
#             )
#             await increase_usage_of_promocodes(promocode_id)
#             booking_text, rubitime_id = await generate_booking_message(message, state)
#             await update_booking_fields(
#                 booking_id=booking_id,
#                 paid=True,
#                 confirmed=True,
#                 rubitime_id=rubitime_id,
#             )
#             for admin in BOT_ADMINS:
#                 await message.bot.send_message(
#                     admin,
#                     booking_text,
#                     parse_mode="HTML",
#                     reply_markup=await admin_kb.create_buttons(l10n=l10n),
#                 )
#             await state.clear()
#             break
#         await asyncio.sleep(delay)
#
#
# @booking_router.callback_query(F.data == "cancel_pay", BookingTariff.status_payment)
# async def cancel_payment(
#     callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
# ):
#     await cancel_payment_handler(callback, state, l10n=l10n)
#
#
# async def generate_booking_message(
#     message: Message, state: FSMContext
# ) -> tuple[str, Any]:
#     user_id = message.from_user.id
#     user = await get_user_by_tg_id(
#         user_id,
#     )
#     data = await state.get_data()
#     visit_date = data.get("visit_date")
#     formatted_visit_date = visit_date.strftime("%d.%m.%Y")
#     rubitime_formatted_visit_date = visit_date.strftime("%Y-%m-%d") + " 09:00:00"
#     tariff_id = data.get("tariff")
#     amount = data.get("amount_w_discount")
#     tariff = await get_tariff_by_id(tariff_id)
#     promocode_name = data.get("promocode_name")
#     discount = data.get("discount")
#     text = (
#         f"✅ Поступила новая запись: \n\n"
#         f"├ <b>Имя:</b> {user.name}\n"
#         f"├ <b>Телефон:</b> {user.contact}\n"
#         f"├ <b>Email:</b> {user.email}\n"
#         f"├ <b>Пользователь TG:</b> @{user.tg_username}\n"
#         f"├ <b>Дата посещения:</b> {formatted_visit_date}\n"
#         f"├ <b>Стоимость:</b> {amount} рублей\n"
#         f"├ <b>Промокод:</b> {promocode_name if promocode_name else '-'}\n"
#         f"└ <b>Тариф:</b> {tariff.name}"
#     )
#     method = "create_record"
#     rubitime_id = await rubitime(
#         method,
#         {
#             "service_id": tariff.service_id,
#             "name": user.name,
#             "email": user.email,
#             "phone": user.contact,
#             "record": rubitime_formatted_visit_date,
#             "comment": f"Промокод: {promocode_name if promocode_name else '-'}, скидка: {discount if discount else '-'}%",
#             "coupon": f"{promocode_name if promocode_name else '-'}",
#             "coupon_discount": f"{discount}%",
#         },
#     )
#     return text, rubitime_id
import logging

from typing import Tuple, Optional
import asyncio
from datetime import datetime
from typing import Any

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from fluent.runtime import FluentLocalization
from yookassa import Payment

import tgbot.keyboards.user_kb.keyboards as kb

import tgbot.keyboards.admin_kb.keyboards as admin_kb

import tgbot.keyboards.calendar_keyboard.custom_calendar as cl
from tgbot.database.requests import (
    get_tariff_by_id,
    check_promocode,
    create_booking,
    increment_user_successful_bookings,
    increase_usage_of_promocodes,
    update_booking_fields,
    get_user_by_tg_id,
)
from tgbot.rubitime import rubitime
from tgbot.handlers.user_handlers.payment import create_payment, cancel_payment_handler
from concurrent.futures import ThreadPoolExecutor

from tgbot.config import BOT_ADMINS
from tgbot.filters import IsUserFilter
from tgbot.tools.tools import send_localized_message

logger = logging.getLogger(__name__)
executor = ThreadPoolExecutor(max_workers=5)

booking_router = Router()

# Ограничиваем доступ только для пользователей
booking_router.message.filter(IsUserFilter(is_user=True))
booking_router.callback_query.filter(IsUserFilter(is_user=True))


class BookingTariff(StatesGroup):
    """Состояния для процесса бронирования."""

    tariff = State()  # Выбор тарифа
    date = State()  # Выбор даты
    promocode = State()  # Ввод промокода
    payment = State()  # Создание платежа
    status_payment = State()  # Проверка статуса платежа


@booking_router.callback_query(F.data == "booking")
async def show_tariffs(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
) -> None:
    """Отображение доступных тарифов для бронирования."""
    await callback.answer()
    await state.set_state(BookingTariff.tariff)
    await send_localized_message(
        callback,
        l10n,
        "select_tariff",
        reply_markup=await kb.tariffs(callback.from_user.id, l10n=l10n),
    )


@booking_router.callback_query(F.data.startswith("tariff_"), BookingTariff.tariff)
async def set_tariff(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
) -> None:
    """Выбор тарифа и переход к выбору даты."""
    await callback.answer()
    tariff_id = int(callback.data.split("_")[1])  # Преобразуем строку в int
    await state.update_data(tariff=tariff_id)
    tariff = await get_tariff_by_id(tariff_id)
    calendar = cl.CustomCalendar()
    locale = callback.from_user.language_code or "en"
    if locale not in ["en", "ru"]:
        locale = "en"
    await send_localized_message(
        callback,
        l10n,
        "choice_made",
        postfix=f"{tariff.description}\n{l10n.format_value('select_date')}",
        reply_markup=await calendar.generate_calendar(
            datetime.now().year, datetime.now().month, "main_menu", locale=locale
        ),
    )
    await state.set_state(BookingTariff.date)


@booking_router.callback_query(F.data.startswith("calendar:"), BookingTariff.date)
async def set_date(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
) -> None:
    """Выбор даты бронирования."""
    calendar = cl.CustomCalendar()
    locale = callback.from_user.language_code or "en"
    if locale not in ["en", "ru"]:
        locale = "en"
    selected_date = await calendar.handle_callback(callback, "main_menu", locale=locale)

    if selected_date:
        if selected_date < datetime.now():
            await send_localized_message(
                callback, l10n, "date_in_past", show_alert=True
            )
            return
        await state.update_data(visit_date=selected_date)
        await send_localized_message(callback, l10n, "enter_promo")
        await state.set_state(BookingTariff.promocode)


@booking_router.message(BookingTariff.promocode)
async def set_promocode(
    message: Message, state: FSMContext, l10n: FluentLocalization
) -> None:
    """Обработка промокода или его пропуск."""
    entered_promocode = message.text.strip()
    if entered_promocode == "/skip_promo":
        await state.update_data(discount=0, promocode_id=None)
        await get_payment(message, l10n.format_value("promo_skipped"), state, l10n)
        return

    promocode_discount, promocode_id = await check_promocode(entered_promocode)
    if promocode_discount is not None:
        await state.update_data(
            discount=promocode_discount,
            promocode_id=promocode_id,
            promocode_name=entered_promocode,
        )
        await get_payment(
            message,
            f"{l10n.format_value('promo_accepted')} {promocode_discount}%!",
            state,
            l10n,
        )
    else:
        await send_localized_message(message, l10n, "promo_not_active")


async def prepare_booking(
    user_id: int,
    visit_date: datetime,
    tariff_id: str,
    discount: float,
    promocode_id: Optional[int],
    l10n: FluentLocalization,
) -> Tuple[Any, float, str]:
    """Подготовка данных для бронирования."""
    tariff = await get_tariff_by_id(tariff_id)
    amount_wo_discount = tariff.price
    # amount_w_discount = amount_wo_discount * (1 - (discount / 100))
    amount_w_discount = int(
        amount_wo_discount * (1 - (discount / 100))
    )  # Преобразуем в int
    formatted_visit_date = visit_date.strftime("%d.%m.%Y")
    description = f"{tariff.name}({formatted_visit_date}) за {amount_w_discount} ₽"
    booking = await create_booking(
        user_tg_id=user_id,
        visit_date=visit_date,
        tariff_id=tariff_id,
        amount_wo_discount=amount_wo_discount,
        amount_w_discount=amount_w_discount,
        promocode_id=promocode_id,
    )
    return booking, amount_w_discount, description


async def handle_free_booking(
    message: Message,
    booking: Any,
    promocode_text: str,
    state: FSMContext,
    l10n: FluentLocalization,
) -> None:
    """Обработка бесплатного бронирования."""
    await state.update_data(payment_status="succeeded")
    await message.answer(
        f"{promocode_text}\n\n{l10n.format_value('reservation_successfully_confirmed')}",
        reply_markup=await kb.user_main(l10n=l10n),
    )
    await increment_user_successful_bookings(message.from_user.id)
    data = await state.get_data()  # Добавляем await
    await increase_usage_of_promocodes(data.get("promocode_id"))
    booking_text, rubitime_id = await generate_booking_message(message, state)
    await update_booking_fields(
        booking_id=booking.id, paid=True, confirmed=True, rubitime_id=rubitime_id
    )
    for admin in BOT_ADMINS:
        await message.bot.send_message(
            admin,
            booking_text,
            parse_mode="HTML",
            reply_markup=await admin_kb.create_buttons(l10n=l10n),
        )
    await state.clear()


@booking_router.message(BookingTariff.payment)
async def get_payment(
    message: Message, promocode_text: str, state: FSMContext, l10n: FluentLocalization
) -> None:
    """Создание бронирования и обработка платежа."""
    data = await state.get_data()
    user_id = message.from_user.id
    visit_date = data["visit_date"]
    tariff_id = data["tariff"]
    discount = data.get("discount", 0)
    promocode_id = data.get("promocode_id")

    booking, amount_w_discount, description = await prepare_booking(
        user_id, visit_date, tariff_id, discount, promocode_id, l10n
    )
    amount_w_discount_int = int(amount_w_discount)  # Преобразуем float в int
    await state.update_data(amount_w_discount=amount_w_discount)

    if amount_w_discount == 0:
        await handle_free_booking(message, booking, promocode_text, state, l10n)
    else:
        payment_id, confirmation_url = await create_payment(
            description, amount_w_discount_int, l10n
        )
        await update_booking_fields(booking_id=booking.id, payment_id=payment_id)
        await state.update_data(booking_id=booking.id, payment_id=payment_id)

        payment_message = await message.answer(
            f"{promocode_text}\n\n{description}",
            reply_markup=await kb.payment(
                confirmation_url, amount_w_discount_int, l10n
            ),
        )
        await state.update_data(payment_message_id=payment_message.message_id)
        await state.set_state(BookingTariff.status_payment)
        # Сохраняем задачу в состоянии
        task = asyncio.create_task(
            poll_payment_status(message, promocode_text, state, l10n)
        )
        await state.update_data(payment_task=task)


async def check_payment_status(payment_id: str) -> Optional[str]:
    """Проверка статуса платежа через YooKassa."""
    try:
        loop = asyncio.get_event_loop()
        payment = await loop.run_in_executor(executor, Payment.find_one, payment_id)
        return payment.status
    except Exception as e:
        logger.error(f"Ошибка проверки статуса платежа {payment_id}: {e}")
        return None


async def poll_payment_status(
    message: Message, promocode_text: str, state: FSMContext, l10n: FluentLocalization
) -> None:
    """Проверка статуса платежа с ограничением по времени."""
    data = await state.get_data()
    booking_id = data["booking_id"]
    payment_id = data["payment_id"]
    payment_message_id = data["payment_message_id"]
    promocode_id = data.get("promocode_id")
    max_attempts = 60  # Ждём максимум 5 минут (60 * 5 сек)
    delay = 5

    for _ in range(max_attempts):
        status = await check_payment_status(payment_id)
        if status == "succeeded":
            await message.bot.edit_message_text(
                f"{promocode_text}\n\n{l10n.format_value('reservation_successfully_confirmed')}",
                chat_id=message.chat.id,
                message_id=payment_message_id,
                reply_markup=await kb.user_main(l10n=l10n),
            )
            await increment_user_successful_bookings(message.from_user.id)
            await increase_usage_of_promocodes(promocode_id)
            booking_text, rubitime_id = await generate_booking_message(message, state)
            await update_booking_fields(
                booking_id=booking_id,
                paid=True,
                confirmed=True,
                rubitime_id=rubitime_id,
            )
            for admin in BOT_ADMINS:
                await message.bot.send_message(
                    admin,
                    booking_text,
                    parse_mode="HTML",
                    reply_markup=await admin_kb.create_buttons(l10n=l10n),
                )
            await state.clear()
            return
        elif status == "canceled":
            await state.update_data(payment_status="cancelled")
            await state.clear()
            return
        await asyncio.sleep(delay)

    # Если время вышло
    await message.bot.edit_message_text(
        l10n.format_value("payment_timeout"),
        chat_id=message.chat.id,
        message_id=payment_message_id,
        reply_markup=await kb.user_main(l10n=l10n),
    )
    await state.clear()


@booking_router.callback_query(F.data == "cancel_pay", BookingTariff.status_payment)
async def cancel_payment(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
) -> None:
    """Отмена платежа и фоновой задачи проверки."""
    await callback.answer()
    data = await state.get_data()
    payment_task = data.get("payment_task")
    if payment_task and not payment_task.done():
        payment_task.cancel()
        logger.info(
            f"Задача проверки платежа для payment_id {data['payment_id']} отменена"
        )
    await cancel_payment_handler(callback, state, l10n=l10n)


async def generate_booking_message(
    message: Message, state: FSMContext
) -> Tuple[str, Any]:
    """Генерация сообщения о бронировании для администраторов."""
    user = await get_user_by_tg_id(message.from_user.id)
    data = await state.get_data()
    visit_date = data["visit_date"]
    tariff_id = data["tariff"]
    amount = data["amount_w_discount"]
    tariff = await get_tariff_by_id(tariff_id)
    promocode_name = data.get("promocode_name", "-")
    discount = data.get("discount", 0)

    formatted_visit_date = visit_date.strftime("%d.%m.%Y")
    rubitime_date = visit_date.strftime("%Y-%m-%d") + " 09:00:00"
    text = (
        f"✅ <b>Новая запись:</b>\n\n"
        f"├ <b>Имя:</b> {user.name}\n"
        f"├ <b>Телефон:</b> {user.contact}\n"
        f"├ <b>Email:</b> {user.email}\n"
        f"├ <b>Пользователь TG:</b> @{user.tg_username}\n"
        f"├ <b>Дата:</b> {formatted_visit_date}\n"
        f"├ <b>Стоимость:</b> {amount} руб.\n"
        f"├ <b>Промокод:</b> {promocode_name}\n"
        f"└ <b>Тариф:</b> {tariff.name}"
    )
    rubitime_id = await rubitime(
        "create_record",
        {
            "service_id": tariff.service_id,
            "name": user.name,
            "email": user.email,
            "phone": user.contact,
            "record": rubitime_date,
            "comment": f"Промокод: {promocode_name}, скидка: {discount}%",
            "coupon": promocode_name,
            "coupon_discount": f"{discount}%",
        },
    )
    return text, rubitime_id
