import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from tgbot.database.requests import get_unclosed_tickets_count
from tgbot.config import BOT_ADMINS
from aiogram import Bot
import tgbot.keyboards.admin_kb.keyboards as kb


async def send_message_to_admin(bot: Bot, admin_id: int, message_text: str):
    """
    Отправляет сообщение администратору.
    """
    try:
        await bot.send_message(
            admin_id, message_text, reply_markup=await kb.tickets_menu()
        )
    except Exception as e:
        logging.error(f"Не удалось отправить сообщение администратору {admin_id}: {e}")


async def notify_admins_about_unclosed_tickets(bot: Bot):
    unclosed_tickets_count = await get_unclosed_tickets_count()
    # Формируем текст сообщения
    message_text = (
        f"‼️ Количество незакрытых заявок: {unclosed_tickets_count} шт 💢\n"
        "Пожалуйста, проверьте и закройте их по возможности."
    )
    if unclosed_tickets_count > 0:
        # Отправляем уведомления всем администраторам
        for admin in BOT_ADMINS:
            await send_message_to_admin(bot, admin, message_text)


# Функция для настройки и запуска планировщика
def setup_scheduler(bot):
    scheduler = AsyncIOScheduler()

    # Настройка задач на конкретное время
    scheduler.add_job(
        notify_admins_about_unclosed_tickets, "cron", hour=9, minute=0, args=[bot]
    )
    scheduler.add_job(
        notify_admins_about_unclosed_tickets, "cron", hour=18, minute=0, args=[bot]
    )

    # Запуск планировщика
    scheduler.start()
    return scheduler
