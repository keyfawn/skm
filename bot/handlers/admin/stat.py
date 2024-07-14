from datetime import datetime

from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from pytz import timezone
from sqlalchemy import select

from bot.data.loader import rt
from bot.db import User
from bot.db.models import Upper
from bot.locales import ExampleAdminConfig
from bot.locales.en.text import admin as text_en
from bot.locales.ru.text import admin as text_ru
from bot.middlewares.session_middleware import SessionMiddleware
from bot.utils.adminka import AdminIs


@rt.message(Command('view_stat'), AdminIs())
@rt.message(F.text == text_ru.btn_show_stat, AdminIs())
@rt.message(F.text == text_en.btn_show_stat, AdminIs())
async def stat_message(message: Message, state: FSMContext, locale: ExampleAdminConfig,
                       sessions: SessionMiddleware):
    await state.clear()

    now = datetime.now(timezone('Europe/Moscow'))
    date_today = datetime(now.year, now.month, now.day, 0, 0, 0)
    date_week = datetime(now.year, now.month, now.day - now.weekday(), 0, 0, 0)
    date_month = datetime(now.year, now.month, 1, 0, 0, 0)

    users_today = (await sessions.bot.execute(select(User).where(date_today <= User.date))).scalars().fetchall()
    users_week = (await sessions.bot.execute(select(User).where(date_week <= User.date))).scalars().fetchall()
    users_month = (await sessions.bot.execute(select(User).where(date_month <= User.date))).scalars().fetchall()
    users_all = (await sessions.bot.execute(select(User))).scalars().fetchall()

    upper_today = (await sessions.bot.execute(select(Upper).where(date_today <= Upper.date))).scalars()
    upper_week = (await sessions.bot.execute(select(Upper).where(date_week <= Upper.date))).scalars()
    upper_month = (await sessions.bot.execute(select(Upper).where(date_month <= Upper.date))).scalars()
    upper_all = (await sessions.bot.execute(select(Upper))).scalars()

    await message.answer(
        locale.stat.format(len(users_today), len(users_week), len(users_month), len(users_all),
                           sum([_.price for _ in upper_today]), sum([_.price for _ in upper_week]),
                           sum([_.price for _ in upper_month]), sum([_.price for _ in upper_all])))
