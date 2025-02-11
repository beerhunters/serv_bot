import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from fluent.runtime import FluentLocalization

import app.admin_kb.keyboards as kb
import app.user_kb.keyboards as user_kb
from app.database.requests import (
    get_open_tickets,
    get_completed_tickets_count_by_admin,
    get_ticket_by_id,
    update_ticket_fields,
    get_all_tickets,
    get_tickets_with_photos,
    get_tickets_by_admin,
)
from filters import IsAdminFilter
from tools.fluent_loader import get_fluent_localization

admin_ticket_router = Router()

# Применяем фильтр для всех хэндлеров на уровне роутера
admin_ticket_router.message.filter(IsAdminFilter(is_admin=True))
admin_ticket_router.callback_query.filter(IsAdminFilter(is_admin=True))


class TicketState(StatesGroup):
    ticket = State()
    comment = State()
    photo = State()
    complete_or_not = State()


@admin_ticket_router.callback_query(F.data == "all_tasks")
async def all_tasks(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    await state.clear()
    open_tickets = await get_open_tickets()
    closed_tickets = await get_completed_tickets_count_by_admin(callback.from_user.id)
    tasks_text = (
        "<b>🤘 Тикет меню 💲</b>\n\n"
        f"<b>🔥 Заявок в работе:</b> {len(open_tickets)}\n"
        f"<b>👍 Завершенных заявок:</b> {closed_tickets}\n\n"
        f"<b>⚠️ Внимание!</b>\n\n"
        f"<i>Закрытые задачи не могут быть возвращены в работу. Пожалуйста, будьте внимательны при их закрытии!</i>"
    )
    # # Проверяем, содержит ли сообщение медиа (например, фото)
    # if callback.message.content_type == 'photo':
    #     # Удаляем старое сообщение с фото
    #     await callback.message.delete()
    #     # Отправляем новое сообщение с текстом и клавиатурой
    #     await callback.message.answer(tasks_text, reply_markup=await kb.tickets_menu(), parse_mode="HTML")
    # else:
    #     # Если сообщение содержит текст, редактируем его
    #     await callback.message.edit_text(tasks_text, reply_markup=await kb.tickets_menu(), parse_mode="HTML")
    # Проверяем, существует ли сообщение, и содержит ли оно текст
    if callback.message and callback.message.text:
        # Если сообщение содержит текст, редактируем его
        await callback.message.edit_text(
            tasks_text, reply_markup=await kb.tickets_menu(l10n=l10n), parse_mode="HTML"
        )
    else:
        # Если сообщение не содержит текст (например, фото или удалено), удаляем и отправляем новое сообщение
        await callback.message.delete()
        await callback.message.answer(
            tasks_text, reply_markup=await kb.tickets_menu(l10n=l10n), parse_mode="HTML"
        )

    await callback.answer()


# @admin_ticket_router.callback_query(F.data == "open_tickets")
# async def list_of_tasks(callback: CallbackQuery, state: FSMContext):
#     open_tickets = await get_open_tickets()
#
#     if callback.message and callback.message.text:
#         # Если сообщение содержит текст, редактируем его
#         if open_tickets:
#             await callback.message.edit_text('🔥Заявок в работе', reply_markup=await kb.list_of_tickets(open_tickets))
#             await state.set_state(TicketState.ticket)
#         else:
#             await callback.message.edit_text('😀 Открытых заявок нет 😀', reply_markup=await kb.admin_main())
#     else:
#         # Если сообщение не содержит текст (например, фото или удалено), удаляем и отправляем новое сообщение
#         if open_tickets:
#             await callback.message.delete()
#             await callback.message.answer('🔥Заявок в работе', reply_markup=await kb.list_of_tickets(open_tickets))
#         else:
#             await callback.message.delete()
#             await callback.message.answer('😀 Открытых заявок нет 😀', reply_markup=await kb.admin_main())
#
#     await callback.answer()
@admin_ticket_router.callback_query(F.data == "open_tickets")
async def list_of_tasks(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    open_tickets = await get_open_tickets()

    message_text = "🔥Заявок в работе" if open_tickets else "😀 Открытых заявок нет 😀"
    reply_markup = (
        await kb.list_of_tickets(open_tickets, l10n=l10n)
        if open_tickets
        else await kb.admin_main(l10n=l10n)
    )

    if callback.message and callback.message.text:
        # Если сообщение содержит текст, редактируем его
        await callback.message.edit_text(message_text, reply_markup=reply_markup)
    else:
        # Если сообщение не содержит текст (например, фото или удалено), удаляем и отправляем новое сообщение
        await callback.message.delete()
        await callback.message.answer(message_text, reply_markup=reply_markup)

    if open_tickets:
        await state.set_state(TicketState.ticket)

    await callback.answer()


@admin_ticket_router.callback_query(F.data.startswith("ticket_"), TicketState.ticket)
async def ticket(callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization):
    ticket_id = callback.data.split("_")[1]
    await state.update_data(ticket_id=ticket_id)
    task = await get_ticket_by_id(ticket_id)
    await state.update_data(reg_time=task.reg_time)
    text = (
        f"<b>Заявка:</b> <code>#{task.id}</code>\n\n"
        # f"<b>Пользователь ID:</b> <a href='tg://user?id={task.user.tg_id}'>{task.user.tg_id}</a>\n"
        f"<b>TG:</b> {task.user.tg_username}\n"
        f"<b>ФИО:</b> {task.user.name}\n"
        f"<b>Расположение:</b> {task.location.name if task.location.name else 'Нет данных'}\n\n"
        f"<b>Сообщение от пользователя:</b> <em>{task.description}</em>\n\n"
        f"<b>Время создания:</b> {task.reg_time}\n"
        f"<b>Статус:</b> {'Выполнена' if task.state else 'Открыта'}\n\n"
        f"<em>⚠️ Для выполнения заявки необходимо нажать соответствующую кнопку! "
        f"После чего оставить комментарий и фото</em>"
    )
    if task.photo_id is None:
        await callback.message.edit_text(
            text, reply_markup=await kb.accept_ticket(l10n=l10n), parse_mode="HTML"
        )
    else:
        await callback.message.delete()
        await callback.message.answer_photo(
            caption=text,
            photo=task.photo_id,
            show_caption_above_media=True,
            reply_markup=await kb.accept_ticket(l10n=l10n),
            parse_mode="HTML",
        )


@admin_ticket_router.callback_query(F.data == "accept_ticket")
async def processing(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):

    text = "Заявка закреплена за Вами!\n\nВыполнить ее сейчас или закончить позже?"

    data = await state.get_data()
    ticket_id = data.get("ticket_id")
    # task = await get_ticket_by_id(ticket_id)
    await update_ticket_fields(ticket_id, admin_id=callback.from_user.id)
    # await state.update_data(reg_time=task.reg_time)

    if callback.message and callback.message.text:
        # Если сообщение содержит текст, редактируем его
        # await callback.message.edit_text(message_text, reply_markup=reply_markup)
        await callback.message.edit_text(
            text, reply_markup=await kb.complete_ticket(l10n=l10n)
        )
    else:
        # Если сообщение не содержит текст (например, фото или удалено), удаляем и отправляем новое сообщение
        await callback.message.delete()
        await callback.message.answer(
            text, reply_markup=await kb.complete_ticket(l10n=l10n)
        )
    # await callback.message.edit_text(
    #     "Заявка закреплена за Вами!\n\nВведите комментарий: "
    # )
    await state.set_state(TicketState.complete_or_not)
    # data = await state.get_data()
    # ticket_id = data.get("ticket_id")
    # await update_ticket_fields(ticket_id, admin_id=callback.from_user.id)


@admin_ticket_router.callback_query(
    F.data == "complete_ticket", TicketState.complete_or_not
)
async def complete_ticket(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    await callback.message.edit_text("Введите сообщение для пользователя: ")
    await state.set_state(TicketState.comment)


@admin_ticket_router.message(TicketState.comment)
async def comment(message: Message, state: FSMContext, l10n: FluentLocalization):
    ticket_comm = message.text
    await state.update_data(ticket_comm=ticket_comm)
    await state.set_state(TicketState.photo)
    await message.answer(
        "Отправьте фото с решением проблемы, либо нажмите /skip_photo."
    )


@admin_ticket_router.message(TicketState.photo)
async def set_photo(message: Message, state: FSMContext, l10n: FluentLocalization):
    if message.text == "/skip_photo":
        await state.update_data(finish_photo_id=None)
        await message.answer(
            "Закрыть задачу?", reply_markup=await kb.close_ticket(l10n=l10n)
        )
    elif message.photo:
        file_id = message.photo[-1].file_id
        await state.update_data(finish_photo_id=file_id)
        await message.answer(
            "Фото сохранено!\n\nЗакрыть задачу?",
            reply_markup=await kb.close_ticket(l10n=l10n),
        )
    else:
        await message.answer(
            "Пожалуйста, отправьте фото или используйте команду /skip_photo."
        )
        return


# @admin_ticket_router.callback_query(F.data == "close_ticket")
# async def complete_ticket(
#     callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
# ):
#     data = await state.get_data()
#     ticket_id = data.get("ticket_id")
#     reg_time = data.get("reg_time")
#     ticket_comm = data.get("ticket_comm")
#     finish_time = datetime.datetime.now().replace(microsecond=0)
#     finish_photo_id = data.get("finish_photo_id")
#     time_spent = int((finish_time - reg_time).total_seconds())
#     await update_ticket_fields(
#         ticket_id,
#         state=1,
#         ticket_comm=ticket_comm,
#         finish_time=finish_time,
#         finish_photo_id=finish_photo_id,
#         time_spent=time_spent,
#     )
#     task = await get_ticket_by_id(ticket_id)
#     await callback.message.edit_text(
#         f"🎉 Заявка #{ticket_id} успешно завершена! 🎉",
#         parse_mode="HTML",
#         reply_markup=await kb.admin_main(l10n=l10n),
#     )
#     # completion_message = (
#     #     f"🎉 Задача <code>#{ticket_id}</code> выполнена!\n"
#     #     # f"<b>Время выполнения:</b> {time_spent}.\n\n"
#     #     f"<b>Ответ исполнителя:</b> - <em>{task.ticket_comm}</em>\n\n"
#     #     f"<em>⚠️ Пожалуйста, проверьте корректность исполнения задачи.</em>"
#     # )
#     completion_message = (
#         f"🎉 {l10n.format_value('t_task')} <code>#{ticket_id}</code> {l10n.format_value('t_complete')}\n"
#         f"<b>{l10n.format_value('t_answer')}</b> - <em>{task.ticket_comm}</em>\n\n"
#         f"<em>{l10n.format_value('t_check')}</em>"
#     )
#     if finish_photo_id:
#         await callback.message.bot.send_photo(
#             chat_id=task.user.tg_id,
#             photo=finish_photo_id,
#             caption=completion_message,
#             show_caption_above_media=True,
#             # reply_markup=await user_kb.back_button(),
#             reply_markup=await user_kb.create_buttons(l10n=l10n),
#         )
#     else:
#         await callback.message.bot.send_message(
#             chat_id=task.user.tg_id,
#             text=completion_message,
#             # reply_markup=await user_kb.back_button(),
#             reply_markup=await user_kb.create_buttons(l10n=l10n),
#             parse_mode="HTML",
#         )
#     await state.clear()


@admin_ticket_router.callback_query(F.data == "close_ticket")
async def complete_ticket(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    data = await state.get_data()
    ticket_id = data.get("ticket_id")
    reg_time = data.get("reg_time")
    ticket_comm = data.get("ticket_comm")
    finish_time = datetime.datetime.now().replace(microsecond=0)
    finish_photo_id = data.get("finish_photo_id")
    time_spent = int((finish_time - reg_time).total_seconds())
    await update_ticket_fields(
        ticket_id,
        state=1,
        ticket_comm=ticket_comm,
        finish_time=finish_time,
        finish_photo_id=finish_photo_id,
        time_spent=time_spent,
    )
    task = await get_ticket_by_id(ticket_id)

    # Получаем язык пользователя (если оно есть в объекте user)
    user_language = (
        task.user.language_code if hasattr(task.user, "language_code") else "ru"
    )

    # Загружаем локализацию
    user_l10n = get_fluent_localization(
        user_language[:2]
    )  # Используем язык пользователя или язык по умолчанию

    await callback.message.edit_text(
        f"🎉 Заявка #{ticket_id} успешно завершена! 🎉",
        parse_mode="HTML",
        reply_markup=await kb.admin_main(l10n=user_l10n),
    )

    completion_message = (
        f"🎉 {user_l10n.format_value('t_task')} <code>#{ticket_id}</code> {user_l10n.format_value('t_complete')}\n"
        f"<b>{user_l10n.format_value('t_answer')}</b> - <em>{task.ticket_comm}</em>\n\n"
        f"<em>{user_l10n.format_value('t_check')}</em>"
    )
    if finish_photo_id:
        await callback.message.bot.send_photo(
            chat_id=task.user.tg_id,
            photo=finish_photo_id,
            caption=completion_message,
            show_caption_above_media=True,
            reply_markup=await user_kb.create_buttons(l10n=user_l10n),
        )
    else:
        await callback.message.bot.send_message(
            chat_id=task.user.tg_id,
            text=completion_message,
            reply_markup=await user_kb.create_buttons(l10n=user_l10n),
            parse_mode="HTML",
        )
    await state.clear()


@admin_ticket_router.callback_query(F.data == "all_my_tickets")
async def all_my_tickets(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    open_tickets = await get_tickets_by_admin(callback.from_user.id)
    if open_tickets:
        await state.set_state(TicketState.ticket)
    message_text = "🔥Заявок в работе" if open_tickets else "😀 Открытых заявок нет 😀"
    reply_markup = (
        await kb.list_of_tickets(open_tickets, l10n=l10n)
        if open_tickets
        else await kb.admin_main(l10n=l10n)
    )
    await callback.message.edit_text(message_text, reply_markup=reply_markup)


@admin_ticket_router.callback_query(F.data == "all_history")
@admin_ticket_router.callback_query(F.data.startswith("history_page_"))
async def history(callback: CallbackQuery, l10n: FluentLocalization):
    tg_id = callback.from_user.id
    page = 1  # Стартовая страница

    if callback.data.startswith("history_page_"):
        page = int(callback.data.split("_")[-1])

    tickets_list = await get_all_tickets(tg_id)

    page_size = 4
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    current_page_tickets = tickets_list[start_index:end_index]

    if current_page_tickets:
        text = f"<b>📨 История всех заявок (страница {page}): </b>\n\n"
        for task in current_page_tickets:
            text += (
                # f"✅\n"
                f"{'✅' if task.state else '⁉️'}\n"
                f"<b>├ Номер заявки:</b> <code>#{task.id}</code>\n"
                f"<b>├ Пользователь:</b> {task.user.tg_username}\n"
                f"<b>├ Описание:</b> {task.description}\n"
                f"<b>├ Дата: </b>{task.reg_time}\n"
                f"<b>├ Фотография: </b>{'Есть' if task.photo_id else '-'}\n"
                f"<b>├ Решение: </b>{task.ticket_comm if task.ticket_comm else '-'}\n"
                f"<b>├ Фото решения: </b>{'Есть' if task.finish_photo_id else '-'}\n"
                f"<b>├ Дата завершения: </b>{task.finish_time if task.finish_time else '-'}\n"
                f"<b>├ Ответственный: </b>{task.admin.tg_username if task.admin_id else '-'}\n"
                f"<b>└ Статус:</b> {'Завершена' if task.state else 'В работе'}\n\n"
            )
        keyboard = await user_kb.tickets(
            "history_page_",
            "all_tasks",
            page,
            len(tickets_list),
            page_size,
            end_index,
            l10n=l10n,
        )
    else:
        text = "📨 История заявок:\n\n" "Заявок пока нет.. 🤷‍️"
        keyboard = await kb.admin_main(l10n=l10n)

    # Сравниваем текст и клавиатуру
    current_message = callback.message.text
    current_keyboard = callback.message.reply_markup

    # Проверяем, изменилось ли сообщение или клавиатура
    if (current_message != text) and (current_keyboard != keyboard):
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")

    await callback.answer()


@admin_ticket_router.callback_query(F.data == "photo_tickets")
@admin_ticket_router.callback_query(F.data.startswith("photo_tickets_page_"))
async def photo_tickets(callback: CallbackQuery, l10n: FluentLocalization):
    page = 1  # Стартовая страница

    if callback.data.startswith("photo_tickets_page_"):
        page = int(callback.data.split("_")[-1])

    tickets_with_photos = await get_tickets_with_photos()

    page_size = 1
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    current_page_tickets = tickets_with_photos[start_index:end_index]

    if current_page_tickets:
        # text = f"<b>📨 История заявок с фото (страница {page}): </b>\n\n"
        keyboard = await user_kb.tickets(
            "photo_tickets_page_",
            "all_tasks",
            page,
            len(tickets_with_photos),
            page_size,
            end_index,
            l10n=l10n,
        )

        for task in current_page_tickets:
            caption = (
                f"Заявка #{task.id} от @{task.user.tg_username}\n"
                f"Дата: {task.reg_time}\n"
                f"Описание: {task.description}\n"
                f"Статус: {'Завершена' if task.state else 'В работе'}"
            )

            # Удаляем предыдущее сообщение
            await callback.message.delete()

            # Отправляем новое сообщение с фото и инлайн-клавиатурой
            await callback.message.answer_photo(
                photo=task.photo_id, caption=caption, reply_markup=keyboard
            )
    else:
        text = "📨 История заявок:\n\n" "Заявок пока нет.. 🤷‍️"
        keyboard = await kb.admin_main(l10n=l10n)

        # Удаляем предыдущее сообщение
        await callback.message.delete()

        # Отправляем новое сообщение без фото, просто с текстом
        await callback.message.answer(text, reply_markup=keyboard, parse_mode="HTML")

    await callback.answer()
