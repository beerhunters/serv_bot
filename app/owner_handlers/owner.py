import random

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from config import GREETINGS_OWNER, INFO_OWNER
from filters import IsOwnerFilter

import app.owner_kb.keyboards as kb
import app.general_keyboards as gkb

owner_router = Router()

# Применяем фильтр для всех хэндлеров на уровне роутера
owner_router.message.filter(IsOwnerFilter(is_owner=True))
owner_router.callback_query.filter(IsOwnerFilter(is_owner=True))


# @owner_router.message(CommandStart())
# @owner_router.message(Command("cancel"))
# @owner_router.callback_query(F.data == "main_menu")
# async def cmd_start(message: Message | CallbackQuery, state: FSMContext):
#     await state.clear()
#     greeting_text = (
#         random.choice(GREETINGS_OWNER).format(message.from_user.first_name.title())
#         + " 👋🏻"
#     )
#     if isinstance(message, Message):
#         await message.answer(greeting_text, reply_markup=await kb.owner_main())
#     elif isinstance(message, CallbackQuery):
#         # Проверяем, содержит ли сообщение медиа (например, фото)
#         if message.message.content_type == "photo":
#             # Удаляем старое сообщение с фото
#             await message.message.delete()
#             # Отправляем новое сообщение с текстом и клавиатурой
#             await message.message.answer(
#                 greeting_text, reply_markup=await kb.owner_main(), parse_mode="HTML"
#             )
#         else:
#             # Если сообщение содержит текст, редактируем его
#             await message.message.edit_text(
#                 greeting_text, reply_markup=await kb.owner_main(), parse_mode="HTML"
#             )
#         await message.answer()
@owner_router.message(CommandStart())
@owner_router.message(Command("cancel"))
@owner_router.callback_query(F.data == "main_menu")
async def cmd_start(message: Message | CallbackQuery, state: FSMContext):
    await state.clear()
    greeting_text = (
        random.choice(GREETINGS_OWNER).format(message.from_user.first_name.title())
        + " 👋🏻"
    )

    # Если сообщение от пользователя
    if isinstance(message, Message):
        await message.answer(greeting_text, reply_markup=await kb.owner_main())
    elif isinstance(message, CallbackQuery):
        # Получаем текущее сообщение и клавиатуру
        current_message = message.message.text
        current_keyboard_text = str(message.message.reply_markup)

        # Проверяем, изменился ли текст сообщения или клавиатура
        if (current_message != greeting_text) or (
            current_keyboard_text != str(await kb.owner_main())
        ):
            # Если изменилось, редактируем сообщение
            if message.message.content_type == "photo":
                # Удаляем старое сообщение с фото
                await message.message.delete()
                # Отправляем новое сообщение с текстом и клавиатурой
                await message.message.answer(
                    greeting_text, reply_markup=await kb.owner_main(), parse_mode="HTML"
                )
            else:
                # Если сообщение содержит текст, редактируем его
                await message.message.edit_text(
                    greeting_text, reply_markup=await kb.owner_main(), parse_mode="HTML"
                )
        else:
            # Если изменений нет, отправляем пустой ответ
            await message.answer()


@owner_router.callback_query(F.data == "info_owner")
async def info(callback: CallbackQuery):
    await callback.message.edit_text(
        INFO_OWNER, reply_markup=await gkb.create_buttons()
    )
    await callback.answer()
