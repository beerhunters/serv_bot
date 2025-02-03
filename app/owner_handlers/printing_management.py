from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

import app.owner_kb.keyboards as kb
import app.general_keyboards as gkb
from app.database.requests import get_adjustments, update_adjustment
from filters import IsOwnerFilter

owner_print_management = Router()

# Применяем фильтр для всех хэндлеров на уровне роутера
owner_print_management.message.filter(IsOwnerFilter(is_owner=True))
owner_print_management.callback_query.filter(IsOwnerFilter(is_owner=True))


class PrintManagement(StatesGroup):
    price = State()
    new_price = State()


@owner_print_management.callback_query(F.data == "manage_printing")
async def manage_printing(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    adjustments = await get_adjustments()
    printing_available = adjustments.get("printing_available")
    scanning_available = adjustments.get("scanning_available")
    free_printing_available = adjustments.get("free_printing_available")
    await state.update_data(
        printing_available=printing_available,
        scanning_available=scanning_available,
        free_printing_available=free_printing_available,
    )
    await callback.message.edit_text(
        text="💠 Выберите действие:",
        reply_markup=await kb.manage_printing(
            printing_available, scanning_available, free_printing_available
        ),
    )
    await callback.answer()


@owner_print_management.callback_query(F.data.startswith("toggle_"))
async def toggle_feature(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    feature_map = {
        "toggle_printing": "printing_available",
        "toggle_scanning": "scanning_available",
        "toggle_free_printing": "free_printing_available",
    }
    feature_key = feature_map.get(callback.data)

    if not feature_key:
        await callback.answer(
            "Ошибка: не удалось определить действие.", show_alert=True
        )
        return

    feature_info = data.get(f"{feature_key}")
    new_state = not feature_info["state"]

    await update_adjustment(name=feature_key, state=new_state)

    if feature_key == "free_printing_available":
        status_message = f"{'🟢 Включена бесплатная печать! 🟢' if new_state else '💰 Выключена бесплатная печать! 💰'}"
    elif feature_key == "printing_available":
        status_message = (
            f"{'🟢 Включена печать! 🟢' if new_state else '💰 Выключена печать! 💰'}"
        )
    elif feature_key == "scanning_available":
        status_message = f"{'🟢 Включено сканирование! 🟢' if new_state else '💰 Выключено сканирование! 💰'}"
    await callback.message.edit_text(
        f"{status_message}\n",
        # reply_markup=await kb.back_button("manage_printing")
        reply_markup=await gkb.create_buttons(back_callback_data="manage_printing"),
    )
    await callback.answer()


@owner_print_management.callback_query(F.data == "change_price_printing")
async def change_price(callback: CallbackQuery, state: FSMContext):
    await state.set_state(PrintManagement.price)
    await callback.message.edit_text("💠 Введите новую стоимость печати:")
    await state.set_state(PrintManagement.new_price)


@owner_print_management.message(PrintManagement.new_price)
async def set_new_price(message: Message, state: FSMContext):
    try:
        new_price = int(message.text)
    except ValueError:
        await message.answer("‼️ Введите целое число: ")
        return
    await update_adjustment(name="printing_available", value=new_price)
    await message.answer(
        "🟢 Стоимость печати изменена!",
        reply_markup=await gkb.create_buttons(back_callback_data="manage_printing"),
    )
    await state.clear()
