from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from fluent.runtime import FluentLocalization

import app.owner_kb.keyboards as kb
import app.general_keyboards as gkb
from app.database.requests import (
    get_admins_from_db,
    save_admin_to_db,
    delete_admin_by_id,
)
from filters import IsOwnerFilter

owner_admin_management = Router()

# Применяем фильтр для всех хэндлеров на уровне роутера
owner_admin_management.message.filter(IsOwnerFilter(is_owner=True))
owner_admin_management.callback_query.filter(IsOwnerFilter(is_owner=True))


class AdminManagement(StatesGroup):
    add_admin = State()
    del_admin = State()


@owner_admin_management.callback_query(F.data == "manage_admin")
async def manage_admin(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    await state.clear()
    await callback.message.edit_text(
        text="💠 Выберите действие:", reply_markup=await kb.manage_admin(l10n=l10n)
    )
    await callback.answer()


@owner_admin_management.callback_query(F.data == "list_admins")
async def list_admins(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    admins = await get_admins_from_db()
    if admins:
        text = "📃 Список администраторов:\n"
        for i, admin in enumerate(admins, 1):
            admin_id, tg_id, tg_username, name = admin
            text += f"{i}. {tg_id} - {tg_username or 'нет юзернейма'} - {name or 'имя не указано'}\n"
    else:
        text = "😕 Нет администраторов"

    await callback.message.edit_text(
        text=text,
        reply_markup=await gkb.create_buttons(
            back_callback_data="manage_admin", l10n=l10n
        ),
    )
    await callback.answer()


@owner_admin_management.callback_query(F.data == "add_admin")
async def add_admin(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    await callback.message.delete()
    message = await callback.message.answer(
        "Пожалуйста, выберите пользователя, которого хотите назначить администратором.",
        reply_markup=await kb.request_user_button(),  # Обычная клавиатура
    )
    await state.update_data(message_id=message.message_id)
    await state.set_state(AdminManagement.add_admin)


@owner_admin_management.message(AdminManagement.add_admin, F.user_shared)
async def handle_shared_contact(
    message: Message, state: FSMContext, l10n: FluentLocalization
):
    # Получаем ID выбранного пользователя
    user_id = message.user_shared.user_id
    # Сохраняем в БД или используем по назначению
    await save_admin_to_db(user_id)
    await message.answer(
        f"✅ Вы добавили пользователя с ID {user_id} в администраторы",
        reply_markup=await kb.owner_main(l10n=l10n),
    )
    data = await state.get_data()
    await message.bot.delete_message(
        chat_id=message.chat.id, message_id=data["message_id"]
    )
    await state.clear()


@owner_admin_management.callback_query(F.data == "delete_admin")
async def del_admin(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    # await callback.answer("Функция в разработке", show_alert=True)
    admins = await get_admins_from_db()
    await callback.message.edit_text(
        "Пожалуйста, выберите пользователя, которого хотите удалить из администраторов.",
        reply_markup=await kb.list_of_admins(admins, l10n=l10n),
    )
    await state.set_state(AdminManagement.del_admin)


@owner_admin_management.callback_query(
    AdminManagement.del_admin, F.data.startswith("admin_")
)
async def process_del_admin(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    admin_id = callback.data.split("_")[1]
    success = await delete_admin_by_id(admin_id)
    if success:
        text = f"❌ Администратор с ID {admin_id} был успешно удалён."
    else:
        text = f"❔ Администратор с ID {admin_id} не найден."
    await callback.message.edit_text(text, reply_markup=await kb.owner_main(l10n=l10n))
    await state.clear()
