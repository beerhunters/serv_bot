import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from fluent.runtime import FluentLocalization
from yookassa import Configuration, Payment

from config import LINK_BOT, YOKASSA_ACCOUNT_ID, YOKASSA_SECRET_KEY

import app.user_kb.keyboards as kb

Configuration.account_id = YOKASSA_ACCOUNT_ID
Configuration.secret_key = YOKASSA_SECRET_KEY


async def create_payment(description: str, amount: int, l10n: FluentLocalization):
    payment = Payment.create(
        {
            "amount": {"value": amount, "currency": "RUB"},
            "confirmation": {"type": "redirect", "return_url": LINK_BOT},
            "capture": True,
            "description": description,
        }
    )
    # print("payment", payment.id)
    return payment.id, payment.confirmation.confirmation_url


async def cancel_payment_handler(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
):
    await state.update_data(payment_status="cancelled")
    await callback.answer("Платеж был отменен.", show_alert=True)

    for i in range(5, 0, -1):
        await asyncio.sleep(1)
        await callback.message.edit_text(
            f"Отмена платежа. Оставшееся время: {i} секунд."
        )

    await callback.message.edit_text(
        "Платеж был отменен.", reply_markup=await kb.user_main(l10n=l10n)
    )
    await state.clear()
