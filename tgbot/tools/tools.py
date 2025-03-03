from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
    CallbackQuery,
)
from fluent.runtime import FluentLocalization


async def send_localized_message(
    message_or_callback: Message | CallbackQuery,
    l10n: FluentLocalization,
    text_key: str,
    reply_markup=ReplyKeyboardRemove(),
    show_alert: bool = False,
    prefix: str = "",  # Новый параметр для текста в начале сообщения
    postfix: str = "",  # Новый параметр для текста в начале сообщения
):
    """
    Utility function to send a localized message with an optional prefix.
    Can handle both Message and CallbackQuery.
    """
    # Формируем локализованный текст
    localized_text = l10n.format_value(text_key)
    # if prefix or postfix != '':
    full_message = f"{prefix}\n\n{localized_text}\n\n{postfix}"

    # Проверяем тип входящего объекта
    if isinstance(message_or_callback, CallbackQuery):
        if show_alert is not True:
            # Ответ на CallbackQuery
            await message_or_callback.message.answer(
                full_message,
                reply_markup=reply_markup,
                # show_alert=show_alert,
                # parse_mode="HTML",
            )
        else:
            # Ответ на CallbackQuery
            await message_or_callback.answer(
                full_message,
                reply_markup=reply_markup,
                show_alert=show_alert,
            )
        # Закрываем всплывающее уведомление
        await message_or_callback.answer()
    elif isinstance(message_or_callback, Message):
        # Ответ на Message
        await message_or_callback.answer(full_message, reply_markup=reply_markup)
