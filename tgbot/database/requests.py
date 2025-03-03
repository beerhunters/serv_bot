import os
import re
from datetime import datetime

from sqlalchemy.orm import joinedload, selectinload

from tgbot.database.db import async_session
from tgbot.database.models import (
    User,
    Location,
    Ticket,
    Adjustment,
    Tariff,
    Promocode,
    Booking,
    Guest,
    Admin,
)
from sqlalchemy import select, update, func, delete, or_, and_

from tgbot.config import BOT_ADMINS


def connection(some_func):
    async def wrapper(*args, **kwargs):
        async with async_session() as session:
            return await some_func(session, *args, **kwargs)

    return wrapper


# Функция для создания или обновления пользователя
@connection
async def create_or_update_user(
    session, tg_id, tg_username=None, name=None, contact=None, email=None
):
    # Проверяем, существует ли уже пользователь с таким tg_id
    user = await session.scalar(select(User).where(User.tg_id == tg_id))

    if user:
        # Если пользователь существует, обновляем его данные
        await session.execute(
            update(User)
            .where(User.tg_id == tg_id)
            .values(
                tg_username=tg_username or user.tg_username,
                name=name or user.name,
                contact=contact or user.contact,
                email=email or user.email,
            )
        )
        await session.commit()  # Коммитим обновление пользователя
        return user  # Возвращаем обновленного пользователя
    else:
        # Если пользователь не существует, создаем новую запись
        new_user = User(
            tg_id=tg_id,
            tg_username=tg_username,
            name=name,
            contact=contact,
            email=email,
        )
        session.add(new_user)
        await session.commit()  # Коммитим добавление нового пользователя
        return new_user  # Возвращаем нового пользователя


@connection
async def increment_user_successful_bookings(session, tg_id):
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    if user:
        user.successful_bookings += 1
        await session.commit()


@connection
async def get_user_by_tg_id(session, tg_id):
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    return user


@connection
async def get_user_by_id(session, user_id):
    user = await session.scalar(select(User).where(User.id == user_id))
    return user


@connection
async def get_new_visitors_for_period(session, first_day: str, last_day: str):
    # Преобразуем строки в объекты datetime
    first_date = datetime.strptime(first_day, "%d.%m.%Y")
    last_date = datetime.strptime(last_day, "%d.%m.%Y")

    # Убедитесь, что last_date включает конец дня
    last_date = last_date.replace(hour=23, minute=59, second=59)

    # Запрос всех пользователей, где дата регистрации между first_date и last_date
    query = select(User).where(User.reg_date.between(first_date, last_date))

    result = await session.execute(query)
    new_visitors = result.scalars().all()

    return new_visitors


@connection
async def get_all_users(session):
    result = await session.execute(select(User))
    return result.scalars().all()


@connection
async def update_language_code(session):
    # Получаем всех пользователей
    result = await session.execute(select(User))
    users = result.scalars().all()  # Извлекаем список пользователей

    # Проходим по всем пользователям и обновляем поле language_code
    for user in users:
        user.language_code = "ru"  # Пример: устанавливаем язык на русский

    # Проводим сессии и коммитим изменения
    await session.commit()

    print(f"Language code updated for {len(users)} users.")


@connection
async def delete_user_from_db(session, user_id):
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalars().first()
    if user:
        await session.execute(delete(User).where(User.id == user_id))
        await session.commit()
        return True  # Успешное удаление
    else:
        return False


@connection
async def search_users_by_name(session, search_query: str):
    result = await session.execute(
        select(User).where(User.name.ilike(f"%{search_query}%"))
    )
    return result.scalars().all()


# @connection
# async def search_users_by_name(session, query: str):
#     result = await session.execute(
#         select(User)
#         .where(func.lower(User.name).contains(query))
#     )
#     return result.scalars().all()
@connection
async def search_users_by_phone(session, phone_number: str):
    result = await session.execute(
        select(User).where(
            User.contact.contains(phone_number)
        )  # Поиск номера телефона по частичному совпадению
    )
    return result.scalars().all()


@connection
async def update_user_fields(session, user_id, **kwargs):
    await session.execute(update(User).where(User.id == user_id).values(**kwargs))
    await session.commit()


# @connection
# async def get_all_locations(session):
#     return await session.scalars(select(Location))
@connection
async def get_all_locations(session):
    result = await session.execute(select(Location))
    return result.scalars().all()


@connection
async def get_location_by_id(session, location_id):
    location = await session.scalar(select(Location).where(Location.id == location_id))
    return location


@connection
async def create_location(session, name):
    new_location = Location(name=name)
    session.add(new_location)
    await session.commit()
    return new_location


@connection
async def delete_location(session, location_id):
    stmt = select(Location).where(Location.id == location_id)
    result = await session.execute(stmt)
    location = result.scalars().first()
    if location:
        await session.execute(delete(Location).where(Location.id == location_id))
        await session.commit()
        return True  # Успешное удаление
    else:
        return False


@connection
async def create_ticket(session, reg_time, tg_id, description, location_id, photo_id):
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    location = await session.scalar(select(Location).where(Location.id == location_id))

    if tg_id is None or location is None:
        raise ValueError("User or location not found.")

    new_ticket = Ticket(
        reg_time=reg_time,
        user=user,  # Передаем объект User
        description=description,
        location=location,  # Передаем объект Location
        photo_id=photo_id,
    )
    session.add(new_ticket)
    await session.commit()
    return new_ticket


@connection
async def update_ticket_fields(session, ticket_id, tg_id=None, **kwargs):
    # Если передан tg_id администратора, то нужно найти его id
    if tg_id:
        admin = await session.execute(select(Admin).where(Admin.tg_id == tg_id))
        admin = admin.scalar()
        if admin:
            kwargs["admin_id"] = admin.id  # Передаем id администратора

    # Обновляем тикет с новыми данными
    await session.execute(update(Ticket).where(Ticket.id == ticket_id).values(**kwargs))
    await session.commit()


# @connection
# async def get_all_tickets(session, tg_id):
#     # Проверяем, является ли tg_id идентификатором администратора
#     admin = await session.scalar(select(Admin).where(Admin.tg_id == tg_id))
#
#     if admin:  # Если администратор найден
#         # Возвращаем все тикеты
#         tickets = await session.scalars(
#             select(Ticket).options(
#                 selectinload(Ticket.admin)
#             )  # Примените options к запросу
#         )
#     else:  # Если это не администратор
#         # Возвращаем тикеты конкретного пользователя
#         tickets = await session.scalars(
#             select(Ticket).where(Ticket.user.has(tg_id=tg_id))
#         )
#
#     return tickets.all()
@connection
async def get_all_tickets(session, tg_id):
    # Проверяем, является ли tg_id идентификатором администратора
    admin = await session.scalar(select(Admin).where(Admin.tg_id == tg_id))

    if admin:  # Если администратор найден
        # Возвращаем все тикеты с подгруженными пользователем и администратором
        tickets = await session.scalars(
            select(Ticket).options(
                selectinload(Ticket.user),  # Загрузка информации о пользователе
                selectinload(Ticket.admin),  # Загрузка информации об администраторе
            )
        )
    else:  # Если это не администратор
        # Возвращаем тикеты конкретного пользователя с подгруженным администратором
        tickets = await session.scalars(
            select(Ticket)
            .where(Ticket.user.has(tg_id=tg_id))
            .options(
                selectinload(Ticket.user),  # Загрузка информации о пользователе
                selectinload(Ticket.admin),  # Загрузка информации об администраторе
            )
        )

    return tickets.all()


@connection
async def get_open_tickets(session):
    result = await session.execute(select(Ticket).where(Ticket.state.is_(False)))
    return result.scalars().all()


@connection
async def get_tickets_by_admin(session, admin_id):
    result = await session.execute(
        select(Ticket).where(Ticket.admin_id == admin_id).where(Ticket.state.is_(False))
    )
    return result.scalars().all()


@connection
async def get_completed_tickets_count_by_admin(session, admin_id):
    result = await session.execute(
        select(func.count(Ticket.id))
        .where(Ticket.admin_id == admin_id)
        .where(Ticket.state.is_(True))
    )
    return result.scalar()


@connection
async def get_ticket_by_id(session, ticket_id):
    ticket = await session.scalar(
        select(Ticket)
        .where(Ticket.id == ticket_id)
        .options(
            joinedload(Ticket.user),  # Жадная загрузка пользователя
            joinedload(Ticket.location),  # Жадная загрузка локации
        )
    )
    return ticket


@connection
async def get_tickets_with_photos(session):
    tickets = await session.scalars(
        select(Ticket)
        .where(Ticket.photo_id.isnot(None))
        .options(selectinload(Ticket.user))
    )
    return tickets.all()


@connection
async def get_tickets_for_period(session, first_day: str, last_day: str):
    """
    Получает все тикеты за указанный период.
    """
    # Преобразуем строки дат в объекты datetime
    first_date = datetime.strptime(first_day, "%d.%m.%Y").date()
    last_date = datetime.strptime(last_day, "%d.%m.%Y").date()

    # Запрос всех тикетов, где дата тикета между first_date и last_date
    query = (
        select(Ticket)
        .where(Ticket.reg_time.between(first_date, last_date))
        .options(selectinload(Ticket.user), selectinload(Ticket.admin))
    )

    result = await session.execute(query)
    tickets = result.scalars().all()

    return tickets


@connection
async def get_unclosed_tickets_count(session) -> int:
    """
    Получает количество незакрытых заявок.
    """
    # Запрос для подсчета незакрытых тикетов (state == False)
    query = select(Ticket).where(Ticket.state.is_(False))
    result = await session.execute(query)
    unclosed_tickets = result.scalars().all()
    return len(unclosed_tickets)


@connection
async def get_all_tariffs(session):
    result = await session.execute(select(Tariff).where(Tariff.is_active.is_(True)))
    return result.scalars().all()


@connection
async def get_tariff_by_id(session, tariff_id):
    tariff = await session.scalar(select(Tariff).where(Tariff.id == tariff_id))
    return tariff


@connection
async def create_or_update_tariff(session, name, **kwargs):
    tariff = await session.scalar(select(Tariff).where(Tariff.name == name))

    if tariff:
        await session.execute(
            update(Tariff).where(Tariff.name == name).values(**kwargs)
        )
        await session.commit()
        return tariff
    else:
        # Извлекаем параметры из kwargs или задаем им значения по умолчанию
        description = kwargs.get("description", "Описание тарифа")
        price = kwargs.get("price", 0)
        purpose = kwargs.get("purpose", "Тип тарифа")
        service_id = int(kwargs.get("service_id", "ID услуги"))
        is_active = kwargs.get("is_active", True)

        # Создаем новый тариф
        new_tariff = Tariff(
            name=name,
            description=description,
            price=price,
            purpose=purpose,
            service_id=service_id,
            is_active=is_active,
        )
        session.add(new_tariff)
        await session.commit()
        return new_tariff


@connection
async def delete_tariff(session, tariff_id):
    stmt = select(Tariff).where(Tariff.id == tariff_id)
    result = await session.execute(stmt)
    tariff = result.scalars().first()
    if tariff:
        await session.execute(delete(Tariff).where(Tariff.id == tariff_id))
        await session.commit()
        return True  # Успешное удаление
    else:
        return False


@connection
async def get_all_promocodes(session):
    result = await session.execute(select(Promocode))
    return result.scalars().all()


@connection
async def get_promocode_by_id(session, promocode_id):
    result = await session.execute(
        select(Promocode).where(Promocode.id == promocode_id)
    )
    return result.scalar_one_or_none()


@connection
async def create_promocode(
    session, name, discount, expiration_date: datetime = None, is_active: bool = True
):
    # Проверка на уникальность имени промокода (по желанию)
    result = await session.execute(select(Promocode).where(Promocode.name == name))
    existing_promocode = result.scalars().first()

    if existing_promocode:
        raise ValueError(f"Промокод с именем '{name}' уже существует.")

    # Создание нового промокода
    new_promocode = Promocode(
        name=name,
        discount=discount,
        expiration_date=expiration_date,
        is_active=is_active,
    )
    session.add(new_promocode)
    await session.commit()
    return new_promocode


@connection
async def update_promocode(session, promocode_id, new_date=None, new_status=None):
    # Создаем базовый запрос для обновления промокода
    update_values = {}

    # Если передана новая дата, добавляем её в запрос
    if new_date is not None:
        update_values["expiration_date"] = new_date

    # Если передан новый статус, добавляем его в запрос
    if new_status is not None:
        update_values["is_active"] = new_status

    # Если есть что обновлять, выполняем запрос
    if update_values:
        result = await session.execute(
            update(Promocode)
            .where(Promocode.id == promocode_id)
            .values(**update_values)
        )
        await session.commit()


@connection
async def delete_promocode(session, promocode_id):
    stmt = select(Promocode).where(Promocode.id == promocode_id)
    result = await session.execute(stmt)
    promocode = result.scalars().first()
    if promocode:
        await session.execute(delete(Promocode).where(Promocode.id == promocode_id))
        await session.commit()
        return True  # Успешное удаление
    else:
        return False


@connection
async def check_promocode(session, promocode_name):
    promocode = await session.scalar(
        select(Promocode).where(Promocode.name == promocode_name)
    )
    if not promocode:
        return None
    # Проверяем дату истечения
    if promocode.expiration_date and promocode.expiration_date < datetime.now():
        # Устанавливаем промокод как неактивный, если дата истекла
        await session.execute(
            update(Promocode)
            .where(Promocode.id == promocode.id)
            .values(is_active=False)
        )
        await session.commit()
        return None
    if promocode.is_active:
        return promocode.discount, promocode.id
    return None


@connection
async def increase_usage_of_promocodes(session, promocode_id):
    promocode = await session.scalar(
        select(Promocode).where(Promocode.id == promocode_id)
    )
    if promocode:
        promocode.usage_quantity += 1
        await session.commit()


# @connection
# async def create_reservation(
#     session,
#     user_id,
#     visit_date,
#     tariff_name,
#     amount_wo_discount,
#     amount_w_discount,
#     payment_id=None,
#     promocode_name=None,
# ):
#     new_reservation = Reservation(
#         user_id=user_id,
#         visit_date=visit_date,
#         tariff_name=tariff_name,
#         promocode_name=promocode_name,
#         amount_wo_discount=amount_wo_discount,
#         amount_w_discount=amount_w_discount,
#         payment_id=payment_id,
#     )
#     session.add(new_reservation)
#     await session.commit()
#     return new_reservation
@connection
async def create_booking(
    session,
    user_tg_id,
    tariff_id,
    visit_date,
    start_time=None,
    end_time=None,
    duration=None,
    promocode_id=None,
    amount_wo_discount=None,
    amount_w_discount=None,
    payment_id=None,
    paid=None,
    rubitime_id=None,
    confirmed=None,
    removed=None,
):
    new_booking = Booking(
        user_tg_id=user_tg_id,
        tariff_id=tariff_id,
        visit_date=visit_date,
        start_time=start_time,
        end_time=end_time,
        duration=duration,
        promocode_id=promocode_id,
        amount_wo_discount=amount_wo_discount,
        amount_w_discount=amount_w_discount,
        payment_id=payment_id,
        paid=paid,
        rubitime_id=rubitime_id,
        confirmed=confirmed,
        removed=removed,
    )
    session.add(new_booking)
    await session.commit()
    return new_booking


# @connection
# async def get_reservation_by_id(session, reservation_id):
#     reservation = await session.scalar(select(Reservation).where(Reservation.id == reservation_id))
#     return reservation


# @connection
# async def update_reservation_fields(session, reservation_id, **kwargs):
#     await session.execute(
#         update(Reservation).where(Reservation.id == reservation_id).values(**kwargs)
#     )
#     await session.commit()
@connection
async def update_booking_fields(session, booking_id, **kwargs):
    await session.execute(
        update(Booking).where(Booking.id == booking_id).values(**kwargs)
    )
    await session.commit()


# @connection
# async def get_reservation_for_period(session, first_day: str, last_day: str):
#     first_date = datetime.strptime(first_day, "%d.%m.%Y").date()
#     last_date = datetime.strptime(last_day, "%d.%m.%Y").date()
#
#     # Запрос всех тикетов, где дата тикета между first_date и last_date
#     query = select(Reservation).where(
#         Reservation.visit_date.between(first_date, last_date)
#     )
#
#     result = await session.execute(query)
#     reservation = result.scalars().all()
#
#     return reservation
# @connection
# async def get_reservation_for_period(session, first_day: str, last_day: str):
#     first_date = datetime.strptime(first_day, "%d.%m.%Y").date()
#     last_date = datetime.strptime(last_day, "%d.%m.%Y").date()
#
#     # Запрос с joinedload для предварительной загрузки связанных данных
#     query = (
#         select(Reservation)
#         .options(
#             joinedload(Reservation.user),
#             joinedload(Reservation.tariff),
#             joinedload(Reservation.promocode),
#         )
#         .where(Reservation.visit_date.between(first_date, last_date))
#     )
#
#     result = await session.execute(query)
#     reservations = result.scalars().all()
#
#     return reservations
@connection
async def get_booking_for_period(session, first_day: str, last_day: str):
    first_date = datetime.strptime(first_day, "%d.%m.%Y").date()
    last_date = datetime.strptime(last_day, "%d.%m.%Y").date()

    # Запрос с joinedload для предварительной загрузки связанных данных
    query = (
        select(Booking)
        .options(
            joinedload(Booking.user),
            joinedload(Booking.tariff),
            joinedload(Booking.promocode),
        )
        .where(Booking.visit_date.between(first_date, last_date))
    )

    result = await session.execute(query)
    reservations = result.scalars().all()

    return reservations


# @connection
# async def get_all_reservations(session, user_id):
#     reservations = await session.scalars(
#         select(Reservation).where(Reservation.user_id == user_id)
#     )
#     return reservations.all()


# @connection
# async def get_all_reservations_by_date(session, visit_date):
#     reservations = await session.scalars(
#         select(Reservation).where(Reservation.visit_date == visit_date)
#     )
#     return reservations.all()


# @connection
# async def update_fields(session, model, record_id, **kwargs):
#     await session.execute(
#         update(model)@connection
#         .where(model.id == record_id)
#         .values(**kwargs)
#     )
#     await session.commit()


@connection
async def create_guest(
    session, user_id, guest_name, guest_phone, office_number, visit_date
):
    new_guest = Guest(
        user_id=user_id,
        guest_name=guest_name,
        guest_phone=guest_phone,
        office_number=office_number,
        visit_date=visit_date,
    )
    session.add(new_guest)
    await session.commit()
    return new_guest


# @connection
# async def get_all_spaces(session):
#     result = await session.execute(select(Room).where(Room.state.is_(True)))
#     return result.scalars().all()


# @connection
# async def get_space_by_id(session, room_id):
#     result = await session.execute(select(Room).where(Room.id == room_id))
#     return result.scalar_one_or_none()


# @connection
# async def add_meeting_room_booking(
#     session, user_id, visit_date, start_time, end_time, duration
# ):
#     new_booking = MeetingRoom(
#         user_id=user_id,
#         visit_date=visit_date,
#         start_time=start_time,
#         end_time=end_time,
#         duration=duration,
#     )
#     session.add(new_booking)
#     await session.commit()
# @connection
# async def add_meeting_room_booking(
#     session, user_id, room_id, visit_date, start_time, end_time, duration
# ) -> int:
#     new_booking = Booking(
#         user_id=user_id,
#         room_id=room_id,
#         visit_date=visit_date,
#         start_time=start_time,
#         end_time=end_time,
#         duration=duration,
#     )
#     session.add(new_booking)
#     await session.commit()
#     await session.refresh(new_booking)  # Получаем ID созданного объекта из БД
#     return new_booking.id


# @connection
# async def update_booking_mr_status(session, booking_id, confirmed: bool):
#     booking = await session.get(Booking, booking_id)
#     if booking:
#         booking.confirmed = confirmed  # Добавьте поле "confirmed" в модель, если нужно
#         await session.commit()


# @connection
# async def update_booking_mr_rubitime(session, booking_id, rubitime_id):
#     booking = await session.get(Booking, booking_id)
#     if booking:
#         booking.rubitime_id = rubitime_id
#         await session.commit()


# @connection
# async def get_all_booking_mr(session):
#     result = await session.execute(select(MeetingRoom))
#     return result.scalars().all()
# @connection
# async def get_all_booking_mr(session):
#     result = await session.execute(
#         select(Booking).options(
#             joinedload(Booking.user),
#             joinedload(Booking.room))
#     )
#     return result.scalars().all()
@connection
async def get_all_bookings(session):
    result = await session.execute(
        select(Booking).options(
            joinedload(Booking.user),
            joinedload(Booking.tariff),
            joinedload(Booking.promocode),
        )
    )
    return result.scalars().all()


# @connection
# async def delete_booking_mr(session, booking_id):
#     # Ищем объект по ID
#     booking = await session.get(MeetingRoom, booking_id)
#     if booking:
#         # Удаляем найденный объект
#         await session.delete(booking)
#         # Фиксируем изменения в базе данных
#         await session.commit()


# @connection
# async def delete_booking_mr(session, booking_id):
#     # Создаем запрос для поиска бронирования по id
#     stmt = select(Booking).where(Booking.id == booking_id)
#     result = await session.execute(stmt)
#     booking = result.scalars().first()
#
#     if booking:
#         # Если бронирование найдено, выполняем запрос на удаление
#         await session.execute(delete(Booking).where(Booking.id == booking_id))
#         await session.commit()
#         return True  # Успешное удаление
#     return False  # Бронирование не найдено
# @connection
# async def delete_booking(session, booking_id):
#     # Создаем запрос для поиска бронирования по id
#     stmt = select(Booking).where(Booking.id == booking_id)
#     result = await session.execute(stmt)
#     booking = result.scalars().first()
#
#     if booking:
#         # Если бронирование найдено, выполняем запрос на удаление
#         booking.removed = True
#         booking.confirmed = False
#         await session.commit()
#         return True  # Успешное удаление
#     return False  # Бронирование не найдено
@connection
async def delete_booking(session, booking_id, confirmed=False, removed=False):
    """
    Обновляет состояние бронирования в зависимости от переданных параметров.

    :param session: Сессия базы данных.
    :param booking_id: ID бронирования.
    :param confirmed: Новое значение для поля confirmed.
    :param removed: Новое значение для поля removed.
    :return: True, если бронирование обновлено, иначе False.
    """
    # Создаем запрос для поиска бронирования по id
    stmt = select(Booking).where(Booking.id == booking_id)
    result = await session.execute(stmt)
    booking = result.scalars().first()

    if booking:
        # Обновляем параметры бронирования
        booking.removed = removed
        booking.confirmed = confirmed
        await session.commit()
        return True  # Успешное обновление
    return False  # Бронирование не найдено


# @connection
# async def get_user_id_by_booking(session, booking_id):
#     booking = await session.get(Booking, booking_id)
#     # return booking.user_id if booking else None
#     return booking if booking else None
@connection
async def get_user_id_by_booking(session, booking_id):
    """
    Получает объект Booking по ID с загрузкой всех необходимых связанных данных.
    :param session: Сессия базы данных.
    :param booking_id: ID бронирования.
    :return: Объект Booking или None.
    """
    stmt = (
        select(Booking)
        .options(
            joinedload(Booking.user),  # Загрузить связанные данные (например, user)
            joinedload(Booking.tariff),  # Пример загрузки другого связанного объекта
        )
        .where(Booking.id == booking_id)
    )

    result = await session.execute(stmt)
    booking = result.scalars().first()

    return booking  # Вернем весь объект Booking


# @connection
# async def is_time_available(session, visit_date, visit_time):
#     query = select(MeetingRoom).where(
#         MeetingRoom.visit_date == visit_date,
#         MeetingRoom.visit_time == visit_time
#     )
#     result = await session.execute(query)
#     return result.scalar() is None  # Возвращает True, если запись отсутствует (время свободно)
# @connection
# async def is_time_available(session, visit_date, start_time, end_time):
#     query = (
#         select(Booking)
#         .where(Booking.visit_date == visit_date)
#         .where((start_time < Booking.end_time) & (end_time > Booking.start_time))
#     )
#     result = await session.execute(query)
#     return result.scalar() is None


# @connection
# async def is_time_available(session, tariff_id, visit_date, start_time, end_time):
#     # Проверка, связан ли тариф с переговорной
#     tariff_query = select(Tariff).where(Tariff.id == tariff_id)
#     result = await session.execute(tariff_query)
#     tariff = result.scalars().first()
#
#     if not tariff or tariff.purpose not in {"Переговорная", "Амфитеатр"}:
#         return True  # Если это не переговорная или амфитеатр, ограничений нет
#
#     # Проверка пересечения времени для переговорной
#     overlapping_booking_query = (
#         select(Booking)
#         .join(Tariff)
#         .where(
#             Tariff.purpose.in_({"Переговорная", "Амфитеатр"}),
#             Booking.visit_date == visit_date,
#             or_(
#                 and_(Booking.start_time <= start_time, Booking.end_time > start_time),
#                 and_(Booking.start_time < end_time, Booking.end_time >= end_time),
#                 and_(Booking.start_time >= start_time, Booking.end_time <= end_time),
#             ),
#         )
#     )
#     overlapping_result = await session.execute(overlapping_booking_query)
#     overlapping_booking = overlapping_result.scalars().first()
#
#     return overlapping_booking is None
# @connection
# async def is_time_available(session, tariff_id, visit_date, start_time, end_time):
#     # Проверка, связан ли тариф с переговорной
#     tariff_query = select(Tariff).where(Tariff.id == tariff_id)
#     result = await session.execute(tariff_query)
#     tariff = result.scalars().first()
#
#     if not tariff:
#         return False  # Если тариф не найден, возвращаем False
#
#     # Определяем категорию, с которой будет работать проверка
#     category = tariff.purpose
#
#     # Если это не "Переговорная" или "Амфитеатр", ограничений нет
#     if category not in {"Переговорная", "Амфитеатр"}:
#         return True
#
#     # Проверка пересечения времени для каждой категории отдельно
#     overlapping_booking_query = (
#         select(Booking)
#         .join(Tariff)
#         .where(
#             Tariff.purpose == category,  # Фильтруем по текущей категории
#             Booking.visit_date == visit_date,
#             Booking.removed == False,  # Учитываем только активные бронирования
#             or_(
#                 and_(Booking.start_time <= start_time, Booking.end_time > start_time),
#                 and_(Booking.start_time < end_time, Booking.end_time >= end_time),
#                 and_(Booking.start_time >= start_time, Booking.end_time <= end_time),
#             ),
#         )
#     )
#
#     overlapping_result = await session.execute(overlapping_booking_query)
#     overlapping_booking = overlapping_result.scalars().first()
#
#     return overlapping_booking is None
@connection
async def is_time_available(session, tariff_id, visit_date, start_time, end_time):
    # Проверка существующих бронирований с такими же параметрами для того же тарифа
    existing_booking_query = select(Booking).where(
        and_(
            Booking.visit_date == visit_date,
            Booking.start_time == start_time,
            Booking.end_time == end_time,
            Booking.tariff_id == tariff_id,
            Booking.removed == False,  # Учитываем только активные бронирования
        )
    )
    existing_booking_result = await session.execute(existing_booking_query)
    existing_booking = existing_booking_result.scalars().first()

    # Если уже существует активное бронирование с такими же параметрами, возвращаем False
    if existing_booking:
        return False

    # Если тариф - "Переговорная" или "Амфитеатр", проверяем пересечение времени только с другими такими же бронированиями
    overlapping_booking_query = select(Booking).where(
        Booking.visit_date == visit_date,
        or_(
            and_(Booking.start_time <= start_time, Booking.end_time > start_time),
            and_(Booking.start_time < end_time, Booking.end_time >= end_time),
            and_(Booking.start_time >= start_time, Booking.end_time <= end_time),
        ),
        Booking.removed.is_(False),
    )

    # Проверяем для того же тарифа (например, "Переговорная" или "Амфитеатр")
    if tariff_id in ["Переговорная", "Амфитеатр"]:
        overlapping_result = await session.execute(overlapping_booking_query)
        overlapping_booking = overlapping_result.scalars().first()

        # Если есть пересечение времени для одного тарифа, возвращаем False
        if overlapping_booking:
            return False

    return True


# @connection
# async def is_time_available(session, tariff_id, visit_date, start_time, end_time):
#     # Проверка, связан ли тариф с переговорной
#     tariff_query = select(Tariff).where(Tariff.id == tariff_id)
#     result = await session.execute(tariff_query)
#     tariff = result.scalars().first()
#
#     if not tariff:
#         return False  # Если тариф не найден, возвращаем False
#
#     # Определяем категорию, с которой будет работать проверка
#     category = tariff.purpose
#
#     # Если это не "Переговорная" или "Амфитеатр", ограничений нет
#     if category not in {"Переговорная", "Амфитеатр"}:
#         return True
#
#     # Проверка пересечения времени для выбранной категории
#     overlapping_booking_query = (
#         select(Booking)
#         .join(Tariff)
#         .where(
#             Booking.visit_date == visit_date,
#             Booking.confirmed.is_(False),
#             Booking.removed.is_(False),  # Учитываем только активные бронирования
#             or_(
#                 and_(Booking.start_time <= start_time, Booking.end_time > start_time),
#                 and_(Booking.start_time < end_time, Booking.end_time >= end_time),
#                 and_(Booking.start_time >= start_time, Booking.end_time <= end_time),
#             ),
#         )
#     )
#
#     # Если категория "Переговорная"
#     if category == "Переговорная":
#         overlapping_booking_query = overlapping_booking_query.where(
#             Tariff.purpose == "Переговорная"
#         )
#
#     # Если категория "Амфитеатр"
#     elif category == "Амфитеатр":
#         overlapping_booking_query = overlapping_booking_query.where(
#             Tariff.purpose == "Амфитеатр"
#         )
#
#     overlapping_result = await session.execute(overlapping_booking_query)
#     overlapping_booking = overlapping_result.scalars().first()
#
#     # Если пересечение найдено, возвращаем False
#     return overlapping_booking is None


async def parse_quiz_file(file_path: str) -> list[dict[str, any]]:
    quizzes = []
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} not found")

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Разделяем квизы по хэштегам
    quiz_blocks = content.strip().split("# Квиз")

    for quiz_block in quiz_blocks:
        if not quiz_block.strip():
            continue

        lines = quiz_block.strip().splitlines()
        name = None
        description = None
        questions = []

        question_text = None
        correct_answer = None
        answer_options = []
        photo_url = None  # Переменная для хранения URL фото

        for line in lines:
            if line.startswith("Название:"):
                name = line.split("Название:")[1].strip()
            elif line.startswith("Описание:"):
                description = line.split("Описание:")[1].strip()
            elif re.match(r"\d+\.\d+ Вопрос:", line):
                # Если есть вопрос, добавляем его в список вопросов перед обработкой следующего
                if question_text and correct_answer and answer_options:
                    questions.append(
                        {
                            "question_text": question_text,
                            "correct_answer": correct_answer,
                            "answer_options": answer_options,
                            "photo_url": photo_url,  # Добавляем фото в вопрос
                        }
                    )
                # Обнуляем все поля для нового вопроса
                question_text = line.split("Вопрос:")[1].strip()
                correct_answer = None
                answer_options = []
                photo_url = None  # Сбрасываем фото для каждого нового вопроса
            elif line.startswith("Фото:"):
                photo_url = line.split("Фото:")[1].strip()
            elif line.startswith("Правильный ответ:"):
                correct_answer = line.split("Правильный ответ:")[1].strip()
            elif line.startswith("Варианты ответов:"):
                answer_options = [
                    option.strip()
                    for option in line.split("Варианты ответов:")[1].split(",")
                ]

        # Добавляем последний вопрос в список
        if question_text and correct_answer and answer_options:
            questions.append(
                {
                    "question_text": question_text,
                    "correct_answer": correct_answer,
                    "answer_options": answer_options,
                    "photo_url": photo_url,
                }
            )

        if name and description and questions:
            quizzes.append(
                {"name": name, "description": description, "questions": questions}
            )

    return quizzes


# @connection
# async def add_quiz(session, name: str, description: str) -> Quiz:
#     new_quiz = Quiz(name=name, description=description)
#     session.add(new_quiz)
#     await session.commit()
#     return new_quiz


# @connection
# async def add_question(
#     session,
#     quiz_id: int,
#     question_text: str,
#     correct_answer: str,
#     answer_options: list[str],
#     photo_url: str = None,
# ) -> None:
#     options_json = json.dumps(answer_options, ensure_ascii=False)
#     new_question = Question(
#         quiz_id=quiz_id,
#         question_text=question_text,
#         correct_answer=correct_answer,
#         answer_options=options_json,
#         photo_url=photo_url,
#     )
#     session.add(new_question)
#     await session.commit()


# @connection
# async def add_quizzes_from_file(session, file_path: str) -> None:
#     quizzes = await parse_quiz_file(file_path)
#     for quiz in quizzes:
#         # Проверяем, существует ли квиз с таким именем
#         existing_quiz = await session.execute(select(Quiz).filter_by(name=quiz["name"]))
#         existing_quiz = existing_quiz.scalar_one_or_none()
#
#         if not existing_quiz:
#             text = f"Квиз {quiz['name']} успешно добавлен!"
#             # Добавляем новый квиз
#             new_quiz = await add_quiz(quiz["name"], quiz["description"])
#
#             # Добавляем вопросы для нового квиза
#             for question in quiz["questions"]:
#                 await add_question(
#                     quiz_id=new_quiz.id,
#                     question_text=question["question_text"],
#                     correct_answer=question["correct_answer"],
#                     answer_options=question["answer_options"],
#                     photo_url=question["photo_url"],
#                 )
#         else:
#             text = f"Квиз {quiz['name']} уже существует!"
#     await session.commit()
#     return text


# @connection
# async def quiz_exists(session, quiz_name: str) -> bool:
#     """Проверка наличия квиза по названию."""
#     existing_quiz = await session.execute(select(Quiz).filter_by(name=quiz_name))
#     return existing_quiz.scalar_one_or_none() is not None
#
#
# @connection
# async def question_exists(session, quiz_id: int, question_text: str) -> bool:
#     """Проверка наличия вопроса по тексту в конкретном квизе."""
#     existing_question = await session.execute(
#         select(Question).filter_by(quiz_id=quiz_id, question_text=question_text)
#     )
#     return existing_question.scalar_one_or_none() is not None
#
#
# @connection
# async def add_quizzes_from_file(session, file_path: str) -> None:
#     quizzes = await parse_quiz_file(file_path)
#
#     for quiz in quizzes:
#         # Проверяем, существует ли квиз с таким именем
#         if await quiz_exists(quiz['name']):
#             text = f"Квиз '{quiz['name']}' уже существует. Пропускаем добавление."
#             # print(f"Квиз '{quiz['name']}' уже существует. Пропускаем добавление.")
#             continue  # Пропускаем добавление этого квиза
#         else:
#             text = f"Квиз '{quiz['name']}' успешно добавлен."
#         # Добавляем новый квиз
#         new_quiz = await add_quiz(quiz['name'], quiz['description'])
#
#         # Добавляем вопросы для нового квиза
#         for question in quiz['questions']:
#             # Проверяем, существует ли вопрос с таким текстом
#             if await question_exists(new_quiz.id, question['question_text']):
#                 text = f"Вопрос '{question['question_text']}' уже существует в квизе '{quiz['name']}'. Пропускаем."
#                 # print(f"Вопрос '{question['question_text']}' уже существует в квизе '{quiz['name']}'. Пропускаем.")
#                 continue  # Пропускаем этот вопрос
#
#             await add_question(
#                 quiz_id=new_quiz.id,
#                 question_text=question['question_text'],
#                 correct_answer=question['correct_answer'],
#                 answer_options=question['answer_options'],
#                 photo_url=question['photo_url']
#             )
#     await session.commit()
#     return text


# @connection
# async def get_all_quizzes(session):
#     result = await session.execute(select(Quiz))
#     quizzes = result.scalars().all()  # Получаем все квизы как список объектов Quiz
#     quiz_data = [{"id": quiz.id, "name": quiz.name} for quiz in quizzes]
#     return quiz_data


# @connection
# async def get_questions_for_quiz(session, quiz_id: int) -> list[dict[str, any]]:
#     result = await session.execute(select(Question).filter_by(quiz_id=quiz_id))
#     questions = result.scalars().all()
#
#     return [
#         {
#             "id": question.id,
#             "quiz_id": question.quiz_id,
#             "question_text": question.question_text,
#             "correct_answer": question.correct_answer,
#             "answer_options": json.loads(
#                 question.answer_options
#             ),  # Преобразуем JSON обратно в список
#             "photo_url": question.photo_url,
#         }
#         for question in questions
#     ]


# @connection
# async def record_quiz_result(
#     session, user_id: int, quiz_id: int, score: int, completed_at: str
# ) -> None:
#     new_result = QuizResult(
#         user_id=user_id, quiz_id=quiz_id, score=score, completed_at=completed_at
#     )
#     session.add(new_result)
#     await session.commit()


# @connection
# async def get_all_quiz_results(session) -> list[QuizResult]:
#     results = await session.execute(select(QuizResult))
#     return results.scalars().all()


@connection
async def create_or_update_admin(
    session, tg_id, tg_username: str = None, name: str = None
):
    # Проверяем, существует ли уже администратор с таким tg_id
    admin = await session.scalar(select(Admin).where(Admin.tg_id == tg_id))

    if admin:
        # Если администратор существует, обновляем его данные
        await session.execute(
            update(Admin)
            .where(Admin.tg_id == tg_id)
            .values(
                tg_username=tg_username or admin.tg_username,
                name=name or admin.name,
            )
        )
    elif tg_id in BOT_ADMINS:
        # Если администратора не существует, создаем новую запись
        admin = Admin(
            tg_id=tg_id,
            tg_username=tg_username,
            name=name,
        )
        session.add(admin)
    else:
        return None
    await session.commit()
    return admin


@connection
async def get_admins_from_db(session):
    result = await session.execute(
        select(Admin.id, Admin.tg_id, Admin.tg_username, Admin.name)
    )
    return result.all()  # Возвращаем все поля, а не только tg_id


@connection
async def save_admin_to_db(session, tg_id):
    new_admin = Admin(tg_id=tg_id)
    session.add(new_admin)
    await session.commit()


@connection
async def delete_admin_by_id(session, admin_id):
    stmt = select(Admin).where(Admin.id == admin_id)
    result = await session.execute(stmt)
    admin = result.scalars().first()
    if admin:
        # Если администратор найден, удалим его
        await session.execute(delete(Admin).where(Admin.id == admin_id))
        await session.commit()
        return True  # Успешное удаление
    else:
        return False  # Администратор не найден


@connection
async def get_adjustments(session) -> dict:
    result = await session.execute(
        select(Adjustment.name, Adjustment.state, Adjustment.value)
    )
    adjustments = result.all()
    return {
        adjustment.name: {"state": adjustment.state, "value": adjustment.value}
        for adjustment in adjustments
    }


@connection
async def update_adjustment(
    session, name, state: bool = None, value: str = None
) -> None:
    # Создаем запрос для обновления данных
    update_stmt = update(Adjustment).where(Adjustment.name == name)

    # Добавляем только те поля, которые нужно обновить
    values_to_update = {}
    if state is not None:
        values_to_update["state"] = state
    if value is not None:
        values_to_update["value"] = value

    if values_to_update:
        # Выполняем обновление
        await session.execute(update_stmt.values(**values_to_update))
        await session.commit()


@connection
async def add_at_symbol_to_usernames(session):
    result = await session.execute(select(User))
    users = result.scalars().all()
    for user in users:
        if user.tg_username and not user.tg_username.startswith("@"):
            user.tg_username = f"@{user.tg_username}"
    await session.commit()
