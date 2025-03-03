"""Точка входа для Telegram-бота PARTA.

Инициализирует бота, регистрирует маршрутизаторы и middleware,
запускает планировщик и начинает обработку сообщений.
"""

import asyncio
import signal

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from tgbot.config import BOT_TOKEN, DEFAULT_LOCALE
from tgbot.middlewares.localization import L10nMiddleware
from tgbot.middlewares.custom_logging import LoggingMiddleware, logger
from tgbot.scheduler import setup_scheduler
from tgbot.routers import ALL_ROUTERS


async def shutdown(
    signal_name: signal.Signals, dp: Dispatcher, scheduler, bot: Bot
) -> None:
    """Останавливает бота корректно при получении сигнала."""
    logger.info(f"Получен сигнал {signal_name}. Завершаем работу...")
    scheduler.shutdown()
    await bot.session.close()
    await dp.stop_polling()


async def main() -> None:
    """Основная функция запуска бота."""
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Middleware registration
    dp.update.middleware(LoggingMiddleware())
    dp.message.outer_middleware(L10nMiddleware(default_locale=DEFAULT_LOCALE))
    dp.callback_query.outer_middleware(L10nMiddleware(default_locale=DEFAULT_LOCALE))

    # Router registration
    dp.include_routers(*ALL_ROUTERS)
    # await inti_db_with_data()
    # Setup scheduler
    scheduler = setup_scheduler(bot)
    # Регистрация обработчиков сигналов
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(
            sig, lambda s=sig: asyncio.create_task(shutdown(s, dp, scheduler, bot))
        )

    try:
        logger.info("Бот запущен и работает...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при работе бота: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
