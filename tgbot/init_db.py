import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.database.db import async_session

from tgbot.database.models import (
    Adjustment,
    Tariff,
    Location,
)


async def populate_adjustments(session: AsyncSession) -> None:
    """Заполнение таблицы adjustments начальными данными."""
    default_adjustments = [
        {"name": "printing_available", "state": True, "value": 15.0},
        {"name": "free_printing_available", "state": False, "value": None},
        {"name": "scanning_available", "state": False, "value": None},
        {"name": "quiz_available", "state": True, "value": None},
    ]
    existing_names = {
        row[0] for row in (await session.execute(select(Adjustment.name))).all()
    }
    for adj_data in default_adjustments:
        if adj_data["name"] not in existing_names:
            adjustment = Adjustment(
                name=adj_data["name"], state=adj_data["state"], value=adj_data["value"]
            )
            session.add(adjustment)
    try:
        await session.commit()
        logging.info("Таблица adjustments успешно заполнена начальными данными.")
    except Exception as e:
        await session.rollback()
        logging.error(f"Ошибка при заполнении таблицы adjustments: {e}")
        raise


async def populate_tariffs(session: AsyncSession) -> None:
    """Заполнение таблицы tariffs начальными данными."""
    default_tariffs = [
        {
            "id": 1,
            "name": "Полный день",
            "description": "Описание",
            "price": 1200,
            "purpose": "Опенспейс",
            "service_id": 49414,
            "is_active": True,
        },
        {
            "id": 2,
            "name": "Тестовый день",
            "description": "Описание",
            "price": 600,
            "purpose": "Опенспейс",
            "service_id": 47890,
            "is_active": True,
        },
        {
            "id": 3,
            "name": "Большая переговорная",
            "description": "Описание",
            "price": 3000,
            "purpose": "Переговорная",
            "service_id": 47900,
            "is_active": True,
        },
        {
            "id": 4,
            "name": "Амфитеатр",
            "description": "Описание",
            "price": 2500,
            "purpose": "Переговорная",
            "service_id": 50764,
            "is_active": True,
        },
        {
            "id": 5,
            "name": "Малая переговорная",
            "description": "Описание",
            "price": 2500,
            "purpose": "Переговорная",
            "service_id": 47901,
            "is_active": False,
        },
        {
            "id": 6,
            "name": "Опенспейс на месяц",
            "description": "Аренда опенспейса на месяц",
            "price": 15000,
            "purpose": "Опенспейс",
            "service_id": 47892,
            "is_active": True,
        },
        {
            "id": 7,
            "name": "Не бронировать - тест",
            "description": "Не бронировать - тест",
            "price": 1,
            "purpose": "Опенспейс",
            "service_id": 47892,
            "is_active": True,
        },
    ]
    existing_ids = {row[0] for row in (await session.execute(select(Tariff.id))).all()}
    for tariff_data in default_tariffs:
        if tariff_data["id"] not in existing_ids:
            tariff = Tariff(
                id=tariff_data["id"],
                name=tariff_data["name"],
                description=tariff_data["description"],
                price=tariff_data["price"],
                purpose=tariff_data["purpose"],
                service_id=tariff_data["service_id"],
                is_active=tariff_data["is_active"],
            )
            session.add(tariff)
    try:
        await session.commit()
        logging.info("Таблица tariffs успешно заполнена начальными данными.")
    except Exception as e:
        await session.rollback()
        logging.error(f"Ошибка при заполнении таблицы tariffs: {e}")
        raise


async def populate_locations(session: AsyncSession) -> None:
    """Заполнение таблицы locations начальными данными."""
    default_locations = [
        {"id": 1, "name": "Коворкинг PARTA"},
    ]
    existing_ids = {
        row[0] for row in (await session.execute(select(Location.id))).all()
    }
    for loc_data in default_locations:
        if loc_data["id"] not in existing_ids:
            location = Location(id=loc_data["id"], name=loc_data["name"])
            session.add(location)
    try:
        await session.commit()
        logging.info("Таблица locations успешно заполнена начальными данными.")
    except Exception as e:
        await session.rollback()
        logging.error(f"Ошибка при заполнении таблицы locations: {e}")
        raise


async def inti_db_with_data():
    """Инициализация базы начальными данными."""
    async with async_session() as session:
        await populate_adjustments(session)
        await populate_tariffs(session)
        await populate_locations(session)  # Добавляем заполнение локаций
