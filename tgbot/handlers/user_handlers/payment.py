# import asyncio
#
# from aiogram.fsm.context import FSMContext
# from aiogram.types import CallbackQuery
# from fluent.runtime import FluentLocalization
# from yookassa import Configuration, Payment
#
# from tgbot.config import LINK_BOT, YOKASSA_ACCOUNT_ID, YOKASSA_SECRET_KEY
#
# import tgbot.keyboards.user_kb.keyboards as kb
#
# Configuration.account_id = YOKASSA_ACCOUNT_ID
# Configuration.secret_key = YOKASSA_SECRET_KEY
#
#
# async def create_payment(description: str, amount: int, l10n: FluentLocalization):
#     payment = Payment.create(
#         {
#             "amount": {"value": amount, "currency": "RUB"},
#             "confirmation": {"type": "redirect", "return_url": LINK_BOT},
#             "capture": True,
#             "description": description,
#         }
#     )
#     # print("payment", payment.id)
#     return payment.id, payment.confirmation.confirmation_url
#
#
# async def cancel_payment_handler(
#     callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
# ):
#     await state.update_data(payment_status="cancelled")
#     await callback.answer("Платеж был отменен.", show_alert=True)
#
#     for i in range(5, 0, -1):
#         await asyncio.sleep(1)
#         await callback.message.edit_text(
#             f"Отмена платежа. Оставшееся время: {i} секунд."
#         )
#
#     await callback.message.edit_text(
#         "Платеж был отменен.", reply_markup=await kb.user_main(l10n=l10n)
#     )
#     await state.clear()
# import asyncio
import logging
from aiogram import Router

# from aiogram.fsm.context import FSMContext
# from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest

# from fluent.runtime import FluentLocalization
# from yookassa import Configuration, Payment

# from tgbot.utils.config import LINK_BOT, YOKASSA_ACCOUNT_ID, YOKASSA_SECRET_KEY
# import tgbot.keyboards.user_kb as kb
import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from fluent.runtime import FluentLocalization
from yookassa import Configuration, Payment

from tgbot.config import LINK_BOT, YOKASSA_ACCOUNT_ID, YOKASSA_SECRET_KEY

import tgbot.keyboards.user_kb.keyboards as kb

Configuration.account_id = YOKASSA_ACCOUNT_ID
Configuration.secret_key = YOKASSA_SECRET_KEY

logger = logging.getLogger(__name__)

Configuration.account_id = YOKASSA_ACCOUNT_ID
Configuration.secret_key = YOKASSA_SECRET_KEY

guest_router = Router()


async def create_payment(
    description: str, amount: int, l10n: FluentLocalization
) -> tuple[str, str]:
    """Создание платежа через YooKassa."""
    try:
        payment = Payment.create(
            {
                "amount": {"value": amount, "currency": "RUB"},
                "confirmation": {"type": "redirect", "return_url": LINK_BOT},
                "capture": True,
                "description": description,
            }
        )
        logger.debug(
            "Платёж создан: id=%s, url=%s",
            payment.id,
            payment.confirmation.confirmation_url,
        )
        return payment.id, payment.confirmation.confirmation_url
    except Exception as e:
        logger.error("Ошибка создания платежа: %s", str(e))
        raise


@guest_router.callback_query()
async def cancel_payment_handler(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
) -> None:
    """Обработка отмены платежа с обновлением сообщения и таймером."""
    data = await state.get_data()
    payment_id = data.get("payment_id")  # Предполагается, что payment_id сохранён ранее

    # Обновляем состояние
    await state.update_data(payment_status="cancelled")
    await callback.answer(l10n.format_value("payment_cancelled_alert"), show_alert=True)
    logger.debug("Начало отмены платежа для payment_id=%s", payment_id)

    # Реальная отмена платежа через YooKassa (если требуется)
    if payment_id:
        try:
            Payment.cancel(payment_id)
            logger.debug("Платёж %s успешно отменён в YooKassa", payment_id)
        except Exception as e:
            logger.error("Ошибка отмены платежа %s в YooKassa: %s", payment_id, str(e))

    # Таймер отмены (опционально)
    for i in range(3, 0, -1):  # Уменьшил до 3 секунд для меньшего раздражения
        try:
            await callback.message.edit_text(
                l10n.format_value("payment_cancelling", {"seconds": i})
            )
            await asyncio.sleep(1)
        except TelegramBadRequest as e:
            logger.warning(
                "Не удалось обновить сообщение в cancel_payment_handler: %s", str(e)
            )
            break

    # Финальное сообщение
    try:
        await callback.message.edit_text(
            l10n.format_value("payment_cancelled"),
            reply_markup=await kb.user_main(l10n=l10n),
        )
    except TelegramBadRequest as e:
        logger.error("Не удалось завершить отмену платежа: %s", str(e))
        await callback.message.answer(
            l10n.format_value("payment_cancelled"),
            reply_markup=await kb.user_main(l10n=l10n),
        )

    await state.clear()
    logger.debug("Отмена платежа завершена для payment_id=%s", payment_id)
