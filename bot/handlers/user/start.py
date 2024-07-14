from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from sqlalchemy import select

from bot.data.loader import rt
from bot.db import User
from bot.locales import ExampleUserConfig
from bot.locales.en.text import user as text_en
from bot.locales.ru.text import user as text_ru
from bot.middlewares.session_middleware import SessionMiddleware
from bot.utils.keyboards import create_markup


class UserState(StatesGroup):
    balance = State()

    crypto_method = State()
    epay_method = State()


@rt.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, locale: ExampleUserConfig):
    await state.clear()
    markup = await create_markup('reply', [[[locale.btn_products]],
                                           [[locale.btn_shopping], [locale.btn_profile]],
                                           [[locale.btn_about]]])
    await message.answer(locale.start.format(message.from_user.first_name), reply_markup=markup)


@rt.message(Command('ru'))
async def set_ru_locale(message: Message, state: FSMContext, locale, sessions: SessionMiddleware):
    await state.clear()
    me: User = (await sessions.bot.execute(select(User).where(User.id == message.from_user.id))).scalar_one()
    me.locale = 'ru'
    await sessions.bot.commit()
    await message.answer(locale.ru_locale)
    await cmd_start(message, state, text_ru)


@rt.message(Command('en'))
async def set_en_locale(message: Message, state: FSMContext, locale, sessions: SessionMiddleware):
    await state.clear()
    me: User = (await sessions.bot.execute(select(User).where(User.id == message.from_user.id))).scalar_one()
    me.locale = 'en'
    await sessions.bot.commit()
    await message.answer(locale.en_locale)
    await cmd_start(message, state, text_en)
