import asyncio
import os
import re

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, FSInputFile, Message
from fluent.runtime import FluentLocalization

import tgbot.keyboards.owner_kb.keyboards as kb
import tgbot.keyboards.general_keyboards as gkb
from tgbot.handlers.admin_handlers.save_xlsx import (
    save_report_to_excel,
    save_report_to_csv,
)
from tgbot.database.models import User
from tgbot.database.requests import (
    get_all_users,
    search_users_by_name,
    search_users_by_phone,
    get_user_by_id,
    update_user_fields,
    delete_user_from_db,
)
from tgbot.filters import IsOwnerFilter

owner_users_management = Router()

# Применяем фильтр для всех хэндлеров на уровне роутера
owner_users_management.message.filter(IsOwnerFilter(is_owner=True))
owner_users_management.callback_query.filter(IsOwnerFilter(is_owner=True))


class UsersManagement(StatesGroup):
    search_user = State()
    search_name = State()
    search_phone = State()
    search_id = State()
    edit_user = State()
    edit_user_name = State()
    edit_user_phone = State()
    edit_user_email = State()
    edit_user_visits = State()


@owner_users_management.callback_query(F.data == "manage_users")
async def manage_users(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    await state.clear()
    await callback.message.edit_text(
        text="💠 Выберите действие:", reply_markup=await kb.manage_users(l10n=l10n)
    )
    await callback.answer()


@owner_users_management.callback_query(F.data == "list_users")
@owner_users_management.callback_query(F.data.startswith("my_users_page_"))
async def list_users(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    # await add_at_symbol_to_usernames()
    await state.clear()
    page = 1  # Стартовая страница

    if callback.data.startswith("my_users_page_"):
        page = int(callback.data.split("_")[-1])

    users = await get_all_users()
    users.reverse()
    await state.update_data(users=users)

    await display_users(callback, users, page, "my_users_page_", l10n=l10n)


# @owner_users_management.callback_query(F.data == "list_users")
# @owner_users_management.callback_query(F.data.startswith('my_users_page_'))
# async def list_users(callback: CallbackQuery, state: FSMContext):
#     await state.clear()
#     page = 1  # Стартовая страница
#
#     if callback.data.startswith('my_users_page_'):
#         page = int(callback.data.split("_")[-1])
#
#     users = await get_all_users()
#     await state.update_data(users=users)
#
#     page_size = 5
#     start_index = (page - 1) * page_size
#     end_index = start_index + page_size
#     current_page_users = users[start_index:end_index]
#
#     if current_page_users:
#         text = f"<b>📨 Список всех пользователей (страница {page}):</b>\n\n"
#         for user in current_page_users:
#             text += (
#                 f"👤 ID: {user.id}.\n"
#                 f" ├ <code>{user.name}</code>\n"
#                 f" ├ <em>🎟️ TG: </em>@{user.tg_username} / <code>{user.tg_id}</code>\n"
#                 f" ├ <em>☎️ Телефон: </em>{user.contact}\n"
#                 f" ├ <em>📨 Email: </em>{user.email}\n"
#                 f" └ <em>🗓️ Посещения: </em>{user.successful_bookings}\n\n"
#             )
#         keyboard = await kb.users(
#             "my_users_page_", "manage_users", page, len(users), page_size, end_index)
#     else:
#         text = (
#             '📨 Пу-пу-пу:\n\n'
#             'Нет ни одного пользователя.. 🤷‍️'
#         )
#         keyboard = await kb.owner_main()
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


@owner_users_management.callback_query(F.data == "download_users")
async def download_users(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    users = await get_all_users()

    if users:
        await callback.message.delete()
        # file_path = await save_report_to_excel(User, "Пользователи", users)
        file_path = await save_report_to_csv(
            User, "Пользователи", users
        )  # Заменили на save_report_to_csv
        document = FSInputFile(file_path)
        await callback.message.answer_document(document)
        if os.path.exists(file_path):
            os.remove(file_path)

        await asyncio.sleep(1)

        text = "🔝                          🔝                          🔝\n✅ Файл отправлен"
        await callback.message.answer(text, reply_markup=await kb.owner_main(l10n=l10n))
    else:
        await callback.message.edit_text(
            f"Ничего не найдено\nПопробуйте еще раз",
            reply_markup=await kb.owner_main(l10n=l10n),
        )
    await state.clear()


@owner_users_management.callback_query(F.data == "find_user")
async def tool_selection(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    await callback.message.edit_text(
        "Как будем искать пользователя?", reply_markup=await kb.search_tools(l10n=l10n)
    )
    await state.set_state(UsersManagement.search_user)
    await callback.answer()


@owner_users_management.callback_query(F.data.startswith("find_"))
@owner_users_management.callback_query(
    F.data.startswith("find_"), UsersManagement.search_user
)
async def find_user(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    tool = callback.data.split("_")[1]
    reply_keyboard = await gkb.create_buttons(l10n=l10n)
    if tool == "name":
        await callback.message.edit_text(
            "Введите фамилию для поиска.", reply_markup=reply_keyboard
        )
        await state.set_state(UsersManagement.search_name)
        await callback.answer()
    elif tool == "phone":
        await callback.message.edit_text(
            "Введите номер телефона пользователя для поиска",
            reply_markup=reply_keyboard,
        )
        await state.set_state(UsersManagement.search_phone)
        await callback.answer()
    elif tool == "id":
        await callback.message.edit_text(
            "Введите ID пользователя для поиска", reply_markup=reply_keyboard
        )
        await state.set_state(UsersManagement.search_id)
        await callback.answer()


@owner_users_management.message(UsersManagement.search_name)
@owner_users_management.callback_query(F.data.startswith("search_users_page_"))
async def search_name(message_or_callback, state: FSMContext, l10n: FluentLocalization):
    page = 1  # Стартовая страница

    if isinstance(
        message_or_callback, CallbackQuery
    ) and message_or_callback.data.startswith("search_users_page_"):
        page = int(message_or_callback.data.split("_")[-1])
        data = await state.get_data()
        users = data.get("search_users", [])
    else:
        search_query = message_or_callback.text.strip()
        if not search_query:
            await message_or_callback.answer("Введите фамилию для поиска.")
            return
        users = await search_users_by_name(search_query)
        await state.update_data(search_users=users)

    if users:
        await display_users(
            message_or_callback, users, page, "search_users_page_", l10n=l10n
        )
        await state.clear()
    else:
        await message_or_callback.answer(
            "❗ Совпадения не найдены.", reply_markup=await kb.owner_main(l10n=l10n)
        )
        await state.clear()


# @owner_users_management.message(UsersManagement.search_name)
# async def search_name(message: Message, state: FSMContext):
#     search_query = message.text.strip()
#     if not search_query:
#         await message.answer("Введите фамилию для поиска.")
#         return
#
#     users = await search_users_by_name(search_query)
#
#     if users:
#         user_list = "\n".join(
#             [(f"👤 ID: {user.id}.\n"
#               f" ├ <code>{user.name}</code>\n"
#               f" ├ <em>🎟️ TG: </em>@{user.tg_username} / <code>{user.tg_id}</code>\n"
#               f" ├ <em>☎️ Телефон: </em>{user.contact}\n"
#               f" ├ <em>📨 Email: </em>{user.email}\n"
#               f" └ <em>🗓️ Посещения: </em>{user.successful_bookings}\n\n") for user in users]
#         )
#         await message.answer(f"Найдены следующие пользователи:\n{user_list}")
#     else:
#         await message.answer("❗ Совпадения не найдены.", reply_markup=await kb.owner_main())
#     await state.clear()


@owner_users_management.message(UsersManagement.search_phone)
async def search_phone(message: Message, state: FSMContext, l10n: FluentLocalization):
    phone_number = message.text.strip()
    if not phone_number.isdigit():
        await message.answer("❗ Введите корректный номер телефона (только цифры).")
        return

    users = await search_users_by_phone(phone_number)

    if not users:
        await message.answer(
            "❗ Пользователь с таким номером телефона не найден.",
            reply_markup=await kb.owner_main(l10n=l10n),
        )
    else:
        response = ""
        for user in users:
            response += (
                f"👤 ID: {user.id}.\n"
                f" ├ <code>{user.name}</code>\n"
                f" ├ <em>🎟️ TG: </em>{user.tg_username} / <code>{user.tg_id}</code>\n"
                f" ├ <em>☎️ Телефон: </em>{user.contact}\n"
                f" ├ <em>📨 Email: </em>{user.email}\n"
                f" └ <em>🗓️ Посещения: </em>{user.successful_bookings}\n"
                f"<em>🪄️ Редактировать: </em>/edit_user_{user.id}\n"
                f"<em>❌ Удалить: </em>/delete_user_{user.id}\n\n"
            )

        await message.answer(
            response,
            reply_markup=await gkb.create_buttons(
                back_callback_data="manage_users", l10n=l10n
            ),
        )

    await state.clear()


@owner_users_management.message(UsersManagement.search_id)
async def search_id(message: Message, state: FSMContext, l10n: FluentLocalization):
    user_id = message.text.strip()
    if not user_id.isdigit():
        await message.answer("❗ Введите корректный ID (только цифры).")
        return

    user = await get_user_by_id(
        user_id,
    )

    if not user:
        await message.answer(
            "❗ Пользователь с таким ID не найден.",
            reply_markup=await kb.owner_main(l10n=l10n),
        )
    else:
        response = (
            f"👤 ID: {user.id}.\n"
            f" ├ <code>{user.name}</code>\n"
            f" ├ <em>🎟️ TG: </em>{user.tg_username} / <code>{user.tg_id}</code>\n"
            f" ├ <em>☎️ Телефон: </em>{user.contact}\n"
            f" ├ <em>📨 Email: </em>{user.email}\n"
            f" └ <em>🗓️ Посещения: </em>{user.successful_bookings}\n\n"
        )

        await message.answer(
            response,
            reply_markup=await kb.edit_keyboard(user.id, l10n=l10n),
        )

    await state.clear()


@owner_users_management.message(F.text.startswith("/edit_user_"))
@owner_users_management.callback_query(F.data.startswith("edit_user_"))
async def edit_user(event, state: FSMContext, l10n: FluentLocalization):
    # Проверяем, что это callback или сообщение
    if isinstance(event, CallbackQuery):
        user_id = event.data.split("_")[2]
        await state.update_data(user_id=user_id)
        await event.message.edit_text(
            "Что необходимо изменить?", reply_markup=await kb.edit_user(l10n=l10n)
        )
        await event.answer()

    elif isinstance(event, Message):
        user_id = event.text.split("_")[2]
        await state.update_data(user_id=user_id)
        await event.bot.delete_message(
            chat_id=event.chat.id, message_id=event.message_id - 1
        )
        # Удаляем сообщение перед ответом
        await event.delete()
        await event.answer(
            "Что необходимо изменить?", reply_markup=await kb.edit_user(l10n=l10n)
        )

    await state.set_state(UsersManagement.edit_user)


@owner_users_management.callback_query(
    F.data.startswith("current_edit_"), UsersManagement.edit_user
)
async def current_edit_user(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    tool = callback.data.split("_")[1]
    reply_keyboard = await gkb.create_buttons(l10n=l10n)
    if tool == "name":
        await callback.message.edit_text("Введите ФИО", reply_markup=reply_keyboard)
        await state.set_state(UsersManagement.edit_user_name)
        await callback.answer()
    elif tool == "phone":
        await callback.message.edit_text(
            "Введите новый номер телефона", reply_markup=reply_keyboard
        )
        await state.set_state(UsersManagement.edit_user_phone)
        await callback.answer()
    elif tool == "email":
        await callback.message.edit_text(
            "Введите новый Email", reply_markup=reply_keyboard
        )
        await state.set_state(UsersManagement.edit_user_email)
        await callback.answer()
    elif tool == "visits":
        await callback.message.edit_text(
            "Исправьте количество посещений", reply_markup=reply_keyboard
        )
        await state.set_state(UsersManagement.edit_user_visits)
        await callback.answer()


@owner_users_management.message(UsersManagement.edit_user_name)
async def edit_user_name(message: Message, state: FSMContext, l10n: FluentLocalization):
    new_name = message.text
    data = await state.get_data()
    user_id = data.get("user_id")
    await update_user_fields(
        user_id,
        name=new_name,
    )
    await message.answer(
        "Изменения сохранены.", reply_markup=await kb.owner_main(l10n=l10n)
    )
    await state.clear()


@owner_users_management.message(UsersManagement.edit_user_phone)
async def edit_user_phone(
    message: Message, state: FSMContext, l10n: FluentLocalization
):
    phone_number = message.text.strip()
    if not phone_number.isdigit():
        await message.answer("❗ Введите корректный номер телефона (только цифры).")
        return
    data = await state.get_data()
    user_id = data.get("user_id")
    await update_user_fields(
        user_id,
        contact=phone_number,
    )
    await message.answer(
        "Изменения сохранены.", reply_markup=await kb.owner_main(l10n=l10n)
    )
    await state.clear()


@owner_users_management.message(UsersManagement.edit_user_email)
async def edit_user_email(
    message: Message, state: FSMContext, l10n: FluentLocalization
):
    email_pattern = re.compile(r"[^@]+@[^@]+\.[^@]+")
    email = message.text
    if not email_pattern.match(email):
        await message.answer(
            "Неверный формат email. Пожалуйста, введите корректный email."
        )
        return
    data = await state.get_data()
    user_id = data.get("user_id")
    await update_user_fields(
        user_id,
        email=email,
    )
    await message.answer(
        "Изменения сохранены.", reply_markup=await kb.owner_main(l10n=l10n)
    )
    await state.clear()


@owner_users_management.message(UsersManagement.edit_user_visits)
async def edit_user_visits(
    message: Message, state: FSMContext, l10n: FluentLocalization
):
    successful_bookings = message.text.strip()
    if not successful_bookings.isdigit():
        await message.answer("❗ Введите только цифры.")
        return
    data = await state.get_data()
    user_id = data.get("user_id")
    await update_user_fields(
        user_id,
        successful_bookings=successful_bookings,
    )
    await message.answer(
        "Изменения сохранены.", reply_markup=await kb.owner_main(l10n=l10n)
    )
    await state.clear()


# @owner_users_management.message(F.text.startswith("/delete_user_"))
# @owner_users_management.callback_query(F.data.startswith("delete_user_"))
# async def delete_user(event, state: FSMContext, l10n: FluentLocalization):
#     if isinstance(event, CallbackQuery):
#         user_id = event.data.split("_")[2]
#         await state.update_data(user_id=user_id)
#         await delete_user_from_db(user_id)
#         await event.message.edit_text(
#             "Пользователь успешно удален.", reply_markup=await kb.owner_main(l10n=l10n)
#         )
#         await event.answer()
#     elif isinstance(event, Message):
#         user_id = event.text.split("_")[2]
#         await state.update_data(user_id=user_id)
#         await delete_user_from_db(user_id)
#         await event.bot.delete_message(
#             chat_id=event.chat.id, message_id=event.message_id - 1
#         )
#         # Удаляем сообщение перед ответом
#         await event.delete()
#         await event.answer(
#             "Пользователь успешно удален.", reply_markup=await kb.owner_main(l10n=l10n)
#         )
#     await state.clear()
@owner_users_management.message(F.text.startswith("/delete_user_"))
@owner_users_management.callback_query(F.data.startswith("delete_user_"))
async def delete_user(event, state: FSMContext, l10n: FluentLocalization):
    if isinstance(event, CallbackQuery):
        user_id = event.data.split("_")[2]
        await state.update_data(user_id=user_id)
        await delete_user_from_db(user_id)
        await event.message.edit_text(
            "Пользователь успешно удален.", reply_markup=await kb.owner_main(l10n=l10n)
        )
        await event.answer()
    elif isinstance(event, Message):
        user_id = event.text.split("_")[2]
        await state.update_data(user_id=user_id)
        await delete_user_from_db(user_id)

        # Проверяем, существует ли сообщение, прежде чем удалять
        try:
            # Пытаемся удалить предыдущее сообщение
            await event.bot.delete_message(
                chat_id=event.chat.id, message_id=event.message_id - 1
            )
        except Exception as e:
            # Логируем ошибку или обрабатываем ситуацию
            # print(f"Ошибка при удалении сообщения: {e}")
            pass

        # Удаляем текущее сообщение
        await event.delete()
        await event.answer(
            "Пользователь успешно удален.", reply_markup=await kb.owner_main(l10n=l10n)
        )
    await state.clear()


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
                f" ├ <em>🗓️ Посещения: </em>{user.successful_bookings}\n"
                f" └ <em>{'🇷🇺' if user.language_code == 'ru' else '🇺🇸'} Язык: </em>{user.language_code}\n"
                f"<em>🪄️ Редактировать: </em>/edit_user_{user.id}\n"
                f"<em>❌ Удалить: </em>/delete_user_{user.id}\n\n"
            )
        keyboard = await kb.users(
            prefix, "manage_users", page, len(users), page_size, end_index, l10n=l10n
        )
    else:
        text = "📨 Пу-пу-пу:\n\n" "Нет ни одного пользователя.. 🤷‍️"
        keyboard = await kb.owner_main(l10n=l10n)

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
