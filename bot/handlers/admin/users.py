from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from bot.utils.log import get_logger
import logging
from sqlalchemy import select

from bot.data.loader import rt
from bot.db import User
from bot.handlers.admin.start import AdminState
from bot.locales import ExampleAdminConfig
from bot.middlewares.session_middleware import SessionMiddleware
from bot.utils.adminka import AdminIs
from bot.utils.common import UserCallbackFactory, UserStatusCallbackFactory, UserStatus, BalanceUserCallbackFactory
from bot.utils.keyboards import create_markup

from bot.locales.ru.text import admin as text_ru
from bot.locales.en.text import admin as text_en


@rt.message(Command('users'), AdminIs())
@rt.message(F.text == text_ru.btn_users, AdminIs())
@rt.message(F.text == text_en.btn_users, AdminIs())
async def all_users_message(message: Message, state: FSMContext, locale: ExampleAdminConfig,
                            sessions: SessionMiddleware, cancel: bool = False):
    await state.clear()
    users = (await sessions.bot.execute(select(User))).scalars()
    markup = await create_markup('inline',
                                 [[[user.fullname, UserCallbackFactory(id=user.id).pack()]] for user in users])
    if cancel:
        await message.edit_text(locale.all_users, reply_markup=markup)
    else:
        await message.answer(locale.all_users, reply_markup=markup)


@rt.callback_query(UserCallbackFactory.filter(F.id), AdminIs())
async def user_callback(query: CallbackQuery, callback_data: UserCallbackFactory,
                        locale: ExampleAdminConfig, sessions: SessionMiddleware):
    user = (await sessions.bot.execute(select(User).where(User.id == callback_data.id))).scalar_one()
    markup = await create_markup('inline', [
        [[locale.inline_view_user, f'tg://user?id={user.id}', ':tg:']],
        [[locale.inline_balance_user, BalanceUserCallbackFactory(id=user.id).pack()]],
        [[locale.inline_auto_mail_cancel, UserStatusCallbackFactory(status=UserStatus.cancel).pack()]]])
    await query.message.edit_text(
        locale.user.format(user.id, user.username, user.fullname, user.locale, user.balance, user.date),
        reply_markup=markup)


@rt.callback_query(BalanceUserCallbackFactory.filter(F.id), AdminIs())
async def balance_user_callback(query: CallbackQuery, callback_data: UserCallbackFactory, state: FSMContext,
                                locale: ExampleAdminConfig):
    await state.update_data(balance_user=callback_data.id)
    await state.set_state(AdminState.balance_user)
    await query.message.edit_text(locale.balance_user)


@rt.message(F.text.isdigit(), AdminIs(), AdminState.balance_user)
async def balance_user_message(message: Message, state: FSMContext, locale: ExampleAdminConfig,
                               sessions: SessionMiddleware):
    user_id = (await state.get_data())['balance_user']
    user = (await sessions.bot.execute(select(User).where(User.id == user_id))).scalar_one()
    user.balance = int(message.text)
    await sessions.bot.commit()
    get_logger('new_upper')
    logging.info(f'add <balance: count={user.balance}, user_id={user_id}> '
                 f'<admin: id={message.from_user.id}, username={message.from_user.username}>')
    markup = await create_markup("inline", [[['Назад', UserCallbackFactory(id=user.id).pack()]]])
    await message.answer(locale.balance_user_ok, reply_markup=markup)


@rt.callback_query(UserStatusCallbackFactory.filter(F.status == UserStatus.cancel), AdminIs())
async def cancel_user_callback(query: CallbackQuery, state: FSMContext,
                               sessions: SessionMiddleware, locale: ExampleAdminConfig):
    await all_users_message(query.message, state, locale, sessions, cancel=True)
