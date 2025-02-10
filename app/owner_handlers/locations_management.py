from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from fluent.runtime import FluentLocalization

import app.owner_kb.keyboards as kb
from app.database.requests import (
    get_all_locations,
    create_location,
    delete_location,
    get_location_by_id,
)
from filters import IsOwnerFilter

owner_locations_management = Router()

# Применяем фильтр для всех хэндлеров на уровне роутера
owner_locations_management.message.filter(IsOwnerFilter(is_owner=True))
owner_locations_management.callback_query.filter(IsOwnerFilter(is_owner=True))


class LocationsManagement(StatesGroup):
    list_locations = State()
    add_location = State()
    del_location = State()


@owner_locations_management.callback_query(F.data == "manage_locations")
async def manage_locations(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    await state.clear()
    await callback.message.edit_text(
        text="💠 Выберите действие:", reply_markup=await kb.manage_locations(l10n=l10n)
    )
    await callback.answer()


@owner_locations_management.callback_query(F.data == "list_locations")
@owner_locations_management.callback_query(F.data.startswith("my_location_page_"))
async def list_promocodes(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    await state.clear()
    page = 1  # Стартовая страница

    if callback.data.startswith("my_location_page_"):
        page = int(callback.data.split("_")[-1])

    locations = await get_all_locations()
    await state.update_data(locations=locations)

    page_size = 8
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    current_page_locations = locations[start_index:end_index]

    if current_page_locations:
        text = f"<b>📨 Список всех локаций (страница {page}):</b>\n\n"
        for i, location in enumerate(current_page_locations, 1):
            text += f"{i}. <code>{location.name}</code>\n\n"
        keyboard = await kb.locations(
            "my_location_page_",
            "manage_locations",
            page,
            len(locations),
            page_size,
            end_index,
            l10n=l10n,
        )
    else:
        text = "📨 Пу-пу-пу:\n\n" "Локации пока не созданы.. 🤷‍️"
        keyboard = await kb.owner_main(l10n=l10n)

    # Сравниваем текст и клавиатуру
    current_message = callback.message.text
    current_keyboard = callback.message.reply_markup

    # Проверяем, изменилось ли сообщение или клавиатура
    if (current_message != text) and (current_keyboard != keyboard):
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")

    await callback.answer()


@owner_locations_management.callback_query(F.data == "add_location")
async def add_new_location(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    await callback.message.edit_text("Введите название локации: ")
    await state.set_state(LocationsManagement.add_location)


@owner_locations_management.message(LocationsManagement.add_location)
async def add_location(message: Message, state: FSMContext, l10n: FluentLocalization):
    location = message.text
    await state.update_data(location=location)
    await create_location(location)
    await message.answer(
        f"📨 Создана локация: <code>{location}</code>",
        reply_markup=await kb.owner_main(l10n=l10n),
    )
    await state.clear()


@owner_locations_management.callback_query(F.data == "delete_location")
async def delete_loc(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    await state.set_state(LocationsManagement.del_location)
    list_of_locations = await get_all_locations()
    await callback.message.edit_text(
        "Выберите локацию для удаления: ",
        reply_markup=await kb.list_locations(list_of_locations, l10n=l10n),
    )
    await callback.answer()


@owner_locations_management.callback_query(F.data.startswith("location_"))
async def del_location(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    location_id = callback.data.split("_")[1]
    await state.update_data(location_id=location_id)
    location = await get_location_by_id(location_id)
    name = location.name
    await delete_location(location_id)
    await callback.message.edit_text(
        f"📨 Удалена локация: <code>{name}</code>",
        reply_markup=await kb.owner_main(l10n=l10n),
    )
    await callback.answer()
    await state.clear()
