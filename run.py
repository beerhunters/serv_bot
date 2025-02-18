import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.admin_handlers.admin_meeting_room import admin_meeting_router
from app.admin_handlers.admin_report import admin_report_router
from app.admin_handlers.admin_ticket import admin_ticket_router
from app.admin_handlers.admins_users import admin_users_router
from app.owner_handlers.admins_management import owner_admin_management
from app.owner_handlers.locations_management import owner_locations_management
from app.owner_handlers.booking_mr_management import owner_booking_mr_management
from app.owner_handlers.printing_management import owner_print_management
from app.owner_handlers.promocodes_management import owner_promo_management

# from app.owner_handlers.quizzes_management import owner_quizzes_management
from app.owner_handlers.tariffs_management import owner_tariff_management
from app.owner_handlers.users_management import owner_users_management
from app.user_handlers.booking import booking_router
from app.user_handlers.booking_meeting_room import meeting_room_router

# from app.database.models import async_main
from app.admin_handlers.admin import admin_router
from app.exception_handlers.exceptions import error_router
from app.user_handlers.guests import guest_router
from app.owner_handlers.owner import owner_router
from app.user_handlers.printing import printer_router

# from app.user_handlers.quiz import quiz_router
from app.user_handlers.ticket import ticket_router
from app.user_handlers.user import user_router

from config import BOT_TOKEN
from middlewares.localization import L10nMiddleware

from middlewares.user_logging import LoggingMiddleware, logger
from scheduler import setup_scheduler

logging.basicConfig(level=logging.INFO)


async def main():
    # await async_main()
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    # Middleware registration
    dp.update.middleware(LoggingMiddleware())
    dp.message.outer_middleware(L10nMiddleware(default_locale="ru"))
    dp.callback_query.outer_middleware(L10nMiddleware(default_locale="ru"))
    # Router registration
    dp.include_routers(
        error_router,
        owner_router,
        owner_admin_management,
        owner_users_management,
        owner_promo_management,
        owner_print_management,
        owner_tariff_management,
        owner_booking_mr_management,
        owner_locations_management,
        # owner_quizzes_management,
        admin_router,
        admin_ticket_router,
        admin_report_router,
        admin_meeting_router,
        admin_users_router,
        user_router,
        ticket_router,
        booking_router,
        guest_router,
        meeting_room_router,
        printer_router,
        # quiz_router,
    )

    # Запуск асинхронного планировщика
    scheduler = setup_scheduler(bot)

    # Starting the bot
    try:
        logger.info("Бот запущен и работает...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при работе бота: {e}")
    finally:
        scheduler.shutdown()  # Останавливаем планировщик перед завершением работы бота
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
