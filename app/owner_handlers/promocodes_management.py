from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

import app.calendar_keyboard.custom_calendar as cl

import app.owner_kb.keyboards as kb
import app.general_keyboards as gkb
from app.database.requests import (
    get_all_promocodes,
    get_promocode_by_id,
    update_promocode,
    delete_promocode,
    create_promocode,
)
from filters import IsOwnerFilter

owner_promo_management = Router()

# Применяем фильтр для всех хэндлеров на уровне роутера
owner_promo_management.message.filter(IsOwnerFilter(is_owner=True))
owner_promo_management.callback_query.filter(IsOwnerFilter(is_owner=True))


class PromoManagement(StatesGroup):
    # add_promo = State()
    add_name = State()
    add_discount = State()
    add_date = State()
    finish_add_promo = State()
    del_promo = State()
    edit_promo = State()
    select_changes = State()
    expiration_date = State()


@owner_promo_management.callback_query(F.data == "manage_promocodes")
async def manage_admin(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        text="💠 Выберите действие:", reply_markup=await kb.manage_promo()
    )
    await callback.answer()


@owner_promo_management.callback_query(F.data == "list_promocodes")
@owner_promo_management.callback_query(F.data.startswith("my_promo_page_"))
async def list_promocodes(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    page = 1  # Стартовая страница

    if callback.data.startswith("my_promo_page_"):
        page = int(callback.data.split("_")[-1])

    promocodes = await get_all_promocodes()
    await state.update_data(promocodes=promocodes)

    page_size = 4
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    current_page_promo = promocodes[start_index:end_index]

    if current_page_promo:
        text = f"<b>📨 Список всех промокодов (страница {page}):</b>\n\n"
        for i, promocode in enumerate(current_page_promo, 1):
            expiration_date = (
                promocode.expiration_date.strftime("%d.%m.%Y")
                if promocode.expiration_date
                else "Без срока"
            )
            text += (
                f"{i}. <code>{promocode.name}</code> - {promocode.discount}%\n"
                f" ├ <em>Использовано: </em>{promocode.usage_quantity} раз\n"
                f" ├ <em>Действительно до: </em>{expiration_date}\n"
                f" └ <em>Статус: </em>{'Активен' if promocode.is_active else 'Не активен'}\n\n"
            )
        keyboard = await kb.promocodes(
            "my_promo_page_",
            "manage_promocodes",
            page,
            len(promocodes),
            page_size,
            end_index,
        )
    else:
        text = "📨 Пу-пу-пу:\n\n" "Промокодов пока нет.. 🤷‍️"
        keyboard = await kb.owner_main()

    # Сравниваем текст и клавиатуру
    current_message = callback.message.text
    current_keyboard = callback.message.reply_markup

    # Проверяем, изменилось ли сообщение или клавиатура
    if (current_message != text) and (current_keyboard != keyboard):
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")

    await callback.answer()


@owner_promo_management.callback_query(F.data == "select_promo")
@owner_promo_management.callback_query(F.data == "delete_promo")
async def select_promo(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if callback.data == "select_promo":
        text = "Выберите промокод, который хотели бы изменить: "
        promocodes = data["promocodes"]
        await state.set_state(PromoManagement.edit_promo)
    if callback.data == "delete_promo":
        promocodes = await get_all_promocodes()
        text = "Выберите промокод, который хотели бы удалить: "
        await state.set_state(PromoManagement.del_promo)
    await callback.message.edit_text(
        text, reply_markup=await kb.list_promocodes(promocodes)
    )


@owner_promo_management.callback_query(
    F.data.startswith("promocode_"), PromoManagement.edit_promo
)
async def edit_promo(callback: CallbackQuery, state: FSMContext):
    promocode_id = int(callback.data.split("_")[1])
    promocode = await get_promocode_by_id(promocode_id)
    await state.update_data(
        promocode_id=promocode_id,
        promocode_name=promocode.name,
        is_active=promocode.is_active,
    )
    await state.set_state(PromoManagement.select_changes)
    await callback.message.edit_text(
        "Можно продлить или включить/отключить промокод\nВыберите действие:",
        reply_markup=await kb.promo_changes(promocode.is_active),
    )


@owner_promo_management.callback_query(F.data == "extend_promo")
async def extend_promo(callback: CallbackQuery, state: FSMContext):
    calendar = cl.CustomCalendar()
    await callback.message.edit_text(
        "Выберите дату:",
        reply_markup=await calendar.generate_calendar(
            datetime.now().year, datetime.now().month, "select_promo", locale="ru"
        ),
    )
    await state.set_state(PromoManagement.expiration_date)


@owner_promo_management.callback_query(
    F.data.startswith("calendar:"), PromoManagement.expiration_date
)
async def set_date(callback: CallbackQuery, state: FSMContext):
    # Получение выбранной даты
    calendar = cl.CustomCalendar()
    selected_date = await calendar.handle_callback(
        callback, "select_promo", locale="ru"
    )

    if selected_date:
        current_date = datetime.now()  # Текущая дата
        data = await state.get_data()  # Данные состояния
        promocode_id = data.get(
            "promocode_id"
        )  # ID промокода из состояния (добавьте это в ваш FSM)

        # Получение промокода из БД
        promocode = await get_promocode_by_id(promocode_id)

        if selected_date > current_date and (
            not promocode.expiration_date or selected_date > promocode.expiration_date
        ):
            # Обновляем состояние с новой выбранной датой
            await state.update_data(expiration_date=selected_date.strftime("%d.%m.%Y"))

            # Отправляем пользователю сообщение о подтверждении сохранения
            await callback.message.edit_text(
                f"Вы выбрали дату: {selected_date.strftime('%d.%m.%Y')}. Сохранить?",
                reply_markup=await kb.save_changes("list_promocodes"),
            )
            await state.set_state(PromoManagement.finish_add_promo)
        else:
            # Если выбранная дата не соответствует требованиям
            await callback.message.edit_text(
                "Выбранная дата должна быть больше текущей и больше даты окончания промокода.",
                reply_markup=await gkb.create_buttons(
                    back_callback_data="manage_promocodes"
                ),
            )
        await callback.answer()


@owner_promo_management.callback_query(
    F.data == "save_new_date", PromoManagement.finish_add_promo
)
async def save_new_date(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_date_str = data.get("expiration_date")  # Новая дата
    promocode_id = data.get("promocode_id")  # ID промокода
    # Преобразование строки даты обратно в объект datetime
    new_expiration_date = datetime.strptime(selected_date_str, "%d.%m.%Y")
    # Обновление даты в БД
    await update_promocode(promocode_id, new_date=new_expiration_date)
    await callback.message.edit_text(
        f"Дата промокода успешно обновлена на {new_expiration_date.strftime('%d.%m.%Y')}",
        reply_markup=await kb.owner_main(),
    )
    await state.clear()
    await callback.answer()


@owner_promo_management.callback_query(
    F.data.startswith("switch_"), PromoManagement.select_changes
)
async def switch_on_off_promo(callback: CallbackQuery, state: FSMContext):
    # "switch_off" if is_active else "switch_on"
    status = callback.data.split("_")[1]
    if status == "on":
        new_status = True
    else:
        new_status = False
    data = await state.get_data()
    promocode_id = data.get("promocode_id")
    promocode_name = data.get("promocode_name")
    await update_promocode(promocode_id, new_status=new_status)
    status_text = f"Статус промокода - {promocode_name} успешно изменен."
    # status_text = f"{"+" if new_status else "-"} Статус промокода - {promocode_name} успешно изменен на {"<b>Включен</b>" if new_status else "<b>Выключен</b>"}"
    await callback.message.edit_text(
        status_text,
        reply_markup=await kb.owner_main(),
    )
    await state.clear()
    await callback.answer()


@owner_promo_management.callback_query(
    F.data.startswith("promocode_"), PromoManagement.del_promo
)
async def delete_promo(callback: CallbackQuery, state: FSMContext):
    promocode_id = int(callback.data.split("_")[1])
    await delete_promocode(promocode_id)
    await callback.message.edit_text(
        f"👌🏼Промокод успешно удален ❌", reply_markup=await kb.owner_main()
    )
    await state.clear()
    await callback.answer()


@owner_promo_management.callback_query(F.data == "add_promo")
async def add_promo(callback: CallbackQuery, state: FSMContext):
    # await callback.answer("Функция в разработке", show_alert=True)
    await callback.message.edit_text("Введите название промокода: ")
    await state.set_state(PromoManagement.add_name)


@owner_promo_management.message(PromoManagement.add_name)
async def add_name(message: Message, state: FSMContext):
    promocode_name = message.text
    await state.update_data(promocode_name=promocode_name)
    await message.answer("Введите размер скидки: ")
    await state.set_state(PromoManagement.add_discount)


@owner_promo_management.message(PromoManagement.add_discount)
async def add_discount(message: Message, state: FSMContext):
    discount = message.text
    await state.update_data(discount=discount)
    calendar = cl.CustomCalendar()
    await message.answer(
        "Выберите дату окончания промокода: ",
        reply_markup=await calendar.generate_calendar(
            datetime.now().year, datetime.now().month, "manage_promocodes", locale="ru"
        ),
    )
    await state.set_state(PromoManagement.add_date)


@owner_promo_management.callback_query(
    F.data.startswith("calendar:"), PromoManagement.add_date
)
async def set_date(callback: CallbackQuery, state: FSMContext):
    calendar = cl.CustomCalendar()
    selected_date = await calendar.handle_callback(
        callback, "manage_promocodes", locale="ru"
    )
    if selected_date:
        await state.update_data(expiration_date=selected_date.strftime("%d.%m.%Y"))
        current_date = datetime.now()  # Текущая дата
        data = await state.get_data()
        promocode_name = data.get("promocode_name")
        discount = data.get("discount")
        expiration_date_str = data.get("expiration_date", None)
        if expiration_date_str:
            expiration_date = datetime.strptime(expiration_date_str, "%d.%m.%Y")
        if selected_date >= current_date:
            await create_promocode(
                name=promocode_name, discount=discount, expiration_date=expiration_date
            )
            await callback.message.edit_text(
                f"🪄 Промокод {promocode_name} успешно создан!",
                reply_markup=await kb.owner_main(),
            )
        else:
            # Если выбранная дата не соответствует требованиям
            await callback.message.edit_text(
                "Ошибка",
                reply_markup=await gkb.create_buttons(
                    back_callback_data="manage_promocodes"
                ),
            )
        await state.clear()
        await callback.answer()
