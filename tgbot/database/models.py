from sqlalchemy import (
    ForeignKey,
    String,
    BigInteger,
    Boolean,
    func,
    DateTime,
    Integer,
    Float,
)
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    reg_date: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=func.now(), index=True
    )
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    tg_username: Mapped[str] = mapped_column(
        String(32), nullable=True
    )  # Telegram usernames до 32 символов
    name: Mapped[str] = mapped_column(
        String(100), nullable=True
    )  # Увеличено для длинных имен
    contact: Mapped[str] = mapped_column(
        String(20), nullable=True
    )  # Подходит для телефонных номеров
    email: Mapped[str] = mapped_column(
        String(255), nullable=True
    )  # Стандартная длина email
    successful_bookings: Mapped[int] = mapped_column(Integer, default=0)
    language_code: Mapped[str] = mapped_column(
        String(10), nullable=True, default="ru"
    )  # ISO коды короче

    tickets: Mapped[list["Ticket"]] = relationship(
        "Ticket", back_populates="user", lazy="selectin"
    )
    guests: Mapped[list["Guest"]] = relationship(
        "Guest", back_populates="user", lazy="selectin"
    )
    bookings: Mapped[list["Booking"]] = relationship(
        "Booking", back_populates="user", lazy="selectin"
    )

    __labels__ = {
        "id": "№",
        "reg_date": "Дата регистрации",
        "tg_id": "ID пользователя",
        "tg_username": "Юзернейм",
        "name": "ФИО",
        "contact": "Телефон",
        "email": "Email",
        "successful_bookings": "Кол-во бронирований",
    }

    def __repr__(self):
        return f"<User(id={self.id}, tg_id={self.tg_id}, name={self.name})>"


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    reg_time: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        default=func.timezone("Europe/Moscow"),  # Устанавливаем UTC+3 по умолчанию
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.tg_id"), type_=BigInteger, index=True
    )
    location_name: Mapped[str] = mapped_column(
        ForeignKey("locations.name"), type_=String(20), index=True
    )  # Исправлен тип
    description: Mapped[str] = mapped_column(
        String(255)
    )  # Увеличено для длинных описаний
    photo_id: Mapped[str] = mapped_column(
        String(255), nullable=True
    )  # Увеличено для длинных ID

    state: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    ticket_comm: Mapped[str] = mapped_column(String(255), nullable=True)  # Увеличено
    finish_time: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    finish_photo_id: Mapped[str] = mapped_column(
        String(255), nullable=True
    )  # Увеличено
    admin_id: Mapped[int] = mapped_column(
        ForeignKey("admins.tg_id"), type_=BigInteger, nullable=True, index=True
    )
    time_spent: Mapped[int] = mapped_column(Integer, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="tickets")
    location: Mapped["Location"] = relationship("Location", back_populates="tickets")
    admin: Mapped["Admin"] = relationship("Admin", back_populates="tickets")

    __labels__ = {
        "id": "Номер заявки",
        "reg_time": "Дата регистрации",
        "user_id": "ID пользователя",
        "description": "Описание",
        "location_name": "Локация",
        "photo_id": "ID фото",
        "state": "Статус",
        "ticket_comm": "Решение/комментарий",
        "finish_time": "Дата закрытия",
        "finish_photo_id": "ID фото",
        "admin_id": "Ответственный",
        "time_spent": "Время выполнения",
    }

    def __repr__(self):
        return f"<Ticket(id={self.id}, user_id={self.user_id}, state={self.state})>"


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, index=True
    )  # Увеличено и обязательное

    tickets: Mapped[list["Ticket"]] = relationship("Ticket", back_populates="location")

    def __repr__(self):
        return f"<Location(id={self.id}, name={self.name})>"


class Promocode(Base):
    __tablename__ = "promocodes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, index=True
    )  # Увеличено и обязательное
    discount: Mapped[int] = mapped_column(Integer, nullable=False)  # Обязательное
    usage_quantity: Mapped[int] = mapped_column(Integer, default=0)
    expiration_date: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    bookings: Mapped[list["Booking"]] = relationship(
        "Booking", back_populates="promocode"
    )

    def __repr__(self):
        return f"<Promocode(id={self.id}, name={self.name}, discount={self.discount})>"


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_tg_id: Mapped[int] = mapped_column(
        ForeignKey("users.tg_id"), type_=BigInteger, nullable=False, index=True
    )
    tariff_id: Mapped[int] = mapped_column(
        ForeignKey("tariffs.id"), nullable=False, index=True
    )
    visit_date: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )  # Исправлен тип
    start_time: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )  # Исправлен тип
    end_time: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )  # Исправлен тип
    duration: Mapped[int] = mapped_column(Integer, nullable=True)
    promocode_id: Mapped[int] = mapped_column(
        ForeignKey("promocodes.id"), nullable=True, index=True
    )
    amount_wo_discount: Mapped[float] = mapped_column(
        Float, nullable=True
    )  # Float для точности
    amount_w_discount: Mapped[float] = mapped_column(
        Float, nullable=True
    )  # Float для точности
    payment_id: Mapped[str] = mapped_column(
        String(36), nullable=True
    )  # Увеличено для UUID
    paid: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    rubitime_id: Mapped[int] = mapped_column(Integer, nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    removed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    user: Mapped["User"] = relationship("User", back_populates="bookings")
    tariff: Mapped["Tariff"] = relationship("Tariff", back_populates="bookings")
    promocode: Mapped["Promocode"] = relationship(
        "Promocode", back_populates="bookings"
    )

    __labels__ = {
        "id": "Номер",
        "user_tg_id": "TG ID пользователя",
        "tariff_id": "ID Тарифа",
        "visit_date": "Дата визита",
        "start_time": "Время начала",
        "end_time": "Время окончания",
        "duration": "Продолжительность",
        "promocode_id": "ID Промокода",
        "amount_wo_discount": "Сумма",
        "amount_w_discount": "Сумма со скидкой",
        "payment_id": "ID оплаты",
        "paid": "Статус оплаты",
        "rubitime_id": "Rubitime ID",
        "confirmed": "Статус подтверждения",
        "removed": "Удален",
    }

    def __repr__(self):
        return f"<Booking(id={self.id}, user_tg_id={self.user_tg_id}, tariff_id={self.tariff_id})>"


class Tariff(Base):
    __tablename__ = "tariffs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )  # Обязательное
    description: Mapped[str] = mapped_column(String(255), default="Just a description")
    price: Mapped[float] = mapped_column(Float, nullable=False)  # Float для точности
    purpose: Mapped[str] = mapped_column(String(50), nullable=True)  # Увеличено
    service_id: Mapped[int] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="tariff")

    def __repr__(self):
        return f"<Tariff(id={self.id}, name={self.name}, price={self.price})>"


class Guest(Base):
    __tablename__ = "guests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.tg_id"), nullable=False, type_=BigInteger, index=True
    )
    guest_name: Mapped[str] = mapped_column(String(100), nullable=True)  # Увеличено
    guest_phone: Mapped[str] = mapped_column(String(20), nullable=True)
    office_number: Mapped[int] = mapped_column(Integer, nullable=True)
    visit_date: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )  # Исправлен тип

    user: Mapped["User"] = relationship("User", back_populates="guests")

    def __repr__(self):
        return f"<Guest(id={self.id}, user_id={self.user_id}, guest_name={self.guest_name})>"


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    tg_username: Mapped[str] = mapped_column(String(32), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=True)  # Увеличено

    tickets: Mapped[list["Ticket"]] = relationship("Ticket", back_populates="admin")

    def __repr__(self):
        return f"<Admin(id={self.id}, tg_id={self.tg_id}, name={self.name})>"


class Adjustment(Base):
    __tablename__ = "adjustments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, index=True
    )  # Обязательное и уникальное
    state: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=True, index=True
    )
    value: Mapped[float] = mapped_column(Float, nullable=True)

    def __repr__(self):
        return f"<Adjustment(id={self.id}, name={self.name}, state={self.state})>"
