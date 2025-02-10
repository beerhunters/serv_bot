import random

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from fluent.runtime import FluentLocalization

from app.database.requests import create_or_update_admin
from config import GREETINGS_ADMIN, INFO_ADMIN
from filters import IsAdminFilter

import app.admin_kb.keyboards as kb

admin_router = Router()

# Применяем фильтр для всех хэндлеров на уровне роутера
admin_router.message.filter(IsAdminFilter(is_admin=True))
admin_router.callback_query.filter(IsAdminFilter(is_admin=True))


# @admin_router.message(CommandStart())
# @admin_router.message(Command("cancel"))
# @admin_router.callback_query(F.data == "main_menu")
# async def cmd_start(message: Message | CallbackQuery, state: FSMContext):
#     await state.clear()
#     admin = await create_or_update_admin(message.from_user.id)
#     if not (admin and admin.name):
#         if message.from_user.username is None:
#             tg_username = f"<a href='tg://user?id={str(message.from_user.id)}'>{message.from_user.first_name}</a>"
#         else:
#             tg_username = "@" + message.from_user.username
#         await create_or_update_admin(
#             message.from_user.id, tg_username, message.from_user.first_name
#         )
#     greeting_text = (
#         random.choice(GREETINGS_ADMIN).format(message.from_user.first_name.title())
#         + " 👋🏻"
#     )
#     if isinstance(message, Message):
#         await message.answer(greeting_text, reply_markup=await kb.admin_main())
#     elif isinstance(message, CallbackQuery):
#         # Проверяем, содержит ли сообщение медиа (например, фото)
#         if message.message.content_type == "photo":
#             # Удаляем старое сообщение с фото
#             await message.message.delete()
#             # Отправляем новое сообщение с текстом и клавиатурой
#             await message.message.answer(
#                 greeting_text, reply_markup=await kb.admin_main(), parse_mode="HTML"
#             )
#         else:
#             # Если сообщение содержит текст, редактируем его
#             await message.message.edit_text(
#                 greeting_text, reply_markup=await kb.admin_main(), parse_mode="HTML"
#             )
#         # await message.message.edit_text(greeting_text, reply_markup=await kb.admin_main())
#         await message.answer()
@admin_router.message(CommandStart())
@admin_router.message(Command("cancel"))
@admin_router.callback_query(F.data == "main_menu")
async def cmd_start(
    message: Message | CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    await state.clear()
    admin = await create_or_update_admin(message.from_user.id)

    # Проверка, есть ли имя пользователя в базе данных
    if not (admin and admin.name):
        # Проверка, есть ли username у пользователя
        if message.from_user.username is None:
            tg_username = f"<a href='tg://user?id={str(message.from_user.id)}'>{message.from_user.first_name}</a>"
        else:
            tg_username = (
                "@" + message.from_user.username
                if not message.from_user.username.startswith("@")
                else message.from_user.username
            )

        # Обновляем или создаем запись администратора
        await create_or_update_admin(
            message.from_user.id, tg_username, message.from_user.first_name
        )

    greeting_text = (
        random.choice(GREETINGS_ADMIN).format(message.from_user.first_name.title())
        + " 👋🏻"
    )

    # Если сообщение от пользователя
    if isinstance(message, Message):
        await message.answer(greeting_text, reply_markup=await kb.admin_main(l10n=l10n))
    else:
        # Получаем текущее сообщение и клавиатуру
        current_message = message.message.text
        current_keyboard_text = str(message.message.reply_markup)

        # Проверяем, изменилось ли сообщение или клавиатура
        if (current_message != greeting_text) or (
            current_keyboard_text != str(await kb.admin_main(l10n=l10n))
        ):
            await message.message.edit_text(
                greeting_text,
                reply_markup=await kb.admin_main(l10n=l10n),
                parse_mode="HTML",
            )
        else:
            # Если изменений нет, отправляем пустой ответ
            await message.answer()


@admin_router.callback_query(F.data == "info_admin")
async def info(callback: CallbackQuery, l10n: FluentLocalization):
    # await callback.message.edit_text(INFO_ADMIN, reply_markup=await kb.back_button())
    await callback.message.edit_text(
        INFO_ADMIN, reply_markup=await kb.create_buttons(l10n=l10n)
    )
    await callback.answer()
