import logging
from typing import Callable, Awaitable, Dict, Any

import pendulum
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from bot.data.loader import bot
from bot.utils.keyboards import create_markup
from bot.utils.log import get_logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from bot.data.config import admins_id
from bot.db import User


class Engines:
    def __init__(self, session: async_sessionmaker):
        self.bot: async_sessionmaker = session()


class SessionMiddleware:
    def __init__(self, session: AsyncSession):
        self.bot: AsyncSession = session


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool: Engines):
        super().__init__()
        self.session_pools: Engines = session_pool

    async def _get(self) -> SessionMiddleware:
        async with self.session_pools.bot as session_user:
            return SessionMiddleware(session_user)

    async def edit_name(self, session, event):
        db_query = await session.execute(select(User).filter_by(id=event.from_user.id))
        user: User = db_query.scalar()
        if user:
            user.username = event.from_user.username
            user.fullname = event.from_user.full_name
            user.dead = False
            try:
                await session.commit()
            except Exception as e:
                get_logger('bot')
                logging.error(e)

    async def get_locale(self, session, event, data):
        user: User = (await session.execute(select(User).where(User.id == event.from_user.id))).scalar_one()

        if event.from_user.id in admins_id:
            match user.locale:
                case "ru":
                    from bot.locales.ru import text
                    data['locale'] = text.admin
                case "en":
                    from bot.locales.en import text
                    data['locale'] = text.admin

        else:
            match user.locale:
                case "ru":
                    from bot.locales.ru import text
                    data['locale'] = text.user
                case "en":
                    from bot.locales.en import text
                    data['locale'] = text.user

        return data

    async def push_admins(self, new_user: (int, str), sessions: AsyncSession) -> None:
        for admin in admins_id:
            admin_user: User = (await sessions.execute(select(User).where(User.id == admin))).scalar_one_or_none()
            if admin_user:
                match admin_user.locale:
                    case "ru":
                        from bot.locales.ru import text
                        locale = text.admin
                    case _:
                        from bot.locales.en import text
                        locale = text.admin
                markup = await create_markup("inline", [
                    [[locale.inline_view_user, f'tg://user?id={new_user[0]}', ":tg:"]]])
                await bot.send_message(admin_user.id, locale.new_user.format(*new_user), reply_markup=markup)

    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]) -> Any:
        async with self.session_pools.bot as session_user:
            sql = select(User).where(User.id == event.from_user.id)
            user_request = await session_user.execute(sql)
            user = user_request.scalar_one_or_none()
            if not user:
                get_logger('new_users')
                logging.info(f'new <user: id={event.from_user.id}, username={event.from_user.username}>')
                new_user = User(id=event.from_user.id, username=event.from_user.username,
                                fullname=event.from_user.full_name,
                                date=pendulum.now('Europe/Moscow'))
                session_user.add(new_user)
                await session_user.commit()
                await self.push_admins((new_user.id, new_user.username), session_user)

            await self.edit_name(session_user, event)

            data = await self.get_locale(session_user, event, data)

            data["sessions"] = SessionMiddleware(session_user)
            return await handler(event, data)
