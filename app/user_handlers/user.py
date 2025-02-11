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

from config import BOT_ADMINS, BOT_OWNERS, GROUP_ID, REG_INFO
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
    if user and user.name:
        await send_localized_message(
            message,
            l10n,
            "greeting",
            reply_markup=await kb.user_main(l10n=l10n),
        )
        await state.clear()
    else:
        await send_localized_message(
            message,
            l10n,
            "registration",
        )
        await state.set_state(Reg.name)


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
        reply_markup=await kb.create_contact_button(l10n=l10n),
    )


@user_router.message(Reg.contact)
async def reg_contact(message: Message, state: FSMContext, l10n: FluentLocalization):
    # Проверяем, если контакт отправлен корректно
    if message.contact:
        await state.update_data(contact=message.contact.phone_number)
        await state.set_state(Reg.email)
        await send_localized_message(
            message,
            l10n,
            "enter_mail",
        )
    else:
        # Если пользователь отправил текст вместо контакта
        await send_localized_message(
            message,
            l10n,
            "send_contact",
            reply_markup=await kb.create_contact_button(l10n=l10n),
        )


@user_router.message(Reg.email)
async def reg_email(message: Message, state: FSMContext, l10n: FluentLocalization):
    email_pattern = re.compile(r"[^@]+@[^@]+\.[^@]+")
    email = message.text

    # Проверка на None
    if not isinstance(email, str):
        await send_localized_message(
            message,
            l10n,
            "invalid_mail_no_text",
        )
        return

    # Проверка формата email
    if not email_pattern.match(email):
        await send_localized_message(
            message,
            l10n,
            "invalid_mail_not_pattern",
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

    # Создаем ссылку для приглашения
    invite_link = await message.bot.create_chat_invite_link(
        chat_id=GROUP_ID,
        name=l10n.format_value(
            "join_group"
        ),  # Используем локализованный текст для имени группы
        member_limit=1,
    )
    # invite_link = ""
    successfully_registered = f"{l10n.format_value('registration_success')}\n\n"
    successfully_registered += l10n.format_value(
        "registration_info", {"invite_link": invite_link}
    )
    # successfully_registered = "Ok"
    await message.answer(
        successfully_registered, reply_markup=await kb.user_main(l10n=l10n)
    )

    # Разбиваем ФИО по пробелам
    name_parts = data["name"].split()
    last_name = (
        name_parts[0] if len(name_parts) > 0 else l10n.format_value("not_provided")
    )
    first_name = (
        name_parts[1] if len(name_parts) > 1 else l10n.format_value("not_provided")
    )
    middle_name = (
        name_parts[2] if len(name_parts) > 2 else l10n.format_value("not_provided")
    )
    tg_username = data["tg_username"]
    contact = data["contact"]

    # Локализованное сообщение для администраторов
    info_new_user = f"{l10n.format_value('new_resident')}\n\n"
    info_new_user += f"{l10n.format_value('user_data')}\n"
    info_new_user += f"{l10n.format_value('last_name', {'last_name': last_name})}\n"
    info_new_user += f"{l10n.format_value('first_name', {'first_name': first_name})}\n"
    info_new_user += (
        f"{l10n.format_value('middle_name', {'middle_name': middle_name})}\n"
    )
    info_new_user += (
        f"{l10n.format_value('tg_username', {'tg_username': tg_username})}\n"
    )
    info_new_user += f"{l10n.format_value('phone', {'contact': contact})}\n"
    info_new_user += f"{l10n.format_value('email', {'email': email})}\n"

    # Отправка сообщения каждому админу
    for admin in BOT_ADMINS:
        try:
            await message.bot.send_message(
                admin,
                info_new_user,
                reply_markup=await kb.create_buttons(l10n=l10n),
            )
        except Exception as e:
            await message.bot.send_message(
                BOT_OWNERS[0],
                f"{l10n.format_value('admin_error')}: {admin}\n{l10n.format_value('error_message')}: {e}",
            )


@user_router.callback_query(F.data == "info_user")
async def info(callback: CallbackQuery, l10n: FluentLocalization):
    await send_localized_message(
        callback,
        l10n,
        "info_user",
        reply_markup=await kb.create_buttons(l10n=l10n),
    )


@user_router.message(Command("test_error"))
async def test_error_handler(message: Message, l10n: FluentLocalization):
    raise ValueError(l10n.format_value("test_error"))
