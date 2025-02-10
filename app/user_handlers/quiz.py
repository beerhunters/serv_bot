from datetime import datetime

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery
from fluent.runtime import FluentLocalization

import app.user_kb.keyboards as kb
from app.database.requests import (
    get_all_quizzes,
    get_questions_for_quiz,
    record_quiz_result,
    get_adjustments,
)
from filters import IsUserFilter

quiz_router = Router()

# Применяем фильтр для всех хэндлеров на уровне роутера
quiz_router.message.filter(IsUserFilter(is_user=True))
quiz_router.callback_query.filter(IsUserFilter(is_user=True))


class QuizStates(StatesGroup):
    selecting_quiz = State()
    answering_questions = State()


@quiz_router.callback_query(F.data == "start_quiz")
async def start_quiz(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    adjustments = await get_adjustments()
    quiz_info = adjustments.get("quiz_available")

    if not quiz_info["state"]:
        await callback.answer("Квиз сейчас недоступен.", show_alert=True)
        return

    quizzes = await get_all_quizzes()
    if not quizzes:
        try:
            await callback.message.answer(
                "В данный момент нет доступных квизов.",
                reply_markup=await kb.user_main(l10n=l10n),
            )
        except TelegramBadRequest as e:
            if str(e) != "Bad Request: message to delete not found":
                raise e
        return

    try:
        await callback.message.edit_text(
            "Выберите квиз из списка:",
            reply_markup=await kb.quiz_list(quizzes, l10n=l10n),
        )
    except TelegramBadRequest as e:
        if str(e) != "Bad Request: message to delete not found":
            raise e
    await state.set_state(QuizStates.selecting_quiz)


# Обработчик выбора квиза
@quiz_router.callback_query(QuizStates.selecting_quiz, F.data.startswith("quiz_"))
async def quiz_selected(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    quiz_id = callback.data.split("_")[
        1
    ]  # Ожидаем, что data будет вида 'quiz_<quiz_id>'
    quizzes = await get_all_quizzes()
    quiz = next((q for q in quizzes if str(q["id"]) == quiz_id), None)

    if not quiz:
        await callback.message.answer(
            "Квиз не найден, попробуйте выбрать другой.",
            reply_markup=await kb.quiz_list(quizzes, l10n=l10n),
        )
        return
    # Удаляем предыдущее сообщение, которое содержало выбор квиза
    last_message_id = callback.message.message_id
    await state.update_data(last_message_id=last_message_id)
    # Сохраняем данные и начинаем квиз
    await state.update_data(quiz_id=quiz["id"], score=0, current_question_index=0)
    await ask_question(callback, state)
    await state.set_state(QuizStates.answering_questions)


async def ask_question(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    data = await state.get_data()
    quiz_id = data["quiz_id"]
    current_question_index = data["current_question_index"]
    last_message_id = data.get("last_message_id")

    questions = await get_questions_for_quiz(quiz_id)

    if current_question_index >= len(questions):
        await finish_quiz(callback, state)
        return

    question = questions[current_question_index]

    await state.update_data(current_question_id=question["id"])

    # Удаляем предыдущее сообщение, если оно существует
    if last_message_id:
        try:
            await callback.message.chat.delete_message(last_message_id)
        except TelegramBadRequest as e:
            if str(e) != "Bad Request: message to delete not found":
                raise e

    if question["photo_url"]:
        # Отправляем новое сообщение с фото и сохраняем его ID
        message = await callback.message.answer_photo(
            photo=question["photo_url"],
            caption=question["question_text"],
            reply_markup=await kb.question(
                question["id"], question["answer_options"], l10n=l10n
            ),
        )
        await state.update_data(last_message_id=message.message_id)
    else:
        # Отправляем текстовое сообщение и сохраняем его ID
        message = await callback.message.answer(
            text=question["question_text"],
            reply_markup=await kb.question(
                question["id"], question["answer_options"], l10n=l10n
            ),
        )
        await state.update_data(last_message_id=message.message_id)


# Обработчик ответов на вопросы
@quiz_router.callback_query(
    QuizStates.answering_questions, F.data.startswith("answer_")
)
async def handle_answer(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    data = await state.get_data()
    quiz_id = data["quiz_id"]
    current_question_index = data["current_question_index"]

    # Получаем вопросы из состояния, чтобы избежать повторных запросов
    questions = data.get("questions")
    if not questions:
        questions = await get_questions_for_quiz(quiz_id)
        await state.update_data(questions=questions)

    question = questions[current_question_index]

    selected_answer_index = int(callback.data.split("_")[2]) - 1
    selected_answer_text = (
        question["answer_options"][selected_answer_index].strip().lower()
    )
    correct_answer_text = question["correct_answer"].strip().lower()

    if selected_answer_text == correct_answer_text:
        score = data["score"] + 1
        await state.update_data(score=score)

    await state.update_data(current_question_index=current_question_index + 1)
    await ask_question(callback, state, l10n=l10n)


async def finish_quiz(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    data = await state.get_data()
    quiz_id = data["quiz_id"]
    score = data["score"]
    user_id = callback.from_user.id
    last_message_id = data.get("last_message_id")

    completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await record_quiz_result(
        user_id=user_id, quiz_id=quiz_id, score=score, completed_at=completed_at
    )

    # Если последнее сообщение было с фото, удаляем его
    if last_message_id:
        try:
            await callback.message.chat.delete_message(last_message_id)
        except TelegramBadRequest as e:
            if str(e) == "Bad Request: message to delete not found":
                pass
            else:
                raise e

    # Отправляем финальное текстовое сообщение
    await callback.message.answer(
        f"Квиз завершен! Ваш результат: {score} из {len(await get_questions_for_quiz(quiz_id))}.",
        reply_markup=await kb.user_main(l10n=l10n),
    )

    await state.clear()
