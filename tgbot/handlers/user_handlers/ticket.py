# from datetime import datetime
#
# from aiogram import Router, F
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import StatesGroup, State
# from aiogram.types import CallbackQuery, Message
# from fluent.runtime import FluentLocalization
#
# import tgbot.keyboards.user_kb.keyboards as kb
# import tgbot.keyboards.admin_kb.keyboards as admin_kb
# from tgbot.database.requests import create_ticket, get_all_tickets
# from tgbot.config import BOT_ADMINS
# from tgbot.filters import IsUserFilter
# from tgbot.tools.tools import send_localized_message
#
# ticket_router = Router()
#
# # Применяем фильтр для всех хэндлеров на уровне роутера
# ticket_router.message.filter(IsUserFilter(is_user=True))
# ticket_router.callback_query.filter(IsUserFilter(is_user=True))
#
#
# class UserTicket(StatesGroup):
#     description = State()
#     location = State()
#     photo = State()
#
#
# @ticket_router.callback_query(F.data == "helpdesk")
# async def helpdesk(
#     callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
# ):
#     await send_localized_message(
#         callback,
#         l10n,
#         "helpdesk_menu",
#         reply_markup=await kb.tickets_menu(l10n=l10n),
#     )
#
#
# @ticket_router.callback_query(F.data == "new_ticket")
# async def new_ticket(
#     callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
# ):
#     await send_localized_message(
#         callback,
#         l10n,
#         "new_ticket",
#     )
#     await state.set_state(UserTicket.description)
#
#
# @ticket_router.message(UserTicket.description)
# async def set_description(
#     message: Message, state: FSMContext, l10n: FluentLocalization
# ):
#     await state.update_data(description=message.text)
#     await state.set_state(UserTicket.location)
#     await send_localized_message(
#         message,
#         l10n,
#         "ticket_location",
#         reply_markup=await kb.locations(l10n=l10n),
#     )
#
#
# @ticket_router.callback_query(F.data.startswith("location_"), UserTicket.location)
# async def set_location(
#     callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
# ):
#     await send_localized_message(
#         callback,
#         l10n,
#         "location_confirmed",
#         show_alert=True,
#     )
#     await state.update_data(location_id=callback.data.split("_")[1])
#     await state.set_state(UserTicket.photo)
#     await send_localized_message(
#         callback,
#         l10n,
#         "ticket_photo",
#     )
#
#
# @ticket_router.message(UserTicket.photo)
# async def set_photo(message: Message, state: FSMContext, l10n: FluentLocalization):
#     if message.text == "/skip_photo":
#         await state.update_data(photo_id=None)
#     elif message.photo:
#         file_id = message.photo[-1].file_id
#         await state.update_data(photo_id=file_id)
#     else:
#         await send_localized_message(
#             message,
#             l10n,
#             "ticket_photo",
#         )
#         return
#
#     data = await state.get_data()
#     reg_time = datetime.now()
#     ticket = await create_ticket(
#         reg_time=reg_time,
#         tg_id=message.chat.id,
#         description=data["description"],
#         location_id=data["location_id"],
#         photo_id=data["photo_id"],
#     )
#     await send_localized_message(
#         message,
#         l10n,
#         "ticket_send",
#         reply_markup=await kb.user_main(l10n=l10n),
#     )
#     # ticket_text = (
#     #     f"📬❗️\n{l10n.format_value('user_msg')} {ticket.user.tg_username} {l10n.format_value('create_msg')} <code>#{ticket.id}</code>.\n\n"
#     #     f"<b>{l10n.format_value('user_message_msg')}:</b>\n<em>{ticket.description}</em>\n\n"
#     #     f"<b>{l10n.format_value('full_name_msg')}:</b> {ticket.user.name}\n"
#     #     f"<b>{l10n.format_value('contact_phone_msg')}:</b> {ticket.user.contact}\n"
#     #     f"<b>{l10n.format_value('location_msg')}:</b> {ticket.location.name}\n"
#     # )
#     ticket_text = (
#         f"📬❗️\nПользователь {ticket.user.tg_username} создал новую заявку <code>#{ticket.id}</code>.\n\n"
#         f"<b>Сообщение от пользователя:</b>\n<em>{ticket.description}</em>\n\n"
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
#                 reply_markup=await admin_kb.admin_main(l10n=l10n),
#             )
#         else:
#             await message.bot.send_message(
#                 admin,
#                 ticket_text,
#                 reply_markup=await admin_kb.admin_main(l10n=l10n),
#                 parse_mode="HTML",
#             )
#
#
# # @ticket_router.callback_query(F.data == "all_tickets")
# # @ticket_router.callback_query(F.data.startswith("my_ticket_page_"))
# # async def all_tickets(callback: CallbackQuery):
# #     tg_id = callback.from_user.id
# #     page = 1  # Стартовая страница
# #
# #     if callback.data.startswith("my_ticket_page_"):
# #         page = int(callback.data.split("_")[-1])
# #
# #     tickets_list = await get_all_tickets(tg_id)
# #
# #     page_size = 4
# #     start_index = (page - 1) * page_size
# #     end_index = start_index + page_size
# #     current_page_tickets = tickets_list[start_index:end_index]
# #
# #     if current_page_tickets:
# #         text = f"<b>📨 История ваших заявок (страница {page}):</b>\n\n"
# #         for ticket in current_page_tickets:
# #             text += (
# #                 # f"✅\n"
# #                 f"{'✅' if ticket.state else '⁉️'}\n"
# #                 f"<b>├ Заявка:</b> <code>#{ticket.id}</code>\n"
# #                 f"<b>├ Описание:</b> {ticket.description}\n"
# #                 f"<b>├ Дата: </b>{ticket.reg_time}\n"
# #                 f"<b>├ Комментарий: </b>{ticket.ticket_comm if ticket.ticket_comm else '-'}\n"
# #                 f"<b>└ Статус:</b> {'Завершена' if ticket.state else 'В работе'}\n\n"
# #             )
# #         keyboard = await kb.tickets(
# #             "my_ticket_page_",
# #             "helpdesk",
# #             page,
# #             len(tickets_list),
# #             page_size,
# #             end_index,
# #         )
# #     else:
# #         text = "📨 История ваших заявок:\n\n" "Заявок пока нет.. 🤷‍️"
# #         keyboard = await kb.user_main()
# #
# #     # Сравниваем текст и клавиатуру
# #     current_message = callback.message.text
# #     current_keyboard = callback.message.reply_markup
# #
# #     # Проверяем, изменилось ли сообщение или клавиатура
# #     if (current_message != text) and (current_keyboard != keyboard):
# #         await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
# #
# #     await callback.answer()
# @ticket_router.callback_query(F.data == "all_tickets")
# @ticket_router.callback_query(F.data.startswith("my_ticket_page_"))
# async def all_tickets(callback: CallbackQuery, l10n: FluentLocalization):
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
#         text = f"<b>{l10n.format_value('ticket_history')} {page}):</b>\n\n"
#         for ticket in current_page_tickets:
#             text += (
#                 f"{'✅' if ticket.state else '⁉️'}\n"
#                 f"<b>├ {l10n.format_value('h_ticket')}</b> <code>#{ticket.id}</code>\n"
#                 f"<b>├ {l10n.format_value('h_description')}</b> {ticket.description}\n"
#                 f"<b>├ {l10n.format_value('h_date')} </b>{ticket.reg_time}\n"
#                 f"<b>├ {l10n.format_value('h_comment')} </b>{ticket.ticket_comm if ticket.ticket_comm else '-'}\n"
#                 f"<b>└ {l10n.format_value('h_status')}</b> {l10n.format_value('h_completed') if ticket.state else l10n.format_value('h_execute')}\n\n"
#             )
#         keyboard = await kb.tickets(
#             "my_ticket_page_",
#             "helpdesk",
#             page,
#             len(tickets_list),
#             page_size,
#             end_index,
#             l10n=l10n,
#         )
#     else:
#         text = l10n.format_value("empty_history")
#         keyboard = await kb.user_main(l10n=l10n)
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
import logging

from aiogram.exceptions import TelegramBadRequest

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from fluent.runtime import FluentLocalization

import tgbot.keyboards.user_kb.keyboards as kb
import tgbot.keyboards.admin_kb.keyboards as admin_kb
from tgbot.database.requests import create_ticket, get_all_tickets
from tgbot.config import BOT_ADMINS
from tgbot.filters import IsUserFilter
from tgbot.tools.time_utils import get_moscow_time
from tgbot.tools.tools import send_localized_message

logger = logging.getLogger(__name__)

ticket_router = Router()

# Применяем фильтр для всех хэндлеров на уровне роутера
ticket_router.message.filter(IsUserFilter(is_user=True))
ticket_router.callback_query.filter(IsUserFilter(is_user=True))


class UserTicket(StatesGroup):
    """Состояния для создания тикета пользователем."""

    description = State()
    location = State()
    photo = State()


@ticket_router.callback_query(F.data == "helpdesk")
async def helpdesk(callback: CallbackQuery, l10n: FluentLocalization) -> None:
    """Отображение меню тикетов."""
    await callback.answer()
    try:
        await send_localized_message(
            callback,
            l10n,
            "helpdesk_menu",
            reply_markup=await kb.tickets_menu(l10n=l10n),
        )
    except TelegramBadRequest as e:
        logger.error("Не удалось отправить меню тикетов: %s", str(e))


@ticket_router.callback_query(F.data == "new_ticket")
async def new_ticket(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
) -> None:
    """Начало создания нового тикета."""
    await callback.answer()
    try:
        await send_localized_message(callback, l10n, "new_ticket")
    except TelegramBadRequest as e:
        logger.error("Не удалось отправить сообщение о новом тикете: %s", str(e))
        return
    await state.set_state(UserTicket.description)


@ticket_router.message(UserTicket.description)
async def set_description(
    message: Message, state: FSMContext, l10n: FluentLocalization
) -> None:
    """Сохранение описания тикета."""
    description = message.text.strip()
    if len(description) < 5:  # Минимальная длина описания
        await send_localized_message(
            message, l10n, "description_too_short", show_alert=True
        )
        return
    await state.update_data(description=description)
    await state.set_state(UserTicket.location)
    try:
        await send_localized_message(
            message,
            l10n,
            "ticket_location",
            reply_markup=await kb.locations(l10n=l10n),
        )
    except TelegramBadRequest as e:
        logger.error("Не удалось отправить запрос локации: %s", str(e))


@ticket_router.callback_query(F.data.startswith("location_"), UserTicket.location)
async def set_location(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
) -> None:
    """Выбор локации для тикета."""
    await callback.answer()
    try:
        location_id = int(callback.data.split("_")[1])
    except (IndexError, ValueError):
        logger.error("Некорректный location_id: %s", callback.data)
        await send_localized_message(
            callback, l10n, "invalid_location", show_alert=True
        )
        return
    try:
        await send_localized_message(
            callback, l10n, "location_confirmed", show_alert=True
        )
        await state.update_data(location_id=location_id)
        await state.set_state(UserTicket.photo)
        await send_localized_message(callback, l10n, "ticket_photo")
    except TelegramBadRequest as e:
        logger.error("Не удалось подтвердить локацию или запросить фото: %s", str(e))


@ticket_router.message(UserTicket.photo)
async def set_photo(
    message: Message, state: FSMContext, l10n: FluentLocalization
) -> None:
    """Добавление фото к тикету и завершение создания."""
    if message.text == "/skip_photo":
        await state.update_data(photo_id=None)
    elif message.photo:
        file_id = message.photo[-1].file_id
        await state.update_data(photo_id=file_id)
    else:
        await send_localized_message(message, l10n, "ticket_photo")
        return

    data = await state.get_data()
    if not all(key in data for key in ["description", "location_id"]):
        logger.error("Недостаточно данных для создания тикета: %s", data)
        await send_localized_message(message, l10n, "ticket_error", show_alert=True)
        return

    # reg_time = datetime.now()
    reg_time = get_moscow_time()
    try:
        ticket = await create_ticket(
            reg_time=reg_time,
            tg_id=message.chat.id,
            description=data["description"],
            location_id=data["location_id"],
            photo_id=data.get("photo_id"),
        )
    except Exception as e:
        logger.error("Ошибка создания тикета: %s", str(e))
        await send_localized_message(message, l10n, "ticket_error", show_alert=True)
        return

    try:
        await send_localized_message(
            message,
            l10n,
            "ticket_send",
            reply_markup=await kb.user_main(l10n=l10n),
        )
    except TelegramBadRequest as e:
        logger.error("Не удалось отправить подтверждение тикета: %s", str(e))

    # ticket_text = (
    #     f"📬❗️\n{l10n.format_value('ticket_created', {'username': ticket.user.tg_username, 'id': ticket.id})}\n\n"
    #     f"<b>{l10n.format_value('description')}:</b>\n<em>{ticket.description}</em>\n\n"
    #     f"<b>{l10n.format_value('full_name')}:</b> {ticket.user.name}\n"
    #     f"<b>{l10n.format_value('contact_phone')}:</b> {ticket.user.contact}\n"
    #     f"<b>{l10n.format_value('location')}:</b> {ticket.location.name}\n"
    # )
    ticket_text = (
        f"📬❗️\nПользователь @{ticket.user.tg_username} создал новую заявку <code>#{ticket.id}</code>.\n\n"
        f"<b>Сообщение от пользователя:</b>\n<em>{ticket.description}</em>\n\n"
        f"<b>ФИО:</b> {ticket.user.name}\n"
        f"<b>Телефон для связи:</b> {ticket.user.contact}\n"
        f"<b>Расположение:</b> {ticket.location.name}\n"
    )
    await state.clear()

    for admin in BOT_ADMINS:
        try:
            if data.get("photo_id"):
                await message.bot.send_photo(
                    admin,
                    caption=ticket_text,
                    photo=data["photo_id"],
                    show_caption_above_media=True,
                    reply_markup=await admin_kb.admin_main(l10n=l10n),
                )
            else:
                await message.bot.send_message(
                    admin,
                    ticket_text,
                    reply_markup=await admin_kb.admin_main(l10n=l10n),
                    parse_mode="HTML",
                )
            logger.debug(
                "Уведомление о тикете #%s отправлено администратору %s",
                ticket.id,
                admin,
            )
        except TelegramBadRequest as e:
            logger.error(
                "Не удалось отправить уведомление администратору %s: %s", admin, str(e)
            )


@ticket_router.callback_query(F.data == "all_tickets")
@ticket_router.callback_query(F.data.startswith("my_ticket_page_"))
async def all_tickets(callback: CallbackQuery, l10n: FluentLocalization) -> None:
    """Отображение истории тикетов пользователя."""
    await callback.answer()
    tg_id = callback.from_user.id
    page = 1
    if callback.data.startswith("my_ticket_page_"):
        try:
            page = int(callback.data.split("_")[-1])
        except ValueError:
            logger.error("Некорректный номер страницы: %s", callback.data)
            page = 1

    try:
        tickets_list = await get_all_tickets(tg_id)
    except Exception as e:
        logger.error("Ошибка получения списка тикетов: %s", str(e))
        await send_localized_message(
            callback, l10n, "ticket_list_error", show_alert=True
        )
        return

    page_size = 4
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    current_page_tickets = tickets_list[start_index:end_index]

    # if current_page_tickets:
    #     text = f"<b>{l10n.format_value('ticket_history', {'page': page})}:</b>\n\n"
    #     for ticket in current_page_tickets:
    #         text += (
    #             f"{'✅' if ticket.state else '⁉️'}\n"
    #             f"<b>├ {l10n.format_value('h_ticket')}</b> <code>#{ticket.id}</code>\n"
    #             f"<b>├ {l10n.format_value('h_description')}</b> {ticket.description}\n"
    #             f"<b>├ {l10n.format_value('h_date')} </b>{ticket.reg_time}\n"
    #             f"<b>├ {l10n.format_value('h_comment')} </b>{ticket.ticket_comm if ticket.ticket_comm else '-'}\n"
    #             f"<b>└ {l10n.format_value('h_status')}</b> {l10n.format_value('h_completed') if ticket.state else l10n.format_value('h_execute')}\n\n"
    #         )
    if current_page_tickets:
        text = f"<b>📨 История ваших заявок (страница {page}):</b>\n\n"
        for ticket in current_page_tickets:
            text += (
                # f"✅\n"
                f"{'✅' if ticket.state else '⁉️'}\n"
                f"<b>├ Заявка:</b> <code>#{ticket.id}</code>\n"
                f"<b>├ Описание:</b> {ticket.description}\n"
                f"<b>├ Дата: </b>{ticket.reg_time}\n"
                f"<b>├ Комментарий: </b>{ticket.ticket_comm if ticket.ticket_comm else '-'}\n"
                f"<b>└ Статус:</b> {'Завершена' if ticket.state else 'В работе'}\n\n"
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

    current_message = callback.message.text
    current_keyboard = str(callback.message.reply_markup)
    if (current_message != text) or (current_keyboard != str(keyboard)):
        try:
            await callback.message.edit_text(
                text, reply_markup=keyboard, parse_mode="HTML"
            )
        except TelegramBadRequest as e:
            logger.error("Не удалось обновить список тикетов: %s", str(e))
            await callback.message.answer(
                text, reply_markup=keyboard, parse_mode="HTML"
            )
    await callback.answer()
