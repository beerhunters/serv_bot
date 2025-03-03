import asyncio
import os
from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, FSInputFile
from fluent.runtime import FluentLocalization

import tgbot.keyboards.admin_kb.keyboards as kb
import tgbot.keyboards.calendar_keyboard.custom_month_cal as cl_month
import tgbot.keyboards.calendar_keyboard.custom_calendar as cl_day
from tgbot.handlers.admin_handlers.save_xlsx import save_report_to_excel
from tgbot.database.models import Ticket, User

# from app.database.models import Reservation
from tgbot.database.models import Booking
from tgbot.database.requests import (
    get_tickets_for_period,
    get_booking_for_period,
    get_new_visitors_for_period,
)

from tgbot.filters import IsAdminFilter

admin_report_router = Router()

# Применяем фильтр для всех хэндлеров на уровне роутера
admin_report_router.message.filter(IsAdminFilter(is_admin=True))
admin_report_router.callback_query.filter(IsAdminFilter(is_admin=True))


class Report(StatesGroup):
    report = State()
    period_option = State()
    period = State()
    report_tickets = State()
    report_bookings = State()
    period_for_nv = State()
    report_new_visitors = State()


@admin_report_router.callback_query(F.data == "admin_report")
async def report_menu(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    # await callback.answer("Функция в разработке", show_alert=True)
    await state.clear()
    await callback.message.edit_text(
        "Выберите отчет, который необходимо получить: ",
        reply_markup=await kb.report_options(l10n=l10n),
    )
    await state.set_state(Report.report)
    await callback.answer()


@admin_report_router.callback_query(F.data.startswith("report_"), Report.report)
async def select_report(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    report_name = callback.data.split("_")[1]
    await state.update_data(report_name=report_name)
    calendar = cl_month.CustomMonthCalendar()
    await callback.message.edit_text(
        f"Выберите необходимый месяц: ",
        reply_markup=await calendar.generate_month_calendar(
            datetime.now().year, "admin_report", locale="ru"
        ),
    )
    await state.set_state(Report.period)
    await callback.answer()


@admin_report_router.callback_query(F.data.startswith("calendar:"), Report.period)
async def set_period(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    calendar = cl_month.CustomMonthCalendar()
    result = await calendar.handle_callback(callback, "admin_report", locale="ru")
    if result:
        first_day_of_month, last_day_of_month = result
        await state.update_data(
            first_day_of_month=first_day_of_month.strftime("%d.%m.%Y"),
            last_day_of_month=last_day_of_month.strftime("%d.%m.%Y"),
        )

        data = await state.get_data()
        first_day = data["first_day_of_month"]
        last_day = data["last_day_of_month"]
        report_name = data["report_name"]

        if report_name == "tickets":
            await state.set_state(Report.report_tickets)
        if report_name == "bookings":
            await state.set_state(Report.report_bookings)
        await callback.message.edit_text(
            f"Вы выбрали период с {first_day} по {last_day}. Хотите создать отчет?",
            reply_markup=await kb.generate_report_button(l10n=l10n),
        )


async def generate_report(
    callback: CallbackQuery,
    state: FSMContext,
    report_type: str,
    model,
    list_name: str,
    get_data_func,
    l10n: FluentLocalization,
):
    data = await state.get_data()
    first_day = data["first_day_of_month"]
    last_day = data["last_day_of_month"]
    report_list = await get_data_func(first_day, last_day)

    if report_list:
        await callback.message.delete()

        # Сохраняем отчет в Excel файл
        file_path = await save_report_to_excel(model, list_name, report_list, first_day)

        # Отправляем файл в чат
        document = FSInputFile(file_path)
        await callback.message.answer_document(document)

        # Удаляем файл после отправки
        if os.path.exists(file_path):
            os.remove(file_path)

        await asyncio.sleep(1)

        text = "🔝                          🔝                          🔝\n✅ Отчет отправлен"
        await callback.message.answer(text, reply_markup=await kb.admin_main(l10n=l10n))
    else:
        await callback.message.edit_text(
            f"За данный период ничего не найдено\nПопробуйте выбрать другой период",
            reply_markup=await kb.admin_main(l10n=l10n),
        )

    await state.clear()


@admin_report_router.callback_query(F.data == "generate_report", Report.report_tickets)
async def tickets_report(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    await generate_report(
        callback, state, "tickets", Ticket, "Заявки", get_tickets_for_period, l10n=l10n
    )


@admin_report_router.callback_query(F.data == "generate_report", Report.report_bookings)
async def bookings_report(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    # await generate_report(callback, state, "reservations", Reservation, "Бронирование", get_reservation_for_period)
    await generate_report(
        callback,
        state,
        "bookings",
        Booking,
        "Бронирование",
        # get_reservation_for_period,
        get_booking_for_period,
        l10n=l10n,
    )


@admin_report_router.callback_query(F.data == "new_visitors", Report.report)
async def select_options_nv(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    await state.update_data(report_name="new_visitors")
    await callback.message.edit_text(
        "Выберите подходящий вариант отчета: ",
        reply_markup=await kb.period_option(l10n=l10n),
    )
    await state.set_state(Report.period_option)
    await callback.answer()


@admin_report_router.callback_query(F.data.startswith("period:"), Report.period_option)
async def select_report(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    period = callback.data.split(":")[1]
    await state.update_data(period=period)
    if period == "day":
        calendar = cl_day.CustomCalendar()
        await callback.message.edit_text(
            "Выберите день отчета: ",
            reply_markup=await calendar.generate_calendar(
                datetime.now().year, datetime.now().month, "new_visitors", locale="ru"
            ),
        )
    if period == "month":
        calendar = cl_month.CustomMonthCalendar()
        await callback.message.edit_text(
            f"Выберите необходимый месяц: ",
            reply_markup=await calendar.generate_month_calendar(
                datetime.now().year, "new_visitors", locale="ru"
            ),
        )
    await state.set_state(Report.period_for_nv)
    await callback.answer()


@admin_report_router.callback_query(
    F.data.startswith("calendar:"), Report.period_for_nv
)
async def set_period(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    data = await state.get_data()
    period = data["period"]

    # Определяем, какой календарь использовать
    calendar = (
        cl_day.CustomCalendar() if period == "day" else cl_month.CustomMonthCalendar()
    )

    # Обрабатываем выбор в зависимости от типа периода
    result = await calendar.handle_callback(callback, "new_visitors", locale="ru")

    if result:
        # Определяем даты в зависимости от периода
        if period == "day":
            first_day = last_day = result  # Одна и та же дата для дня
        elif period == "month":
            first_day, last_day = result  # Начало и конец месяца

        # Обновляем данные в состоянии
        await state.update_data(
            first_day_of_month=first_day.strftime("%d.%m.%Y"),
            last_day_of_month=last_day.strftime("%d.%m.%Y"),
        )

        # Получаем обновленные данные
        first_day = (await state.get_data())["first_day_of_month"]
        last_day = (await state.get_data())["last_day_of_month"]

        # Переходим к следующему состоянию
        await state.set_state(Report.report_new_visitors)

        # Редактируем сообщение
        await callback.message.edit_text(
            f"Вы выбрали период с {first_day} по {last_day}. Хотите создать отчет?",
            reply_markup=await kb.generate_report_button(l10n=l10n),
        )


@admin_report_router.callback_query(
    F.data == "generate_report", Report.report_new_visitors
)
async def reservations_report(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    await generate_report(
        callback,
        state,
        "new_visitors",
        User,
        "Новые пользователи",
        get_new_visitors_for_period,
        l10n=l10n,
    )
