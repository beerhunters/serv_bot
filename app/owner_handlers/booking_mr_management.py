from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from fluent.runtime import FluentLocalization

import app.owner_kb.keyboards as kb
import app.admin_kb.keyboards as kb_admin
import app.user_kb.keyboards as user_kb
import config
from app.database.requests import (
    get_all_bookings,
    delete_booking,
    get_admins_from_db,
    get_user_id_by_booking,
)
from app.rubitime import rubitime
from filters import RoleFilter

owner_booking_mr_management = Router()

# Применяем фильтр для всех хэндлеров на уровне роутера
# owner_booking_mr_management.message.filter(IsOwnerFilter(is_owner=True))
# owner_booking_mr_management.callback_query.filter(IsOwnerFilter(is_owner=True))
# ROLES = ["owner", "admin"]
owner_booking_mr_management.callback_query.filter(RoleFilter(roles=["owner", "admin"]))


class RequestManagement(StatesGroup):
    list_requests = State()


# Функция для определения основной клавиатуры в зависимости от роли
async def get_main_keyboard(user_id: int, l10n: FluentLocalization):
    # Проверка владельца
    if user_id in config.BOT_OWNERS:
        return await kb.owner_main(l10n=l10n)
    # Проверка администратора (получаем список админов из БД)
    db_admins = await get_admins_from_db()
    db_admin_ids = {admin[1] for admin in db_admins}  # admin[1] — это tg_id
    bot_admins = set(config.BOT_ADMINS).union(db_admin_ids)
    if user_id in bot_admins:
        return await kb_admin.admin_main(l10n=l10n)
    # Вернуть None или клавиатуру по умолчанию, если пользователь не владелец и не администратор
    return None


@owner_booking_mr_management.callback_query(F.data == "manage_booking")
async def manage_requests(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    # await state.clear()
    # await callback.answer("Функция в разработке", show_alert=True)
    await state.clear()
    await callback.message.edit_text(
        text="💠 Выберите действие:", reply_markup=await kb.manage_booking(l10n=l10n)
    )
    await callback.answer()


@owner_booking_mr_management.callback_query(F.data == "list_booking")
@owner_booking_mr_management.callback_query(F.data.startswith("my_booking_page_"))
async def list_booking(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    await state.clear()
    page = 1  # Стартовая страница

    if callback.data.startswith("my_booking_page_"):
        page = int(callback.data.split("_")[-1])

    booking_list = await get_all_bookings()
    # for booking_mr in booking_mr_list:
    #     print("Данные бронирования:")
    #     # Вывод всех атрибутов объекта MeetingRoom
    #     for attr, value in vars(booking_mr).items():
    #         print(f"  {attr}: {value}")
    await state.update_data(booking_list=booking_list)

    await display_booking(callback, booking_list, page, "my_booking_page_", l10n=l10n)


@owner_booking_mr_management.message(F.text.startswith("/delete_booking_"))
@owner_booking_mr_management.callback_query(F.data.startswith("delete_booking_"))
async def delete_entry(event, state: FSMContext, l10n: FluentLocalization):
    main_keyboard = await get_main_keyboard(event.from_user.id, l10n=l10n)
    if isinstance(event, CallbackQuery):
        booking_id = event.data.split("_")[2]
        booking = await get_user_id_by_booking(
            booking_id,
        )
        await state.update_data(booking_id=booking_id)
        await delete_booking(
            booking_id,
            confirmed=False,
            removed=True,
        )
        await event.message.edit_text(
            "Бронирование успешно удалено.", reply_markup=main_keyboard
        )
        await event.answer()
    elif isinstance(event, Message):
        booking_id = event.text.split("_")[2]
        booking = await get_user_id_by_booking(
            booking_id,
        )
        await state.update_data(booking_id=booking_id)
        await delete_booking(
            booking_id,
            confirmed=False,
            removed=True,
        )
        await event.bot.delete_message(
            chat_id=event.chat.id, message_id=event.message_id - 1
        )
        # Удаляем сообщение перед ответом
        await event.delete()
        await event.answer("Бронирование успешно удалено.", reply_markup=main_keyboard)
    await event.bot.send_message(
        booking.user_tg_id,
        "К сожалению, выбранное время уже занято.☹️",
        reply_markup=await user_kb.user_main(l10n=l10n),
    )
    if booking.confirmed:
        await rubitime("remove_record", {"id": booking.rubitime_id})
    else:
        pass
    await state.clear()


async def display_booking(
    message_or_callback, booking_list, page, prefix, l10n: FluentLocalization
):
    page_size = 5  # Размер страницы
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    current_page_booking = booking_list[start_index:end_index]

    # Формируем текст сообщения
    if current_page_booking:
        text = f"<b>📨 Список бронирований (страница {page}):</b>\n\n"
        for booking in current_page_booking:
            approve_reject = (
                f"<em>✅ Подтвердить: </em>/approve_booking_{booking.id}\n"
                if not booking.confirmed and not booking.removed
                else (
                    f"<em>❌ Отклонить: </em>/reject_booking_{booking.id}\n\n"
                    if booking.confirmed and not booking.removed
                    else ""
                )
            )
            delete_text = (
                f"<em>❌ Удалить: </em>/delete_booking_{booking.id}\n\n"
                if not booking.confirmed and not booking.removed
                else f""
            )
            state_text = (
                f"Подтверждено 🟢\n"
                if booking.confirmed
                else (
                    f"Не подтверждено ⭕️\n"
                    if not booking.confirmed and not booking.removed
                    else "Удаленный ❌\n"
                )
            )
            edit_text = (
                f"<em>🪄️ Редактировать: </em>/edit_booking_mr_{booking.id}\n"
                if not booking.confirmed and not booking.removed
                else ""
            )
            text += (
                f"📟 ID: {booking.id}.\n"
                f" ├ <em>👤 ФИО: </em>{booking.user.name}\n"
                f" ├ <em>🎟️ TG пользователя: </em>{booking.user.tg_username}\n"
                f" ├ <em>📍 Тариф: </em>{booking.tariff.name}\n"
                f" ├ <em>☎️ Дата посещение: </em>{booking.visit_date}\n"
                f" ├ <em>⏱️ Время начала: </em>{booking.start_time}\n"
                f" ├ <em>⏱️ Время окончания: </em>{booking.end_time}\n"
                f" ├ <em>⏱️ Продолжительность: </em>{booking.duration}\n"
                # f" └ <em>💈 Статус: </em>{'Подтверждено' if booking.confirmed else 'Не подтверждено'}\n"
                f" └ <em>💈 Статус: </em>{state_text}\n"
                f"{approve_reject}"
                # f"<em>🪄️ Редактировать: </em>/edit_booking_mr_{booking.id}\n"
                # f"<em>❌ Удалить: </em>/delete_booking_mr_{booking_mr.id}\n\n
                f"{edit_text}"
                f"{delete_text}"
            )
        keyboard = await kb.booking_list(
            prefix,
            "main_menu",
            page,
            len(booking_list),
            page_size,
            end_index,
            l10n=l10n,
        )
    else:
        # Если список бронирований пуст
        text = "📨 Нет доступных бронирований.. 🤷‍️"
        keyboard = await get_main_keyboard(message_or_callback.from_user.id, l10n=l10n)

    # Проверяем, сообщение ли это или callback
    if isinstance(message_or_callback, Message):
        await message_or_callback.answer(text, reply_markup=keyboard, parse_mode="HTML")
    else:
        # Получаем текущее сообщение и клавиатуру
        current_message = message_or_callback.message.text
        current_keyboard_text = str(message_or_callback.message.reply_markup)

        # Проверяем, изменилось ли сообщение или клавиатура
        if (current_message != text) or (current_keyboard_text != str(keyboard)):
            await message_or_callback.message.edit_text(
                text, reply_markup=keyboard, parse_mode="HTML"
            )
        else:
            # Отправляем пустой ответ, если изменения не требуются
            await message_or_callback.answer()
