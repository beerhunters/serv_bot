import asyncio
import os

from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message, FSInputFile
from fluent.runtime import FluentLocalization

import app.owner_kb.keyboards as kb
import app.general_keyboards as gkb
from app.admin_handlers.save_xlsx import save_report_to_excel
from app.database.models import QuizResult
from app.database.requests import (
    get_adjustments,
    update_adjustment,
    add_quizzes_from_file,
    get_all_quiz_results,
)
from filters import IsOwnerFilter

owner_quizzes_management = Router()

# Применяем фильтр для всех хэндлеров на уровне роутера
owner_quizzes_management.message.filter(IsOwnerFilter(is_owner=True))
owner_quizzes_management.callback_query.filter(IsOwnerFilter(is_owner=True))


class QuizManagement(StatesGroup):
    upload_quiz = State()


@owner_quizzes_management.callback_query(F.data == "manage_quizzes")
async def manage_quizzes(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    await state.clear()
    adjustments = await get_adjustments()
    quiz_available = adjustments["quiz_available"]
    await state.update_data(quiz_available=quiz_available)
    await callback.message.edit_text(
        text="💠 Выберите действие:",
        reply_markup=await kb.manage_quizzes(quiz_available, l10n=l10n),
    )
    await callback.answer()


@owner_quizzes_management.callback_query(F.data.startswith("quiz_toggle_"))
async def toggle_feature(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    data = await state.get_data()
    feature_map = {"quiz_toggle_free": "quiz_available"}
    feature_key = feature_map.get(callback.data)
    if not feature_key:
        await callback.answer(
            "Ошибка: не удалось определить действие.", show_alert=True
        )
        return
    feature_info = data.get(feature_key)
    if feature_info is None:
        await callback.answer("Ошибка: нет данных по функции.", show_alert=True)
        return
    new_state = not feature_info["state"]
    await update_adjustment(name=feature_key, state=new_state)
    if feature_key == "quiz_available":
        status_message = (
            f"{'🟢 Квиз включен! 🟢' if new_state else '🔴 Квиз выключен! 🔴'}"
        )
    await callback.message.edit_text(
        f"{status_message}\n",
        reply_markup=await gkb.create_buttons(
            back_callback_data="manage_quizzes", l10n=l10n
        ),
    )
    await callback.answer()


@owner_quizzes_management.callback_query(F.data == "upload_quiz")
async def upload_quiz(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    await callback.message.edit_text("Отправьте файл с данными квиза в формате .txt.")
    await state.set_state(QuizManagement.upload_quiz)
    await callback.answer()


@owner_quizzes_management.message(
    F.content_type == ContentType.DOCUMENT, QuizManagement.upload_quiz
)
async def handle_quiz_file(
    message: Message, state: FSMContext, l10n: FluentLocalization
):
    if message.document:
        if message.document.file_name != "quiz_data.txt":
            await message.answer(
                "Файл должен иметь название 'quiz_data.txt'. Пожалуйста, отправьте правильный файл."
            )
            return

        file_id = message.document.file_id
        file_info = await message.bot.get_file(file_id)
        file_path = file_info.file_path

        # Скачиваем файл
        file = await message.bot.download_file(file_path)

        # Сохраняем файл на диск
        with open("docs/quiz_data.txt", "wb") as f:
            f.write(file.read())

        # await message.answer("Квиз обновлен.", reply_markup=await kb.owner_main())
        text = await add_quizzes_from_file("docs/quiz_data.txt")
        await add_quizzes_from_file("docs/quiz_data.txt")
        await message.answer(text, reply_markup=await kb.owner_main(l10n=l10n))
        await state.clear()
    else:
        await message.answer("Пожалуйста, отправьте файл с данными квиза.")


@owner_quizzes_management.callback_query(F.data == "quiz_results_for_display")
async def quiz_results_for_display(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    await generate_report(
        callback,
        state,
        "quiz_results_for_display",
        QuizResult,
        "Результаты квизов",
        get_all_quiz_results,
        l10n=l10n,
    )


async def generate_report(
    callback: CallbackQuery,
    state: FSMContext,
    report_type: str,
    model,
    list_name: str,
    get_data_func,
    l10n: FluentLocalization,
):
    report_list = await get_data_func()

    if report_list:
        await callback.message.delete()

        # Сохраняем отчет в Excel файл
        file_path = await save_report_to_excel(model, list_name, report_list)

        # Отправляем файл в чат
        document = FSInputFile(file_path)
        await callback.message.answer_document(document)

        # Удаляем файл после отправки
        if os.path.exists(file_path):
            os.remove(file_path)

        await asyncio.sleep(1)

        text = "🔝                          🔝                          🔝\n✅ Результаты квизов:"
        await callback.message.answer(text, reply_markup=await kb.owner_main(l10n=l10n))
    else:
        await callback.message.edit_text(
            f"Ничего не найдено\nПопробуйте в другой раз",
            reply_markup=await kb.owner_main(l10n=l10n),
        )

    await state.clear()
