# tools/time_utils.py
import datetime
from datetime import timezone, timedelta

# Часовой пояс UTC+3 (Москва)
MOSCOW_TZ = timezone(timedelta(hours=3))


def get_moscow_time() -> datetime.datetime:
    """Возвращает текущее время в московском часовом поясе (UTC+3)."""
    return datetime.datetime.now(MOSCOW_TZ).replace(microsecond=0)


def ensure_moscow_tz(dt: datetime.datetime) -> datetime.datetime:
    """Приводит объект datetime к московскому часовому поясу, если он offset-naive."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=MOSCOW_TZ)
    return dt.astimezone(MOSCOW_TZ)  # Переводим в UTC+3, если часовой пояс отличается
