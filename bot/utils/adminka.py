from aiogram.filters import BaseFilter
from aiogram.types import Message
from bot.data.config import admins_id


class AdminIs(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.from_user.id in admins_id:
            return True
        return False
