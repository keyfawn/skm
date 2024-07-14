import logging

import ngrok
import pendulum
import uvicorn
from fastapi import FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from bot.data.config import NGROK_TOKEN, CRYPTO_TOKEN, EPAY_TOKEN, url_ngrok, admins_id
from bot.data.loader import bot
from bot.db import User
from bot.db.models import Upper
from bot.utils.keyboards import create_markup
from bot.utils.log import get_logger

app = FastAPI()


@app.post(f"/crypto-{CRYPTO_TOKEN}")
async def crypto_webhook(update: dict):
    if update['payload']['status'] == 'paid':
        payment_amount = int((float(update['payload']['amount']) - float(update['payload']['fee'])) * 88)
        payment_user_id = int(update['payload']['payload'])

        engine_shop = create_async_engine(url='sqlite+aiosqlite:///db/bot.db')
        session_maker = async_sessionmaker(engine_shop, expire_on_commit=False)
        async with session_maker() as session:
            user: User = (await session.execute(select(User).where(User.id == payment_user_id))).scalar()
            upper = Upper(
                user_id=payment_user_id,
                price=payment_amount,
                date=pendulum.now('Europe/Moscow'),
                method='crypto'
            )
            session.add(upper)
            user.balance += payment_amount
            await session.commit()

            match user.locale:
                case "ru":
                    from bot.locales.ru import text
                    locale = text.user
                case _:
                    from bot.locales.en import text
                    locale = text.user

            await bot.send_message(chat_id=payment_user_id, text=locale.upper_balance.format(payment_amount))

            for admin in admins_id:
                admin_user: User = (await session.execute(select(User).where(User.id == admin))).scalar_one_or_none()
                if admin_user:
                    match admin_user.locale:
                        case "ru":
                            from bot.locales.ru import text
                            locale = text.admin
                        case _:
                            from bot.locales.en import text
                            locale = text.admin
                    markup = await create_markup("inline", [
                        [[locale.inline_view_user, f'tg://user?id={payment_user_id}', ":tg:"]]])
                    await bot.send_message(admin_user.id,
                                           locale.new_upper.format(payment_user_id, payment_amount),
                                           reply_markup=markup)

            get_logger('new_upper')
            logging.info(f'new <upper: amount={payment_amount}, user_id={payment_user_id}>')

    return 200


# @app.post(f"/epay-{EPAY_TOKEN}")
@app.post(f"/epay")
async def epay_webhook(update: dict):
    if update['status'] == 'successful_payment':
        payment_amount = int(update['amount_without_comission'])
        payment_user_id = int(update['merchant_order_id'])

        engine_shop = create_async_engine(url='sqlite+aiosqlite:///db/bot.db')
        session_maker = async_sessionmaker(engine_shop, expire_on_commit=False)
        async with session_maker() as session:
            user: User = (await session.execute(select(User).where(User.id == payment_user_id))).scalar()
            upper = Upper(
                user_id=payment_user_id,
                price=payment_amount,
                date=pendulum.now('Europe/Moscow'),
                method='epay'
            )
            session.add(upper)
            user.balance += payment_amount
            await session.commit()

            match user.locale:
                case "ru":
                    from bot.locales.ru import text
                    locale = text.user
                case _:
                    from bot.locales.en import text
                    locale = text.user

            await bot.send_message(chat_id=payment_user_id, text=locale.upper_balance.format(payment_amount))

            for admin in admins_id:
                admin_user: User = (await session.execute(select(User).where(User.id == admin))).scalar_one_or_none()
                if admin_user:
                    match admin_user.locale:
                        case "ru":
                            from bot.locales.ru import text
                            locale = text.admin
                        case _:
                            from bot.locales.en import text
                            locale = text.admin
                    markup = await create_markup("inline", [
                        [[locale.inline_view_user, f'tg://user?id={payment_user_id}', ":tg:"]]])
                    await bot.send_message(admin_user.id,
                                           locale.new_upper.format(payment_user_id, payment_amount),
                                           reply_markup=markup)

            get_logger('new_upper')
            logging.info(f'new <upper: amount={payment_amount}, user_id={payment_user_id}>')

    return 200


@app.get("/")
async def homepage():
    return "work"


def run():
    ngrok.set_auth_token(NGROK_TOKEN)
    listener = ngrok.forward("localhost:3001", domain=url_ngrok[8:])

    uvicorn.run(app, host="localhost", port=3001, loop="uvloop")
