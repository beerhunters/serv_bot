from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from fluent.runtime import FluentLocalization

import app.admin_kb.keyboards as kb
from app.database.requests import (
    get_all_users,
)
from filters import IsAdminFilter

admin_users_router = Router()

# Применяем фильтр для всех хэндлеров на уровне роутера
admin_users_router.message.filter(IsAdminFilter(is_admin=True))
admin_users_router.callback_query.filter(IsAdminFilter(is_admin=True))


@admin_users_router.callback_query(F.data == "list_users")
@admin_users_router.callback_query(F.data.startswith("my_users_page_"))
async def list_users(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    # await add_at_symbol_to_usernames()
    await state.clear()
    page = 1  # Стартовая страница

    if callback.data.startswith("my_users_page_"):
        page = int(callback.data.split("_")[-1])

    users = await get_all_users()
    # Разворачиваем список "на месте"
    users.reverse()

    await state.update_data(users=users)

    await display_users(callback, users, page, "my_users_page_", l10n=l10n)


async def display_users(
    message_or_callback, users, page, prefix, l10n: FluentLocalization
):
    page_size = 5  # Размер страницы
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    current_page_users = users[start_index:end_index]

    if current_page_users:
        text = f"<b>📨 Список пользователей (страница {page}):</b>\n\n"
        for user in current_page_users:
            text += (
                f"👤 ID: {user.id}.\n"
                f" ├ <code>{user.name}</code>\n"
                f" ├ <em>🎟️ TG: </em>{user.tg_username} / <code>{user.tg_id}</code>\n"
                f" ├ <em>☎️ Телефон: </em>{user.contact}\n"
                f" ├ <em>📨 Email: </em>{user.email}\n"
                f" └ <em>🗓️ Посещения: </em>{user.successful_bookings}\n\n"
            )
        keyboard = await kb.users(
            prefix, "main_menu", page, len(users), page_size, end_index, l10n=l10n
        )
    else:
        text = "📨 Пу-пу-пу:\n\n" "Нет ни одного пользователя.. 🤷‍️"
        keyboard = await kb.admin_main(l10n=l10n)

    # Проверяем, сообщение ли это или callback
    if isinstance(message_or_callback, Message):
        await message_or_callback.answer(text, reply_markup=keyboard, parse_mode="HTML")
    else:
        current_message = message_or_callback.message.text
        current_keyboard = message_or_callback.message.reply_markup

        # Проверяем, изменилось ли сообщение или клавиатура
        if (current_message != text) or (current_keyboard != keyboard):
            await message_or_callback.message.edit_text(
                text, reply_markup=keyboard, parse_mode="HTML"
            )

        await message_or_callback.answer()
