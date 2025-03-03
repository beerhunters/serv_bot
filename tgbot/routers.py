from tgbot.handlers.admin_handlers.admin_meeting_room import admin_meeting_router
from tgbot.handlers.admin_handlers.admin_report import admin_report_router
from tgbot.handlers.admin_handlers.admin_ticket import admin_ticket_router
from tgbot.handlers.admin_handlers.admins_users import admin_users_router
from tgbot.handlers.owner_handlers.admins_management import owner_admin_management
from tgbot.handlers.owner_handlers.locations_management import (
    owner_locations_management,
)
from tgbot.handlers.owner_handlers.booking_mr_management import (
    owner_booking_mr_management,
)
from tgbot.handlers.owner_handlers.printing_management import owner_print_management
from tgbot.handlers.owner_handlers.promocodes_management import owner_promo_management
from tgbot.handlers.owner_handlers.tariffs_management import owner_tariff_management
from tgbot.handlers.owner_handlers.users_management import owner_users_management
from tgbot.handlers.user_handlers.booking import booking_router
from tgbot.handlers.user_handlers.booking_meeting_room import meeting_room_router
from tgbot.handlers.admin_handlers.admin import admin_router
from tgbot.handlers.exception_handlers.exceptions import error_router
from tgbot.handlers.user_handlers.guests import guest_router
from tgbot.handlers.owner_handlers.owner import owner_router
from tgbot.handlers.user_handlers.printing import printer_router
from tgbot.handlers.user_handlers.ticket import ticket_router
from tgbot.handlers.user_handlers.user import user_router

ALL_ROUTERS = [
    error_router,
    owner_router,
    owner_admin_management,
    owner_users_management,
    owner_promo_management,
    owner_print_management,
    owner_tariff_management,
    owner_booking_mr_management,
    owner_locations_management,
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
]
