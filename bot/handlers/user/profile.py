from base64 import b64encode

import aiohttp
from aiocryptopay.const import Assets
from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from sqlalchemy import select

from bot.data.loader import rt, crypto
from bot.data.config import epai_id
from bot.db.models import User, Products, Upper
from bot.handlers.user.start import UserState
from bot.locales import ExampleUserConfig
from bot.locales.en.text import user as text_en
from bot.locales.ru.text import user as text_ru
from bot.middlewares.session_middleware import SessionMiddleware
from bot.utils.common import SideProductCallbackFactory, SideProductStatus, BalanceUserCallbackFactory, \
    MethodBalanceCallbackFactory, MethodStatus
from bot.utils.keyboards import create_markup


@rt.message(Command('profile'))
@rt.message(F.text == text_ru.btn_profile)
@rt.message(F.text == text_en.btn_profile)
async def profile_message(message: Message, state: FSMContext, locale: ExampleUserConfig,
                          sessions: SessionMiddleware):
    await state.clear()
    user: User = (await sessions.bot.execute(select(User).where(User.id == message.from_user.id))).scalar_one()
    markup = await create_markup("inline", [
        [[locale.inline_balance, BalanceUserCallbackFactory(id=message.from_user.id).pack()]]])
    await message.answer(locale.profile.format(user.id, user.locale, user.date, user.balance),
                         reply_markup=markup)


@rt.callback_query(BalanceUserCallbackFactory.filter(F.id))
async def balance_callback(query: CallbackQuery, locale: ExampleUserConfig):
    markup = await create_markup("inline", [
        [['Crypto', MethodBalanceCallbackFactory(method=MethodStatus.crypto).pack()]],
        [['E-pay', MethodBalanceCallbackFactory(method=MethodStatus.epay).pack()]]
    ])
    await query.message.edit_text(locale.method_balance, reply_markup=markup)


@rt.callback_query(MethodBalanceCallbackFactory.filter(F.method == MethodStatus.crypto))
async def crypto_method_callback(query: CallbackQuery, locale: ExampleUserConfig, state: FSMContext,):
    await state.set_state(UserState.crypto_method)
    await query.message.edit_text(locale.crypto_method)


@rt.callback_query(MethodBalanceCallbackFactory.filter(F.method == MethodStatus.epay))
async def epay_method_callback(query: CallbackQuery, locale: ExampleUserConfig, state: FSMContext,):
    await state.set_state(UserState.epay_method)
    await query.message.edit_text(locale.epay_method)


@rt.message(F.text.isdigit(), UserState.crypto_method)
async def crypto_method_message(message: Message, locale: ExampleUserConfig, ):
    if int(message.text) >= 1:
        check = await crypto.create_invoice(amount=int(message.text),
                                            payload=f'{message.from_user.id}',
                                            asset=Assets.USDT,
                                            expires_in=60*5)
        markup = await create_markup("inline", [
            [[locale.inline_pay_balance, check.bot_invoice_url]]
        ])
        await message.answer(locale.pay_balance, reply_markup=markup)
    else:
        await message.delete()


@rt.message(F.text.isdigit(), UserState.epay_method)
async def epay_method_message(message: Message, locale: ExampleUserConfig, sessions: SessionMiddleware):
    if int(message.text) >= 300:
        data = f"api_key={epai_id}&amount={message.text}&merch={message.from_user.id}"
        # data = f"api_key={EPAY_TOKEN}&amount={message.text}"
        message_bytes = data.encode('ascii')
        base64_bytes = b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')

        markup = await create_markup("inline", [
            [[locale.inline_pay_balance, f'https://t.me/epayapibot?start={base64_message}']]
            # [[locale.inline_pay_balance, f'https://morepaymentss.click/api/telegram/sbp/?start={base64_message}']]
        ])
        await message.answer(locale.pay_balance, reply_markup=markup)
    else:
        await message.delete()
