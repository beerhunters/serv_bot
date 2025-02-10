# from aiogram import Router, F
# from aiogram.fsm.state import StatesGroup, State
# from aiogram.types import CallbackQuery, Message
#
# import app.admin_kb.keyboards as kb
# import app.user_kb.keyboards as user_kb
# from app.database.requests import (
#     get_user_id_by_booking_mr,
#     delete_booking_mr,
#     update_booking_mr_status,
# )
# from app.rubitime import rubitime
#
# from filters import IsAdminFilter
#
# admin_meeting_router = Router()
#
# # Применяем фильтр для всех хэндлеров на уровне роутера
# admin_meeting_router.message.filter(IsAdminFilter(is_admin=True))
# admin_meeting_router.callback_query.filter(IsAdminFilter(is_admin=True))
#
#
# class MeetingState(StatesGroup):
#     complete_or_not = State()
#
#
# # Подтверждение бронирования
# @admin_meeting_router.message(F.text.startswith("/approve_booking_"))
# @admin_meeting_router.callback_query(F.data.startswith("approve_booking_"))
# async def approve_booking(event):
#     if isinstance(event, Message):
#         booking_id = int(event.text.split("_")[2])
#         await update_booking_mr_status(booking_id, confirmed=True)
#         booking_mr = await get_user_id_by_booking_mr(
#             booking_id,
#         )
#         await event.answer(
#             "✅ Бронирование подтверждено.", reply_markup=await kb.admin_main()
#         )
#         user_id = booking_mr.user_id
#         await event.bot.send_message(
#             user_id,
#             "✅ Ваше бронирование подтверждено! 🔆",
#             reply_markup=await user_kb.user_main(),
#         )
#     if isinstance(event, CallbackQuery):
#         booking_id = int(event.data.split("_")[2])
#
#         # Обновляем статус бронирования как подтвержденный
#         await update_booking_mr_status(booking_id, confirmed=True)
#
#         # Получаем id пользователя, чтобы уведомить его
#         # user_id = await get_user_id_by_booking_mr(
#         #     booking_id,
#         # )
#         booking_mr = await get_user_id_by_booking_mr(
#             booking_id,
#         )
#         user_id = booking_mr.user_id
#         await event.bot.send_message(
#             user_id,
#             "✅ Ваше бронирование подтверждено! 🔆",
#             reply_markup=await user_kb.user_main(),
#         )
#         await event.message.edit_text(
#             "✅ Бронирование подтверждено.", reply_markup=await kb.admin_main()
#         )
#         # await event.message.bot.send_message(
#         #     user_id,
#         #     "✅ Ваше бронирование подтверждено! 🔆",
#         #     reply_markup=await user_kb.user_main(),
#         # )
#
#
# # Отклонение бронирования
# @admin_meeting_router.message(F.text.startswith("/reject_booking_"))
# @admin_meeting_router.callback_query(F.data.startswith("reject_booking_"))
# async def reject_booking(event):
#     if isinstance(event, Message):
#         booking_id = int(event.text.split("_")[2])
#         booking_mr = await get_user_id_by_booking_mr(
#             booking_id,
#         )
#         user_id = booking_mr.user_id
#         rubitime_id = booking_mr.rubitime_id
#         # Удаляем запись о бронировании из базы данных
#         await delete_booking_mr(booking_id)
#         method = "remove_record"
#         # 'service_id' = > '', // id услуги
#         #     Большая Переговорная (на 10-12 человек) - 47900
#         #     Опенспейс на день - 49414
#         #     Амфитеатр (на 30-35 человек) - 50764
#         await rubitime(
#             method,
#             {
#                 "id": rubitime_id,
#             },
#         )
#         await event.answer(
#             "⛔️ Бронирование отклонено. ⛔️", reply_markup=await kb.admin_main()
#         )
#         await event.bot.send_message(
#             user_id,
#             "К сожалению, выбранное время уже занято.☹️",
#             reply_markup=await user_kb.user_main(),
#         )
#     if isinstance(event, CallbackQuery):
#         booking_id = int(event.data.split("_")[2])
#
#         # Получаем id пользователя для уведомления об отказе
#         # user_id = await get_user_id_by_booking_mr(
#         #     booking_id,
#         # )
#         booking_mr = await get_user_id_by_booking_mr(
#             booking_id,
#         )
#         user_id = booking_mr.user_id
#         rubitime_id = booking_mr.rubitime_id
#         # Удаляем запись о бронировании из базы данных
#         await delete_booking_mr(booking_id)
#         method = "remove_record"
#         # 'service_id' = > '', // id услуги
#         #     Большая Переговорная (на 10-12 человек) - 47900
#         #     Опенспейс на день - 49414
#         #     Амфитеатр (на 30-35 человек) - 50764
#         await rubitime(
#             method,
#             {
#                 "id": rubitime_id,
#             },
#         )
#
#         await event.bot.send_message(
#             user_id,
#             "К сожалению, выбранное время уже занято.☹️",
#             reply_markup=await user_kb.user_main(),
#         )
#         await event.message.edit_text(
#             "⛔️ Бронирование отклонено. ⛔️", reply_markup=await kb.admin_main()
#         )
from datetime import datetime

from aiogram import Router, F

# from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from fluent.runtime import FluentLocalization

import app.admin_kb.keyboards as kb
import app.user_kb.keyboards as user_kb
from app.database.requests import (
    get_user_id_by_booking,
    delete_booking,
    # update_booking_mr_status,
    update_booking_fields,
)
from app.rubitime import rubitime
from filters import IsAdminFilter

admin_meeting_router = Router()
admin_meeting_router.message.filter(IsAdminFilter(is_admin=True))
admin_meeting_router.callback_query.filter(IsAdminFilter(is_admin=True))


async def handle_booking(event, action, l10n: FluentLocalization):
    # Получаем ID бронирования
    booking_id = int(
        event.text.split("_")[2]
        if isinstance(event, Message)
        else event.data.split("_")[2]
    )
    booking = await get_user_id_by_booking(
        booking_id,
    )
    user_tg_id = booking.user_tg_id

    # Логика для подтверждения или отклонения
    if action == "approve":
        # Объединяем дату и время в одну строку и преобразуем в объект datetime
        combined_datetime = datetime.strptime(
            f"{booking.visit_date.split(' ')[0]} {booking.start_time}", "%Y-%m-%d %H:%M"
        )

        # Форматируем объект datetime в нужный формат
        formatted_datetime = combined_datetime.strftime("%Y-%m-%d %H:%M:%S")
        method = "create_record"
        rubitime_id = await rubitime(
            method,
            {
                "service_id": booking.tariff.service_id,
                "name": booking.user.name,
                "email": booking.user.email,
                "phone": booking.user.contact,
                "record": formatted_datetime,
                "duration": booking.duration * 60,
            },
        )
        await update_booking_fields(booking_id, rubitime_id=rubitime_id, confirmed=True)
        admin_message = "✅ Бронирование подтверждено."
        user_message = "✅ Ваше бронирование подтверждено! 🔆"
    elif action == "reject":
        await delete_booking(
            booking_id,
            confirmed=False,
        )
        try:
            await rubitime("remove_record", {"id": booking.rubitime_id})
        except:
            pass
        admin_message = "⛔️ Бронирование отклонено. ⛔️"
        user_message = "К сожалению, выбранное время уже занято.☹️"

    # Отправляем сообщение админу и пользователю
    # await event.answer(admin_message, reply_markup=await kb.admin_main())
    await event.bot.send_message(
        user_tg_id, user_message, reply_markup=await user_kb.user_main(l10n=l10n)
    )

    # Если событие - CallbackQuery, обновляем текст
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(
            admin_message, reply_markup=await kb.admin_main(l10n=l10n)
        )
    else:
        # await event.bot.delete_message(
        #     chat_id=event.chat.id, message_id=event.message_id - 1
        # )
        await event.answer(admin_message, reply_markup=await kb.admin_main(l10n=l10n))


# Хендлеры для подтверждения и отклонения
@admin_meeting_router.message(F.text.startswith("/approve_booking_"))
@admin_meeting_router.callback_query(F.data.startswith("approve_booking_"))
async def approve_booking(event, l10n: FluentLocalization):
    await handle_booking(event, "approve", l10n=l10n)


@admin_meeting_router.message(F.text.startswith("/reject_booking_"))
@admin_meeting_router.callback_query(F.data.startswith("reject_booking_"))
async def reject_booking(event, l10n: FluentLocalization):
    await handle_booking(event, "reject", l10n=l10n)
