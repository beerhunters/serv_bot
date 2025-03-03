from aiogram.filters import BaseFilter
from aiogram.types import Message

from tgbot import config
from tgbot.database.requests import get_admins_from_db


class IsOwnerFilter(BaseFilter):
    """
    Custom filter "is_owner".
    """

    key = "is_owner"

    def __init__(self, is_owner):
        self.is_owner = is_owner

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in config.BOT_OWNERS


class IsAdminFilter(BaseFilter):
    """
    Custom filter "is_admin".
    """

    key = "is_admin"

    def __init__(self, is_admin):
        self.is_admin = is_admin

    async def __call__(self, message: Message) -> bool:
        # Получаем администраторов из БД
        db_admins = await get_admins_from_db()

        # Извлекаем только tg_id администраторов
        db_admin_ids = [admin[1] for admin in db_admins]  # admin[1] это tg_id

        # Объединяем списки администраторов
        bot_admins = list(
            set(config.BOT_ADMINS + db_admin_ids)
        )  # Удаляем дубликаты, если есть

        # # Объединяем списки администраторов
        # bot_admins = list(set(config.BOT_ADMINS + db_admins))  # Удаляем дубликаты, если есть

        # return message.from_user.id in config.BOT_ADMINS
        return message.from_user.id in bot_admins


class IsUserFilter(BaseFilter):
    """
    Custom filter for regular users.
    """

    key = "is_user"

    def __init__(self, is_user: bool):
        self.is_user = is_user

    async def __call__(self, message: Message) -> bool:
        user_id = message.from_user.id
        return (user_id not in config.BOT_ADMINS) and (user_id not in config.BOT_OWNERS)


class RoleFilter(BaseFilter):
    """
    Custom filter to check if a user has one of the specified roles.
    """

    key = "roles"

    def __init__(self, roles):
        self.roles = roles

    async def __call__(self, message: Message) -> bool:
        user_id = message.from_user.id

        # Проверка на владельца
        if "owner" in self.roles and user_id in config.BOT_OWNERS:
            return True

        # Получение администраторов из базы данных
        db_admins = await get_admins_from_db()
        db_admin_ids = {admin[1] for admin in db_admins}  # admin[1] — это tg_id
        bot_admins = set(config.BOT_ADMINS).union(db_admin_ids)

        # Проверка на администратора
        if "admin" in self.roles and user_id in bot_admins:
            return True

        # Проверка на пользователя
        if "user" in self.roles:
            return True

        return False


# class IsAdminFilter(BaseFilter):
#     """
#     Filter that checks for admin rights existence
#     """
#     key = "is_admin"
#
#     def __init__(self, is_admin: bool):
#         self.is_admin = is_admin
#
#     async def __call__(self, message: types.Message) -> bool:
#         member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
#         return member.is_chat_admin() == self.is_admin


# class MemberCanRestrictFilter(BaseFilter):
#     """
#     Filter that checks member ability for restricting
#     """
#     key = 'member_can_restrict'
#
#     def __init__(self, member_can_restrict: bool) -> bool:
#         self.member_can_restrict = member_can_restrict
#
#     async def __call__(self, message: types.Message):
#         member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
#
#         # I don't know why, but telegram thinks, if member is chat creator, he cant restrict member
#         return (member.is_chat_creator() or member.can_restrict_members) == self.member_can_restrict
