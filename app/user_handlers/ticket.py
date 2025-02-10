from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from fluent.runtime import FluentLocalization

import app.user_kb.keyboards as kb
import app.admin_kb.keyboards as admin_kb
from app.database.requests import create_ticket, get_all_tickets
from config import BOT_ADMINS
from filters import IsUserFilter
from tools.tools import send_localized_message

ticket_router = Router()

# Применяем фильтр для всех хэндлеров на уровне роутера
ticket_router.message.filter(IsUserFilter(is_user=True))
ticket_router.callback_query.filter(IsUserFilter(is_user=True))


class UserTicket(StatesGroup):
    description = State()
    location = State()
    photo = State()


#
# @ticket_router.callback_query(F.data == "helpdesk")
# async def helpdesk(callback: CallbackQuery, state: FSMContext):
#     await callback.message.edit_text(
#         f"Выберите пункт меню: \n", reply_markup=await kb.tickets_menu()
#     )
#     await callback.answer()
#     # await state.set_state(UserTicket.description)
@ticket_router.callback_query(F.data == "helpdesk")
async def helpdesk(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    await send_localized_message(
        callback,
        l10n,
        "helpdesk_menu",  # Ключ для локализованного текста регистрации
        reply_markup=await kb.tickets_menu(l10n=l10n),
        # reply_markup=await kb.tickets_menu(),
    )


# @ticket_router.callback_query(F.data == "new_ticket")
# async def new_ticket(callback: CallbackQuery, state: FSMContext):
#     await callback.message.edit_text(
#         f"Отправьте запрос или опишите проблему\n\n"
#         f"Для отмены используйте команду /cancel."
#     )
#     await state.set_state(UserTicket.description)
@ticket_router.callback_query(F.data == "new_ticket")
async def new_ticket(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    await send_localized_message(
        callback,
        l10n,
        "new_ticket",  # Ключ для локализованного текста регистрации
    )
    await state.set_state(UserTicket.description)


# @ticket_router.message(UserTicket.description)
# async def set_description(message: Message, state: FSMContext):
#     await state.update_data(description=message.text)
#     await state.set_state(UserTicket.location)
#     await message.answer("Выберите местоположение:", reply_markup=await kb.locations())
@ticket_router.message(UserTicket.description)
async def set_description(
    message: Message, state: FSMContext, l10n: FluentLocalization
):
    await state.update_data(description=message.text)
    await state.set_state(UserTicket.location)
    await send_localized_message(
        message,
        l10n,
        "ticket_location",  # Ключ для локализованного текста регистрации
        reply_markup=await kb.locations(l10n=l10n),
        # reply_markup=await kb.locations(),
    )


# @ticket_router.callback_query(F.data.startswith("location_"), UserTicket.location)
# async def set_location(callback: CallbackQuery, state: FSMContext):
#     await callback.answer("Выбор сделан.")
#     await state.update_data(location_id=callback.data.split("_")[1])
#     await state.set_state(UserTicket.photo)
#     await callback.message.edit_text(
#         "Отправьте фото, связанное с проблемой, либо нажмите /skip_photo."
#     )
@ticket_router.callback_query(F.data.startswith("location_"), UserTicket.location)
async def set_location(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    await send_localized_message(
        callback,
        l10n,
        "location_confirmed",  # Ключ для локализованного текста регистрации
        show_alert=True,  # Показывать уведомление пользователю
    )
    await state.update_data(location_id=callback.data.split("_")[1])
    await state.set_state(UserTicket.photo)
    await send_localized_message(
        callback,
        l10n,
        "ticket_photo",  # Ключ для локализованного текста регистрации
    )


# @ticket_router.message(UserTicket.photo)
# async def set_photo(message: Message, state: FSMContext):
#     if message.text == "/skip_photo":
#         await state.update_data(photo_id=None)
#     elif message.photo:
#         file_id = message.photo[-1].file_id
#         await state.update_data(photo_id=file_id)
#     else:
#         await message.answer(
#             "Пожалуйста, отправьте фото или используйте команду /skip_photo."
#         )
#         return
#
#     data = await state.get_data()
#     ticket = await create_ticket(
#         tg_id=message.chat.id,
#         description=data["description"],
#         location_id=data["location_id"],
#         photo_id=data["photo_id"],
#     )
#     await message.answer(
#         "Ваш запрос успешно отправлен.", reply_markup=await kb.user_main()
#     )
#     ticket_text = (
#         f"📬❗️\nПользователь {ticket.user.tg_username} создал новую заявку <code>#{ticket.id}</code>.\n\n"
#         f"<b>Сообщение от пользователя:</b>\n <em>{ticket.description}</em>\n\n"
#         f"<b>ФИО:</b> {ticket.user.name}\n"
#         f"<b>Телефон для связи:</b> {ticket.user.contact}\n"
#         f"<b>Расположение:</b> {ticket.location.name}\n"
#     )
#     await state.clear()
#     for admin in BOT_ADMINS:
#         if data["photo_id"] is not None:
#             await message.bot.send_photo(
#                 admin,
#                 caption=ticket_text,
#                 photo=data["photo_id"],
#                 show_caption_above_media=True,
#                 # reply_markup=await admin_kb.back_button("all_tasks"),
#                 reply_markup=await admin_kb.accept_ticket(),
#             )
#         else:
#             await message.bot.send_message(
#                 admin,
#                 ticket_text,
#                 # reply_markup=await admin_kb.back_button("all_tasks"),
#                 reply_markup=await admin_kb.accept_ticket(),
#                 parse_mode="HTML",
#             )
@ticket_router.message(UserTicket.photo)
async def set_photo(message: Message, state: FSMContext, l10n: FluentLocalization):
    if message.text == "/skip_photo":
        await state.update_data(photo_id=None)
    elif message.photo:
        file_id = message.photo[-1].file_id
        await state.update_data(photo_id=file_id)
    else:
        await send_localized_message(
            message,
            l10n,
            "ticket_photo",  # Ключ для локализованного текста регистрации
        )
        return

    data = await state.get_data()
    reg_time = datetime.now()
    ticket = await create_ticket(
        reg_time=reg_time,
        tg_id=message.chat.id,
        description=data["description"],
        location_id=data["location_id"],
        photo_id=data["photo_id"],
    )
    await send_localized_message(
        message,
        l10n,
        "ticket_send",  # Ключ для локализованного текста регистрации
        reply_markup=await kb.user_main(l10n=l10n),
        # reply_markup=await kb.user_main(),
    )
    # ticket_text = (
    #     f"📬❗️\n{l10n.format_value('user_msg')} {ticket.user.tg_username} {l10n.format_value('create_msg')} <code>#{ticket.id}</code>.\n\n"
    #     f"<b>{l10n.format_value('user_message_msg')}:</b>\n<em>{ticket.description}</em>\n\n"
    #     f"<b>{l10n.format_value('full_name_msg')}:</b> {ticket.user.name}\n"
    #     f"<b>{l10n.format_value('contact_phone_msg')}:</b> {ticket.user.contact}\n"
    #     f"<b>{l10n.format_value('location_msg')}:</b> {ticket.location.name}\n"
    # )
    ticket_text = (
        f"📬❗️\nПользователь {ticket.user.tg_username} создал новую заявку <code>#{ticket.id}</code>.\n\n"
        f"<b>Сообщение от пользователя:</b>\n<em>{ticket.description}</em>\n\n"
        f"<b>ФИО:</b> {ticket.user.name}\n"
        f"<b>Телефон для связи:</b> {ticket.user.contact}\n"
        f"<b>Расположение:</b> {ticket.location.name}\n"
    )
    await state.clear()
    for admin in BOT_ADMINS:
        if data["photo_id"] is not None:
            await message.bot.send_photo(
                admin,
                caption=ticket_text,
                photo=data["photo_id"],
                show_caption_above_media=True,
                reply_markup=await admin_kb.admin_main(l10n=l10n),
                # reply_markup=await admin_kb.accept_ticket(l10n=l10n),
                # reply_markup=await admin_kb.accept_ticket(),
            )
        else:
            await message.bot.send_message(
                admin,
                ticket_text,
                reply_markup=await admin_kb.admin_main(l10n=l10n),
                # reply_markup=await admin_kb.accept_ticket(l10n=l10n),
                # reply_markup=await admin_kb.accept_ticket(),
                parse_mode="HTML",
            )


# @ticket_router.callback_query(F.data == "all_tickets")
# @ticket_router.callback_query(F.data.startswith("my_ticket_page_"))
# async def all_tickets(callback: CallbackQuery):
#     tg_id = callback.from_user.id
#     page = 1  # Стартовая страница
#
#     if callback.data.startswith("my_ticket_page_"):
#         page = int(callback.data.split("_")[-1])
#
#     tickets_list = await get_all_tickets(tg_id)
#
#     page_size = 4
#     start_index = (page - 1) * page_size
#     end_index = start_index + page_size
#     current_page_tickets = tickets_list[start_index:end_index]
#
#     if current_page_tickets:
#         text = f"<b>📨 История ваших заявок (страница {page}):</b>\n\n"
#         for ticket in current_page_tickets:
#             text += (
#                 # f"✅\n"
#                 f"{'✅' if ticket.state else '⁉️'}\n"
#                 f"<b>├ Заявка:</b> <code>#{ticket.id}</code>\n"
#                 f"<b>├ Описание:</b> {ticket.description}\n"
#                 f"<b>├ Дата: </b>{ticket.reg_time}\n"
#                 f"<b>├ Комментарий: </b>{ticket.ticket_comm if ticket.ticket_comm else '-'}\n"
#                 f"<b>└ Статус:</b> {'Завершена' if ticket.state else 'В работе'}\n\n"
#             )
#         keyboard = await kb.tickets(
#             "my_ticket_page_",
#             "helpdesk",
#             page,
#             len(tickets_list),
#             page_size,
#             end_index,
#         )
#     else:
#         text = "📨 История ваших заявок:\n\n" "Заявок пока нет.. 🤷‍️"
#         keyboard = await kb.user_main()
#
#     # Сравниваем текст и клавиатуру
#     current_message = callback.message.text
#     current_keyboard = callback.message.reply_markup
#
#     # Проверяем, изменилось ли сообщение или клавиатура
#     if (current_message != text) and (current_keyboard != keyboard):
#         await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
#
#     await callback.answer()
@ticket_router.callback_query(F.data == "all_tickets")
@ticket_router.callback_query(F.data.startswith("my_ticket_page_"))
async def all_tickets(callback: CallbackQuery, l10n: FluentLocalization):
    tg_id = callback.from_user.id
    page = 1  # Стартовая страница

    if callback.data.startswith("my_ticket_page_"):
        page = int(callback.data.split("_")[-1])

    tickets_list = await get_all_tickets(tg_id)

    page_size = 4
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    current_page_tickets = tickets_list[start_index:end_index]

    if current_page_tickets:
        text = f"<b>{l10n.format_value('ticket_history')} {page}):</b>\n\n"
        for ticket in current_page_tickets:
            text += (
                f"{'✅' if ticket.state else '⁉️'}\n"
                f"<b>├ {l10n.format_value("h_ticket")}</b> <code>#{ticket.id}</code>\n"
                f"<b>├ {l10n.format_value("h_description")}</b> {ticket.description}\n"
                f"<b>├ {l10n.format_value("h_date")} </b>{ticket.reg_time}\n"
                f"<b>├ {l10n.format_value("h_comment")} </b>{ticket.ticket_comm if ticket.ticket_comm else '-'}\n"
                f"<b>└ {l10n.format_value("h_status")}</b> {l10n.format_value("h_completed") if ticket.state else l10n.format_value("h_execute")}\n\n"
            )
        keyboard = await kb.tickets(
            "my_ticket_page_",
            "helpdesk",
            page,
            len(tickets_list),
            page_size,
            end_index,
            l10n=l10n,
        )
    else:
        text = l10n.format_value("empty_history")
        keyboard = await kb.user_main(l10n=l10n)
        # keyboard = await kb.user_main()

    # Сравниваем текст и клавиатуру
    current_message = callback.message.text
    current_keyboard = callback.message.reply_markup

    # Проверяем, изменилось ли сообщение или клавиатура
    if (current_message != text) and (current_keyboard != keyboard):
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")

    await callback.answer()
