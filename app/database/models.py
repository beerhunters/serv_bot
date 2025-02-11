from sqlalchemy import (
    ForeignKey,
    String,
    BigInteger,
    Boolean,
    func,
    DateTime,
    Integer,
    CheckConstraint,
    UniqueConstraint,
    Float,
)
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    async_sessionmaker,
    create_async_engine,
    AsyncSession,
)

engine = create_async_engine(url="sqlite+aiosqlite:///db.sqlite3")

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    reg_date: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    tg_id: Mapped[int] = mapped_column(BigInteger)
    tg_username: Mapped[str] = mapped_column(String, nullable=True)
    name: Mapped[str] = mapped_column(String(20), nullable=True)
    contact: Mapped[str] = mapped_column(String(20), nullable=True)
    email: Mapped[str] = mapped_column(String(20), nullable=True)
    successful_bookings: Mapped[int] = mapped_column(Integer, default=0)
    language_code: Mapped[str] = mapped_column(String(20), nullable=True, default="ru")

    # Добавляем отношение с таблицей
    tickets: Mapped[list["Ticket"]] = relationship("Ticket", back_populates="user")
    # reservations: Mapped[list["Reservation"]] = relationship("Reservation", back_populates="user")
    guests: Mapped[list["Guest"]] = relationship("Guest", back_populates="user")
    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="user")

    # Пользовательский атрибут для читаемых заголовков
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


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    reg_time: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    # Связываем с таблицей User через ForeignKey
    user_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"))
    # Связываем с таблицей Location через ForeignKey
    # location_id: Mapped[int] = mapped_column(ForeignKey('locations.id'))
    location_name: Mapped[int] = mapped_column(ForeignKey("locations.name"))
    description: Mapped[str] = mapped_column(String(128))
    photo_id: Mapped[str] = mapped_column(String(128), nullable=True)

    state: Mapped[bool] = mapped_column(Boolean, default=False)
    ticket_comm: Mapped[str] = mapped_column(String(128), nullable=True)
    finish_time: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    finish_photo_id: Mapped[str] = mapped_column(String(128), nullable=True)
    admin_id: Mapped[int] = mapped_column(ForeignKey("admins.tg_id"), nullable=True)
    time_spent: Mapped[int] = mapped_column(Integer, nullable=True)

    # Отношение с User
    user: Mapped["User"] = relationship("User", back_populates="tickets")
    # Отношение с Location
    location: Mapped["Location"] = relationship("Location", back_populates="tickets")
    # Связь с Admin (кто закрыл тикет)
    admin: Mapped["Admin"] = relationship("Admin", back_populates="tickets")

    # Пользовательский атрибут для читаемых заголовков
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


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20), nullable=True)

    # Отношение с Ticket
    tickets: Mapped[list["Ticket"]] = relationship("Ticket", back_populates="location")


# class Tariff(Base):
#     __tablename__ = "tariffs"
#
#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     name: Mapped[str] = mapped_column(String(20), nullable=True)
#     description: Mapped[str] = mapped_column(String(128), default="Just a description")
#     price: Mapped[int] = mapped_column(Integer)
#     service_id: Mapped[int] = mapped_column(Integer, nullable=True)
#     is_active: Mapped[bool] = mapped_column(Boolean, default=True)
#
#     # reservations: Mapped[list["Reservation"]] = relationship(
#     #     "Reservation", back_populates="tariff"
#     # )
#     bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="tariff")


class Promocode(Base):
    __tablename__ = "promocodes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20), nullable=True)
    discount: Mapped[int] = mapped_column(Integer)
    usage_quantity: Mapped[int] = mapped_column(Integer, default=0)
    expiration_date: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)

    # reservations: Mapped[list["Reservation"]] = relationship(
    #     "Reservation", back_populates="promocode"
    # )
    bookings: Mapped[list["Booking"]] = relationship(
        "Booking", back_populates="promocode"
    )


# class Reservation(Base):
#     __tablename__ = "reservations"
#
#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     user_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"), nullable=False)
#     visit_date: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
#     # visit_date: Mapped[str] = mapped_column(String(20), nullable=True)
#     tariff_name: Mapped[str] = mapped_column(ForeignKey("tariffs.name"), nullable=False)
#     promocode_name: Mapped[str] = mapped_column(
#         ForeignKey("promocodes.name"), nullable=True
#     )
#     amount_wo_discount: Mapped[int] = mapped_column(Integer, nullable=True)
#     amount_w_discount: Mapped[int] = mapped_column(Integer, nullable=True)
#     payment_id: Mapped[str] = mapped_column(String(20), nullable=True)
#     paid: Mapped[bool] = mapped_column(Boolean, default=False)
#     rubitime_id: Mapped[int] = mapped_column(Integer, nullable=True)
#
#     # Связи с другими моделями
#     user: Mapped["User"] = relationship("User", back_populates="reservations")
#     tariff: Mapped["Tariff"] = relationship("Tariff", back_populates="reservations")
#     promocode: Mapped["Promocode"] = relationship(
#         "Promocode", back_populates="reservations"
#     )
#
#     # @property
#     # def promocode_name(self):
#     #     return self.promocode.name if self.promocode else None
#     #
#     # @property
#     # def tariff_name(self):
#     #     return self.tariff.name if self.tariff else None
#     #
#     # @property
#     # def user_name(self):
#     #     return self.user.name if self.user else None
#     # Пользовательский атрибут для читаемых заголовков
#     __labels__ = {
#         "id": "Номер",
#         "user_id": "ID пользователя",
#         "visit_date": "Дата визита",
#         "tariff_name": "Тариф",
#         "promocode_name": "Промокод",
#         "amount_wo_discount": "Сумма",
#         "amount_w_discount": "Сумма со скидкой",
#         "payment_id": "ID оплаты",
#         "paid": "Статус оплаты",
#     }


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_tg_id: Mapped[str] = mapped_column(ForeignKey("users.tg_id"), nullable=False)
    tariff_id: Mapped[str] = mapped_column(ForeignKey("tariffs.id"), nullable=False)
    visit_date: Mapped[str] = mapped_column(String(20), nullable=True)
    start_time: Mapped[str] = mapped_column(String(20), nullable=True)  # Время начала
    end_time: Mapped[str] = mapped_column(String(20), nullable=True)  # Время окончания
    duration: Mapped[int] = mapped_column(Integer, nullable=True)
    promocode_id: Mapped[str] = mapped_column(
        ForeignKey("promocodes.id"), nullable=True
    )
    amount_wo_discount: Mapped[int] = mapped_column(Integer, nullable=True)
    amount_w_discount: Mapped[int] = mapped_column(Integer, nullable=True)
    payment_id: Mapped[str] = mapped_column(String(20), nullable=True)
    paid: Mapped[bool] = mapped_column(Boolean, default=False)
    rubitime_id: Mapped[int] = mapped_column(Integer, nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    removed: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (
        CheckConstraint(
            "start_time LIKE '__:__' AND end_time LIKE '__:__'",
            name="check_time_format",
        ),
        #     UniqueConstraint(
        #         "visit_date",
        #         "start_time",
        #         "end_time",
        #         "tariff_id",
        #         name="unique_booking_for_tariff",
        #     ),
    )
    # Связи с другими моделями
    user: Mapped["User"] = relationship("User", back_populates="bookings")
    tariff: Mapped["Tariff"] = relationship("Tariff", back_populates="bookings")
    promocode: Mapped["Promocode"] = relationship(
        "Promocode", back_populates="bookings"
    )

    # Пользовательский атрибут для читаемых заголовков
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


class Tariff(Base):
    __tablename__ = "tariffs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=True)
    description: Mapped[str] = mapped_column(String(128), default="Just a description")
    price: Mapped[int] = mapped_column(Integer)
    purpose: Mapped[str] = mapped_column(String(20), nullable=True)
    service_id: Mapped[int] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="tariff")


class Guest(Base):
    __tablename__ = "guests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    guest_name: Mapped[str] = mapped_column(String(20), nullable=True)
    guest_phone: Mapped[str] = mapped_column(String(20), nullable=True)
    office_number: Mapped[int] = mapped_column(Integer, nullable=True)
    visit_date: Mapped[str] = mapped_column(String(20), nullable=True)

    # Связи с другими моделями
    user: Mapped["User"] = relationship("User", back_populates="guests")


# class Booking(Base):
#     __tablename__ = "bookings"
#
#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     user_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"), nullable=False)
#
#     room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False)
#
#     visit_date: Mapped[str] = mapped_column(String(20), nullable=True)
#     start_time: Mapped[str] = mapped_column(String(20), nullable=True)  # Время начала
#     end_time: Mapped[str] = mapped_column(String(20), nullable=True)  # Время окончания
#     duration: Mapped[int] = mapped_column(Integer, nullable=True)
#     confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
#     rubitime_id: Mapped[int] = mapped_column(Integer, nullable=True)
#     removed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
#
#     # Добавляем проверку формата времени HH:MM
#     __table_args__ = (
#         CheckConstraint(
#             "start_time LIKE '__:__' AND end_time LIKE '__:__'",
#             name="check_time_format",
#         ),
#         # Уникальность брони в пределах одного времени
#         UniqueConstraint(
#             "user_id",
#             "room_id",
#             "visit_date",
#             "start_time",
#             "end_time",
#             name="user_booking_unique",
#         ),
#     )
#
#     user: Mapped["User"] = relationship("User", back_populates="bookings")
#     room: Mapped["Room"] = relationship("Room", back_populates="bookings")
#
#
# class Room(Base):
#     __tablename__ = "rooms"
#
#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     name: Mapped[str] = mapped_column(String(255), nullable=False)
#     capacity: Mapped[int] = mapped_column(Integer, nullable=False)
#     type: Mapped[str] = mapped_column(String(50), nullable=True)
#     service_id: Mapped[int] = mapped_column(Integer, nullable=True)
#     state: Mapped[bool] = mapped_column(Boolean, default=True)
#
#     bookings: Mapped["Booking"] = relationship("Booking", back_populates="room")


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(128), nullable=False)

    questions: Mapped["Question"] = relationship(
        "Question", back_populates="quiz", cascade="all, delete-orphan"
    )
    quiz_results: Mapped["QuizResult"] = relationship(
        "QuizResult", back_populates="quiz", cascade="all, delete-orphan"
    )


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    quiz_id: Mapped[int] = mapped_column(
        ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False
    )
    question_text: Mapped[str] = mapped_column(String, nullable=False)
    correct_answer: Mapped[str] = mapped_column(String, nullable=False)
    answer_options: Mapped[str] = mapped_column(String, nullable=False)
    photo_url: Mapped[str] = mapped_column(String(128), nullable=True)

    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="questions")


class QuizResult(Base):
    __tablename__ = "quiz_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"), nullable=False)
    quiz_id: Mapped[int] = mapped_column(
        ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False
    )
    # quiz_name: Mapped[str] = mapped_column(ForeignKey('quizzes.name', ondelete='CASCADE'), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    completed_at: Mapped[str] = mapped_column(String(20), nullable=False)

    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="quiz_results")

    # Пользовательский атрибут для читаемых заголовков
    __labels__ = {
        "id": "№",
        "user_id": "ID пользователя",
        "quiz_id": "ID квиза",
        "score": "Очки",
        "completed_at": "Дата завершения",
    }


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(Integer)
    tg_username: Mapped[str] = mapped_column(String(20), nullable=True)
    name: Mapped[str] = mapped_column(String(20), nullable=True)

    # Добавляем отношение с таблицей Ticket
    tickets: Mapped[list["Ticket"]] = relationship("Ticket", back_populates="admin")


class Adjustment(Base):
    __tablename__ = "adjustments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20), nullable=True)
    state: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=True
    )  # Поле "Статус" необязательное
    value: Mapped[float] = mapped_column(
        Float, nullable=True
    )  # Поле "Значение" необязательное, тип можно изменить


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
