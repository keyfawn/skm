from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from sqlalchemy import select

from bot.data.loader import rt
from bot.db import User
from bot.locales import ExampleAdminConfig
from bot.locales.en.text import admin as text_en
from bot.locales.ru.text import admin as text_ru
from bot.middlewares.session_middleware import SessionMiddleware
from bot.utils.adminka import AdminIs
from bot.utils.keyboards import create_markup


class AdminState(StatesGroup):
    balance = State()

    new_product_photo = State()
    new_product_title = State()
    new_product_desc = State()
    new_product_price = State()
    new_product_count = State()

    btn_with = State()
    message_mail = State()
    check_mail = State()

    auto_btn_with = State()
    auto_message_mail = State()
    auto_check_mail = State()
    auto_mail_time = State()

    balance_user = State()


@rt.message(CommandStart(), AdminIs())
async def cmd_start(message: Message, state: FSMContext, locale: ExampleAdminConfig):
    await state.clear()
    markup = await create_markup('reply', [[[locale.btn_show_stat]],
                                           [[locale.btn_users]],
                                           [[locale.btn_mailing], [locale.btn_auto_mailing]],
                                           [[locale.btn_products]]],
                                 input_field_placeholder=locale.admin_panel)
    await message.answer(locale.start.format(message.from_user.first_name), reply_markup=markup)


@rt.message(Command('ru'), AdminIs())
async def set_ru_locale(message: Message, state: FSMContext, locale, sessions: SessionMiddleware):
    await state.clear()
    me: User = (await sessions.bot.execute(select(User).where(User.id == message.from_user.id))).scalar_one()
    me.locale = 'ru'
    await sessions.bot.commit()
    await message.answer(locale.ru_locale)
    await cmd_start(message, state, text_ru)


@rt.message(Command('en'), AdminIs())
async def set_en_locale(message: Message, state: FSMContext, locale, sessions: SessionMiddleware):
    await state.clear()
    me: User = (await sessions.bot.execute(select(User).where(User.id == message.from_user.id))).scalar_one()
    me.locale = 'en'
    await sessions.bot.commit()
    await message.answer(locale.en_locale)
    await cmd_start(message, state, text_en)
