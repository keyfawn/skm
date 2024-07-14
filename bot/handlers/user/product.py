from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from sqlalchemy import select

from bot.data.loader import rt
from bot.db.models import User, Products
from bot.locales import ExampleUserConfig
from bot.locales.en.text import user as text_en
from bot.locales.ru.text import user as text_ru
from bot.middlewares.session_middleware import SessionMiddleware
from bot.utils.common import SideProductCallbackFactory, SideProductStatus
from bot.utils.keyboards import create_markup


@rt.message(Command('products'))
@rt.message(F.text == text_ru.btn_products)
@rt.message(F.text == text_en.btn_products)
async def products_message(message: Message, state: FSMContext, locale: ExampleUserConfig,
                           sessions: SessionMiddleware):
    await state.clear()
    user: User = (await sessions.bot.execute(select(User).where(User.id == message.from_user.id))).scalar_one()
    products: list[Products] = (
        await sessions.bot.execute(select(Products).where(Products.price > user.balance))).scalars().fetchall()
    if products:
        product = products[0]
        markup = await create_markup('inline', [
            [['<-', SideProductCallbackFactory(status=SideProductStatus.left, product_id=product.id).pack()],
             [locale.inline_product_buy,
              SideProductCallbackFactory(status=SideProductStatus.buy, product_id=product.id).pack()],
             ['->', SideProductCallbackFactory(status=SideProductStatus.right, product_id=product.id).pack()], ]
        ])
        await message.answer_photo(
            product.photo,
            locale.product.format(product.title, product.desc, product.price, product.fake_count),
            reply_markup=markup
        )
    else:
        await message.answer(locale.non_product)


@rt.callback_query(SideProductCallbackFactory.filter(F.status == SideProductStatus.buy))
async def buy_product_callback(query: CallbackQuery, locale: ExampleUserConfig):
    await query.answer(locale.small_balance)


@rt.callback_query(SideProductCallbackFactory.filter(F.status == SideProductStatus.left))
async def left_product_callback(query: CallbackQuery, locale: ExampleUserConfig,
                               callback_data: SideProductCallbackFactory, sessions: SessionMiddleware):
    user: User = (await sessions.bot.execute(select(User).where(User.id == query.from_user.id))).scalar_one()
    products: list[Products] = (await sessions.bot.execute(select(Products).where(
        Products.price > user.balance, Products.id < callback_data.product_id
    ))).scalars().fetchall()
    if products:
        product = products[0]
        markup = await create_markup('inline', [
            [['<-', SideProductCallbackFactory(status=SideProductStatus.left, product_id=product.id).pack()],
             [locale.inline_product_buy,
              SideProductCallbackFactory(status=SideProductStatus.buy, product_id=product.id).pack()],
             ['->', SideProductCallbackFactory(status=SideProductStatus.right, product_id=product.id).pack()], ]
        ])
        await query.message.edit_media(
            InputMediaPhoto(media=product.photo,
                            caption=locale.product.format(
                                product.title, product.desc, product.price, product.fake_count)),
            reply_markup=markup
        )
    else:
        await query.answer(locale.product_end)


@rt.callback_query(SideProductCallbackFactory.filter(F.status == SideProductStatus.right))
async def right_product_callback(query: CallbackQuery, locale: ExampleUserConfig,
                               callback_data: SideProductCallbackFactory, sessions: SessionMiddleware):
    user: User = (await sessions.bot.execute(select(User).where(User.id == query.from_user.id))).scalar_one()
    products: list[Products] = (await sessions.bot.execute(select(Products).where(
        Products.price > user.balance, Products.id > callback_data.product_id
    ))).scalars().fetchall()
    if products:
        product = products[0]
        markup = await create_markup('inline', [
            [['<-', SideProductCallbackFactory(status=SideProductStatus.left, product_id=product.id).pack()],
             [locale.inline_product_buy,
              SideProductCallbackFactory(status=SideProductStatus.buy, product_id=product.id).pack()],
             ['->', SideProductCallbackFactory(status=SideProductStatus.right, product_id=product.id).pack()], ]
        ])
        await query.message.edit_media(
            InputMediaPhoto(media=product.photo,
                            caption=locale.product.format(
                                product.title, product.desc, product.price, product.fake_count)),
            reply_markup=markup
        )
    else:
        await query.answer(locale.product_end)
