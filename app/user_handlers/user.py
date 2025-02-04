import random
import re

from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    FSInputFile,
)
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from fluent.runtime import FluentLocalization

from app.database.requests import create_or_update_user
import app.user_kb.keyboards as kb
from config import BOT_ADMINS, INFO_USER, BOT_OWNERS, GREETINGS_USER, GROUP_ID, REG_INFO
from filters import IsUserFilter
from tools.tools import send_localized_message

user_router = Router()

# Применяем фильтр для всех хэндлеров на уровне роутера
user_router.message.filter(IsUserFilter(is_user=True))
user_router.callback_query.filter(IsUserFilter(is_user=True))


class Reg(StatesGroup):
    name = State()
    contact = State()
    email = State()


# @user_router.message(CommandStart())
# @user_router.message(Command("cancel"))
# @user_router.callback_query(F.data == "main_menu")
# async def cmd_start(message: Message | CallbackQuery, state: FSMContext):
#     # 1 / 0
#     user = await create_or_update_user(
#         message.from_user.id, tg_username=message.from_user.username
#     )
#
#     if user and user.name:
#         # greeting_text = f'Доброго времени суток, {user.name}!'
#         greeting_text = (
#             random.choice(GREETINGS_USER).format(user.name.title()) + " 👋🏻"
#         )
#
#         # Если сообщение от пользователя
#         if isinstance(message, Message):
#             await message.answer(greeting_text, reply_markup=await kb.user_main())
#
#         elif isinstance(message, CallbackQuery):
#             # Получаем текущее сообщение и клавиатуру
#             current_message = message.message.text
#             current_keyboard_text = str(message.message.reply_markup)
#
#             # Проверяем, изменился ли текст сообщения или клавиатура
#             if (current_message != greeting_text) or (
#                 current_keyboard_text != str(await kb.user_main())
#             ):
#                 # Если изменилось, редактируем сообщение
#                 if message.message.content_type == "text":
#                     await message.message.edit_text(
#                         greeting_text, reply_markup=await kb.user_main()
#                     )
#                 else:
#                     # Если не текстовое сообщение, отправляем новое
#                     await message.message.reply(
#                         greeting_text, reply_markup=await kb.user_main()
#                     )
#             else:
#                 # Если изменений нет, отправляем пустой ответ
#                 await message.answer()
#
#         await state.clear()
#     else:
#         registration_text = (
#             "Добро пожаловать! Пожалуйста пройдите регистрацию.\n\nВведите Ваше ФИО."
#         )
#
#         # Если сообщение от пользователя
#         if isinstance(message, Message):
#             await message.answer(registration_text)
#
#         elif isinstance(message, CallbackQuery):
#             # Получаем текущее сообщение и проверяем, нужно ли его редактировать
#             current_message = message.message.text
#             if current_message != registration_text:
#                 await message.message.edit_text(registration_text)
#             await message.answer()
#
#         await state.set_state(Reg.name)
@user_router.message(CommandStart())
@user_router.message(Command("cancel"))
@user_router.callback_query(F.data == "main_menu")
async def cmd_start(
    message: Message | CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    # Создание или обновление пользователя
    user = await create_or_update_user(
        message.from_user.id, tg_username=message.from_user.username
    )

    if user:
        await send_localized_message(
            message,
            l10n,
            "greeting",  # Ключ локализованного приветствия
            reply_markup=await kb.user_main(),
        )
        await state.clear()
    else:
        await send_localized_message(
            message,
            l10n,
            "registration",  # Ключ для локализованного текста регистрации
            reply_markup=await kb.user_main(),
        )
        await state.set_state(Reg.name)


# @user_router.message(Reg.name)
# async def reg_name(message: Message, state: FSMContext):
#     await state.update_data(name=message.text)
#     if message.from_user.username is None:
#         tg_username = f"<a href='tg://user?id={str(message.from_user.id)}'>{message.from_user.first_name}</a>"
#     else:
#         # Если username есть, проверяем, начинается ли он с '@' и добавляем, если нет
#         tg_username = (
#             message.from_user.username
#             if message.from_user.username.startswith("@")
#             else "@" + message.from_user.username
#         )
#     await state.update_data(tg_username=tg_username)
#     await state.set_state(Reg.contact)
#     photo_path = "docs/send_contact.jpg"
#     input_file = FSInputFile(photo_path)
#     await message.answer_photo(
#         photo=input_file,
#         caption="Отправьте номер телефона, нажав на кнопку '📲Отправить контакт'",
#         reply_markup=kb.contact,
#     )
@user_router.message(Reg.name)
async def reg_name(message: Message, state: FSMContext, l10n: FluentLocalization):
    await state.update_data(name=message.text)
    if message.from_user.username is None:
        tg_username = f"<a href='tg://user?id={str(message.from_user.id)}'>{message.from_user.first_name}</a>"
    else:
        # Если username есть, проверяем, начинается ли он с '@' и добавляем, если нет
        tg_username = (
            message.from_user.username
            if message.from_user.username.startswith("@")
            else "@" + message.from_user.username
        )
    await state.update_data(tg_username=tg_username)
    await state.set_state(Reg.contact)
    photo_path = "docs/send_contact.jpg"
    input_file = FSInputFile(photo_path)
    await message.answer_photo(
        photo=input_file,
        caption=l10n.format_value("send_contact"),
        reply_markup=kb.contact,
    )


# @user_router.message(Reg.contact)
# async def reg_contact(message: Message, state: FSMContext):
#     # Проверяем, если контакт отправлен корректно
#     if message.contact:
#         await state.update_data(contact=message.contact.phone_number)
#         await state.set_state(Reg.email)
#         await message.answer("Введите email.")
#     else:
#         # Если пользователь отправил текст вместо контакта
#         await message.answer(
#             "Пожалуйста, отправьте номер телефона, нажав на кнопку '📲Отправить контакт'",
#             reply_markup=kb.contact,
#         )
@user_router.message(Reg.contact)
async def reg_contact(message: Message, state: FSMContext, l10n: FluentLocalization):
    # Проверяем, если контакт отправлен корректно
    if message.contact:
        await state.update_data(contact=message.contact.phone_number)
        await state.set_state(Reg.email)
        await send_localized_message(
            message,
            l10n,
            "enter_mail",  # Ключ для локализованного текста регистрации
        )
    else:
        # Если пользователь отправил текст вместо контакта
        await send_localized_message(
            message,
            l10n,
            "send_contact",  # Ключ для локализованного текста регистрации
            reply_markup=kb.contact,
        )


# @user_router.message(Reg.email)
# async def reg_email(message: Message, state: FSMContext):
#     email_pattern = re.compile(r"[^@]+@[^@]+\.[^@]+")
#     email = message.text
#
#     # Проверка на None
#     if not isinstance(email, str):
#         await message.answer(
#             "Некорректный ввод. Пожалуйста, введите ваш email текстом."
#         )
#         return
#
#     # Проверка формата email
#     if not email_pattern.match(email):
#         await message.answer(
#             "Неверный формат email. Пожалуйста, введите корректный email."
#         )
#         return
#
#     # Сохраняем email в состояние
#     await state.update_data(email=email)
#     data = await state.get_data()
#
#     # Используем create_or_update_user для обновления данных пользователя
#     await create_or_update_user(
#         message.from_user.id,
#         tg_username=data.get("tg_username"),
#         name=data.get("name"),
#         contact=data.get("contact"),
#         email=email,
#     )
#     await state.clear()
#
#     invite_link = await message.bot.create_chat_invite_link(
#         chat_id=GROUP_ID,
#         name="Вступить в группу",  # Название ссылки (опционально)
#         member_limit=1,  # Лимит (опционально, например, 1 пользователь)
#     )
#
#     # Уведомление о регистрации
#     successfully_registered = (
#         f"✨Вы успешно прошли регистрацию!✨ \n\n"
#         + REG_INFO.format(invite_link.invite_link)
#     )
#     await message.answer(successfully_registered, reply_markup=await kb.user_main())
#
#     # Разбиваем ФИО по пробелам
#     name_parts = data["name"].split()
#     last_name = name_parts[0] if len(name_parts) > 0 else "Не указано"
#     first_name = name_parts[1] if len(name_parts) > 1 else "Не указано"
#     middle_name = name_parts[2] if len(name_parts) > 2 else "Не указано"
#
#     # Формируем сообщение для админов
#     info_new_user = (
#         "<b>👤 Новый резидент ✅</b> \n\n"
#         f"<b>📋 ФИО:</b>\n"
#         f"Фамилия: <code>{last_name}</code>\n"
#         f"Имя: <code>{first_name}</code>\n"
#         f"Отчество: <code>{middle_name}</code>\n"
#         f"<b>🎟️ TG: </b> {data['tg_username']}\n"
#         f"<b>☎️ Телефон: </b> <code>{data['contact']}</code>\n"
#         f"<b>📨 Email: </b> <code>{email}</code>\n"
#     )
#     for admin in BOT_ADMINS:
#         try:
#             await message.bot.send_message(
#                 admin, info_new_user, reply_markup=await kb.create_buttons()
#             )
#         except Exception as e:
#             await message.bot.send_message(
#                 BOT_OWNERS[0],
#                 f"Пользователь {admin} не зарегистрирован в боте.\nОшибка: {e}",
#             )
#         # # Создаем ссылку-приглашение для группы
#         # GROUP_ID = -1002444417785  # Укажите ID вашей группы
#         # try:
#         #     invite_link = await message.bot.create_chat_invite_link(
#         #         chat_id=GROUP_ID,
#         #         name="Вступить в группу",  # Название ссылки (опционально)
#         #         member_limit=1,  # Лимит (опционально, например, 1 пользователь)
#         #     )
#         #
#         #     # Отправляем пользователю ссылку
#         #     await message.answer(
#         #         # f"✨ Вы успешно прошли регистрацию! ✨\n\n"
#         #         f"✨ Присоединяйтесь к нашей группе, перейдя по ссылке:\n{invite_link.invite_link}"
#         #     )
#         # except Exception as e:
#         #     await message.answer(
#         #         "Ошибка при создании ссылки-приглашения. Пожалуйста, обратитесь к администратору."
#         #     )
#         #     # Логируем ошибку
#         #     await message.bot.send_message(
#         #         BOT_OWNERS[0],
#         #         f"Ошибка при создании ссылки для группы {GROUP_ID}:\n{e}",
#         #     )
@user_router.message(Reg.email)
async def reg_email(message: Message, state: FSMContext, l10n: FluentLocalization):
    email_pattern = re.compile(r"[^@]+@[^@]+\.[^@]+")
    email = message.text

    # Проверка на None
    if not isinstance(email, str):
        await send_localized_message(
            message,
            l10n,
            "invalid_mail_no_text",  # Ключ для локализованного текста регистрации
        )
        return

    # Проверка формата email
    if not email_pattern.match(email):
        await send_localized_message(
            message,
            l10n,
            "invalid_mail_not_pattern",  # Ключ для локализованного текста регистрации
        )
        return

    # Сохраняем email в состояние
    await state.update_data(email=email)
    data = await state.get_data()

    # Используем create_or_update_user для обновления данных пользователя
    await create_or_update_user(
        message.from_user.id,
        tg_username=data.get("tg_username"),
        name=data.get("name"),
        contact=data.get("contact"),
        email=email,
    )
    await state.clear()

    invite_link = await message.bot.create_chat_invite_link(
        chat_id=GROUP_ID,
        name="Вступить в группу",  # Название ссылки (опционально)
        member_limit=1,  # Лимит (опционально, например, 1 пользователь)
    )

    # Уведомление о регистрации
    successfully_registered = (
        f"✨Вы успешно прошли регистрацию!✨ \n\n"
        + REG_INFO.format(invite_link.invite_link)
    )
    await message.answer(successfully_registered, reply_markup=await kb.user_main())

    # Разбиваем ФИО по пробелам
    name_parts = data["name"].split()
    last_name = name_parts[0] if len(name_parts) > 0 else "Не указано"
    first_name = name_parts[1] if len(name_parts) > 1 else "Не указано"
    middle_name = name_parts[2] if len(name_parts) > 2 else "Не указано"

    # Формируем сообщение для админов
    info_new_user = (
        "<b>👤 Новый резидент ✅</b> \n\n"
        f"<b>📋 ФИО:</b>\n"
        f"Фамилия: <code>{last_name}</code>\n"
        f"Имя: <code>{first_name}</code>\n"
        f"Отчество: <code>{middle_name}</code>\n"
        f"<b>🎟️ TG: </b> {data['tg_username']}\n"
        f"<b>☎️ Телефон: </b> <code>{data['contact']}</code>\n"
        f"<b>📨 Email: </b> <code>{email}</code>\n"
    )
    for admin in BOT_ADMINS:
        try:
            await message.bot.send_message(
                admin, info_new_user, reply_markup=await kb.create_buttons()
            )
        except Exception as e:
            await message.bot.send_message(
                BOT_OWNERS[0],
                f"Пользователь {admin} не зарегистрирован в боте.\nОшибка: {e}",
            )


# @user_router.callback_query(F.data == "info_user")
# async def info(callback: CallbackQuery):
#     await callback.message.edit_text(INFO_USER, reply_markup=await kb.create_buttons())
#     await callback.answer()
@user_router.callback_query(F.data == "info_user")
async def info(callback: CallbackQuery, l10n: FluentLocalization):
    await send_localized_message(
        callback,
        l10n,
        "info_user",  # Ключ для локализованного текста регистрации
        reply_markup=await kb.create_buttons(),
    )


@user_router.message(Command("test_error"))
async def test_error_handler(message: Message):
    raise ValueError("Тестовая ошибка!")
