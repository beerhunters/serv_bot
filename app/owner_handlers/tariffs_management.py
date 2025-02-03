from typing import Union

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

import app.owner_kb.keyboards as kb
import app.general_keyboards as gkb
from app.database.requests import (
    get_all_tariffs,
    get_tariff_by_id,
    create_or_update_tariff,
    delete_tariff,
)
from filters import IsOwnerFilter

owner_tariff_management = Router()

# Применяем фильтр для всех хэндлеров на уровне роутера
owner_tariff_management.message.filter(IsOwnerFilter(is_owner=True))
owner_tariff_management.callback_query.filter(IsOwnerFilter(is_owner=True))


class TariffManagement(StatesGroup):
    # add_tariff = State()
    add_tariff_name = State()
    add_tariff_description = State()
    add_tariff_price = State()
    add_tariff_service_id = State()
    finish_add_tariff = State()
    del_tariff = State()
    edit_tariff = State()
    select_changes = State()
    edit_tariff_price = State()


@owner_tariff_management.callback_query(F.data == "manage_tariffs")
async def manage_tariffs(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        text="💠 Выберите действие:", reply_markup=await kb.manage_tariffs()
    )
    await callback.answer()


@owner_tariff_management.callback_query(F.data == "list_tariffs")
@owner_tariff_management.callback_query(F.data.startswith("my_tariff_page_"))
async def list_promocodes(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    page = 1  # Стартовая страница

    if callback.data.startswith("my_tariff_page_"):
        page = int(callback.data.split("_")[-1])

    tariffs = await get_all_tariffs()
    await state.update_data(tariffs=tariffs)

    page_size = 4
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    current_page_tariffs = tariffs[start_index:end_index]

    if current_page_tariffs:
        text = f"<b>📨 Список всех тарифов (страница {page}):</b>\n\n"
        for i, tariff in enumerate(current_page_tariffs, 1):
            text += (
                f"{i}. <code>{tariff.name}</code>\n"
                f" ├ <em>Описание: </em>{tariff.description}\n"
                f" ├ <em>Цена: </em>{tariff.price} руб.\n"
                f" └ <em>Статус: </em>{'Активен 🟢' if tariff.is_active else 'Не активен 🛑'}\n"
                f"<em>🪄️ Редактировать: </em>/edit_tariff_{tariff.id}\n"
                f"<em>❌ Удалить: </em>/delete_tariff_{tariff.id}\n\n"
            )
        keyboard = await kb.tariffs(
            "my_tariff_page_",
            "manage_tariffs",
            page,
            len(tariffs),
            page_size,
            end_index,
        )
    else:
        text = "📨 Пу-пу-пу:\n\n" "Тарифы пока не созданы.. 🤷‍️"
        keyboard = await kb.owner_main()

    # Сравниваем текст и клавиатуру
    current_message = callback.message.text
    current_keyboard = callback.message.reply_markup

    # Проверяем, изменилось ли сообщение или клавиатура
    if (current_message != text) and (current_keyboard != keyboard):
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")

    await callback.answer()


# @owner_tariff_management.callback_query(F.data == "select_tariff")
# @owner_tariff_management.callback_query(F.data == "delete_tariff")
# async def select_tariff(callback: CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     if callback.data == "select_tariff":
#         text = "Выберите тариф, который хотели бы изменить: "
#         tariffs = data["tariffs"]
#         await state.set_state(TariffManagement.edit_tariff)
#     if callback.data == "delete_tariff":
#         tariffs = await get_all_tariffs()
#         text = "Выберите тариф, который хотели бы удалить: "
#         await state.set_state(TariffManagement.del_tariff)
#     await callback.message.edit_text(text, reply_markup=await kb.list_tariffs(tariffs))


@owner_tariff_management.message(F.text.startswith("/edit_tariff_"))
# @owner_tariff_management.callback_query(
#     F.data.startswith("tariff_"), TariffManagement.edit_tariff
# )
async def edit_tariff(event: Message, state: FSMContext):
    # if isinstance(event, CallbackQuery):
    #     tariff_id = int(event.data.split("_")[2])
    #     tariff = await get_tariff_by_id(tariff_id)
    #     await state.update_data(
    #         tariff_id=tariff_id,
    #         name=tariff.name,
    #         price=tariff.price,
    #         is_active=tariff.is_active,
    #     )
    #     await event.message.edit_text(
    #         "Можно изменить цену или включить/отключить тариф\nВыберите действие:",
    #         reply_markup=await kb.tariff_changes(tariff.is_active),
    #     )
    # elif isinstance(event, Message):
    tariff_id = int(event.text.split("_")[2])
    tariff = await get_tariff_by_id(tariff_id)
    await state.update_data(
        tariff_id=tariff_id,
        name=tariff.name,
        price=tariff.price,
        is_active=tariff.is_active,
    )
    await event.bot.delete_message(
        chat_id=event.chat.id, message_id=event.message_id - 1
    )
    # Удаляем сообщение перед ответом
    await event.delete()
    await event.answer(
        "Можно изменить цену или включить/отключить тариф\nВыберите действие:",
        reply_markup=await kb.tariff_changes(tariff.is_active),
    )
    # tariff = await get_tariff_by_id(tariff_id)
    # await state.update_data(
    #     tariff_id=tariff_id,
    #     name=tariff.name,
    #     price=tariff.price,
    #     is_active=tariff.is_active,
    # )
    await state.set_state(TariffManagement.select_changes)
    # await event.message.edit_text(
    #     "Можно изменить цену или включить/отключить тариф\nВыберите действие:",
    #     reply_markup=await kb.tariff_changes(tariff.is_active),
    # )


# async def handle_tariff_update(event: Union[Message, CallbackQuery], state: FSMContext):
#     """Вспомогательная функция для обновления информации о тарифе."""
#     if isinstance(event, CallbackQuery):
#         tariff_id = int(event.data.split("_")[2])
#     elif isinstance(event, Message):
#         tariff_id = int(event.text.split("_")[2])
#
#     # Получаем тариф по ID
#     tariff = await get_tariff_by_id(tariff_id)
#
#     # Обновляем данные в состоянии
#     await state.update_data(
#         tariff_id=tariff_id,
#         name=tariff.name,
#         price=tariff.price,
#         is_active=tariff.is_active,
#     )
#
#     return tariff
#
#
# @owner_tariff_management.message(F.text.startswith("/edit_tariff_"))
# async def edit_tariff(event: Union[Message, CallbackQuery], state: FSMContext):
#     tariff = await handle_tariff_update(event, state)
#
#     # Удаляем предыдущее сообщение, если это Message
#     if isinstance(event, Message):
#         await event.bot.delete_message(
#             chat_id=event.chat.id, message_id=event.message_id - 1
#         )
#         await event.delete()
#
#     # Отправляем новое сообщение с кнопками выбора действий
#     await event.answer(
#         "Можно изменить цену или включить/отключить тариф\nВыберите действие:",
#         reply_markup=await kb.tariff_changes(tariff.is_active),
#     )
#
#     # Устанавливаем состояние для выбора изменений
#     await state.set_state(TariffManagement.select_changes)


@owner_tariff_management.callback_query(F.data == "change_price_tariff")
async def change_price_tariff(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите новую цену тарифа: ")
    await state.set_state(TariffManagement.edit_tariff_price)


@owner_tariff_management.message(TariffManagement.edit_tariff_price)
async def edit_tariff_price(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        new_price = int(message.text)
    except ValueError:
        await message.answer("‼️ Введите целое число: ")
        return
    tariff_name = data.get("name")
    await create_or_update_tariff(name=tariff_name, price=new_price)
    await message.answer(
        "🟢 Цена тарифа успешно изменена!",
        reply_markup=await gkb.create_buttons(back_callback_data="manage_tariffs"),
    )
    await state.clear()


@owner_tariff_management.callback_query(
    F.data.startswith("switch_"), TariffManagement.select_changes
)
async def switch_on_off_tariff(callback: CallbackQuery, state: FSMContext):
    # "switch_off" if is_active else "switch_on"
    status = callback.data.split("_")[1]
    if status == "on":
        new_status = True
    else:
        new_status = False
    data = await state.get_data()
    tariff_name = data.get("name")
    await create_or_update_tariff(tariff_name, is_active=new_status)
    # status_text = f"{"🟢" if new_status else "🔴"} Тариф - '{tariff_name}' успешно {"<b>Включен</b>" if new_status else "<b>Выключен</b>"}"
    status_text = f"Тариф - '{tariff_name}' успешно изменен"
    await callback.message.edit_text(status_text, reply_markup=await kb.owner_main())
    await state.clear()
    await callback.answer()


@owner_tariff_management.message(F.text.startswith("/delete_tariff_"))
# @owner_tariff_management.callback_query(
#     F.data.startswith("tariff_"), TariffManagement.del_tariff
# )
async def del_tariff(event: Message, state: FSMContext):
    tariff_id = int(event.text.split("_")[2])
    await delete_tariff(tariff_id)
    # await event.message.edit_text(
    #     f"👌🏼Тариф успешно удален ❌", reply_markup=await kb.owner_main()
    # )
    # await state.clear()
    # await event.answer()
    await event.bot.delete_message(
        chat_id=event.chat.id, message_id=event.message_id - 1
    )
    # Удаляем сообщение перед ответом
    await event.delete()
    await event.answer(
        f"👌🏼Тариф успешно удален ❌", reply_markup=await kb.owner_main()
    )


@owner_tariff_management.callback_query(F.data == "add_tariff")
async def add_tariff(callback: CallbackQuery, state: FSMContext):
    # await callback.answer("Функция в разработке", show_alert=True)
    await callback.message.edit_text("Введите название тарифа: ")
    await state.set_state(TariffManagement.add_tariff_name)


@owner_tariff_management.message(TariffManagement.add_tariff_name)
async def add_tariff_name(message: Message, state: FSMContext):
    tariff_name = message.text
    await state.update_data(tariff_name=tariff_name)
    await message.answer("Введите service_id тарифа: ")
    await state.set_state(TariffManagement.add_tariff_service_id)


@owner_tariff_management.message(TariffManagement.add_tariff_service_id)
async def add_tariff_name(message: Message, state: FSMContext):
    tariff_service_id = int(message.text)
    await state.update_data(tariff_service_id=tariff_service_id)
    await message.answer("Введите описание тарифа: ")
    await state.set_state(TariffManagement.add_tariff_description)


@owner_tariff_management.message(TariffManagement.add_tariff_description)
async def add_tariff_description(message: Message, state: FSMContext):
    tariff_description = message.text
    await state.update_data(tariff_description=tariff_description)
    await message.answer("Введите цену тарифа: ")
    await state.set_state(TariffManagement.add_tariff_price)


@owner_tariff_management.message(TariffManagement.add_tariff_price)
async def set_tariff_price(message: Message, state: FSMContext):
    try:
        tariff_price = int(message.text)
    except ValueError:
        await message.answer("‼️ Введите целое число: ")
        return
    await state.update_data(tariff_price=tariff_price)
    data = await state.get_data()
    tariff_name = data.get("tariff_name")
    tariff_description = data.get("tariff_description")
    tariff_price = data.get("tariff_price")
    tariff_service_id = data.get("tariff_service_id")
    text = (
        f"Создан тариф: \n\n"
        f"Название: {tariff_name}\n"
        f"Описание: {tariff_description}\n"
        f"Цена: {tariff_price}\n"
    )
    await message.answer(text, reply_markup=await kb.save_changes("list_tariffs"))
    await state.set_state(TariffManagement.finish_add_tariff)


@owner_tariff_management.callback_query(
    F.data == "save_new_date", TariffManagement.finish_add_tariff
)
async def save_new_date(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    tariff_name = data.get("tariff_name")
    tariff_description = data.get("tariff_description")
    tariff_price = data.get("tariff_price")
    tariff_service_id = data.get("tariff_service_id")
    await create_or_update_tariff(
        name=tariff_name,
        description=tariff_description,
        price=tariff_price,
        service_id=tariff_service_id,
    )
    text = f"Тариф '{tariff_name}' успешно создан"
    await callback.message.edit_text(text, reply_markup=await kb.owner_main())
    await state.clear()
    await callback.answer()
