from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from bot.utils.log import get_logger
import logging
from sqlalchemy import select

from bot.data.loader import rt
from bot.db.models import Products
from bot.handlers.admin.start import AdminState
from bot.locales import ExampleAdminConfig
from bot.middlewares.session_middleware import SessionMiddleware
from bot.utils.adminka import AdminIs
from bot.utils.common import (ProductCallbackFactory, ProductStatusCallbackFactory, ProductStatus, ProductDelete,
                              NewProductAdd)
from bot.utils.keyboards import create_markup

from bot.locales.ru.text import admin as text_ru
from bot.locales.en.text import admin as text_en


@rt.message(Command('products'), AdminIs())
@rt.message(F.text == text_ru.btn_products, AdminIs())
@rt.message(F.text == text_en.btn_products, AdminIs())
async def all_product_message(message: Message, sessions: SessionMiddleware, state: FSMContext,
                              locale: ExampleAdminConfig, cancel: bool = False):
    await state.clear()
    products = (await sessions.bot.execute(select(Products))).scalars()
    markup = await create_markup('inline',
                                 [*[[[product.title, ProductCallbackFactory(id=product.id).pack()]]
                                    for product in products],
                                  [[locale.inline_product_new,
                                    ProductStatusCallbackFactory(status=ProductStatus.add).pack()]]])
    if cancel: await message.delete()
    await message.answer(locale.all_products, reply_markup=markup)


@rt.callback_query(ProductCallbackFactory.filter(F.id), AdminIs())
async def show_product_callback(query: CallbackQuery, callback_data: ProductCallbackFactory, locale: ExampleAdminConfig,
                                sessions: SessionMiddleware, state: FSMContext):
    product = (await sessions.bot.execute(select(Products).where(Products.id == callback_data.id))).scalar_one()
    await state.update_data(product=product.id)
    markup = await create_markup('inline', [[[locale.inline_auto_mail_delete,
                                              ProductStatusCallbackFactory(status=ProductStatus.delete).pack()]],
                                            [[locale.inline_auto_mail_cancel,
                                              ProductStatusCallbackFactory(status=ProductStatus.all_products).pack()]]])
    await query.message.delete()
    await query.message.answer_photo(product.photo,
                                     caption=locale.new_product_example.format(product.title, product.desc,
                                                                               product.price, product.count,
                                                                               product.fake_count),
                                     reply_markup=markup)


@rt.callback_query(ProductStatusCallbackFactory.filter(F.status == ProductStatus.all_products), AdminIs())
async def cancel_all_product(query: CallbackQuery, locale: ExampleAdminConfig, sessions: SessionMiddleware,
                             state: FSMContext):
    await all_product_message(query.message, sessions, state, locale, True)


@rt.callback_query(ProductStatusCallbackFactory.filter(F.status == ProductStatus.delete), AdminIs())
async def delete_product_callback(query: CallbackQuery, state: FSMContext, locale: ExampleAdminConfig):
    product_id = (await state.get_data())['product']
    markup = await create_markup('inline', [
        [[locale.inline_ok_delete, ProductDelete(id=product_id).pack()]],
        [[locale.inline_auto_mail_cancel, ProductStatusCallbackFactory(status=ProductStatus.all_products).pack()]]])
    await query.message.edit_caption(query.inline_message_id, locale.pre_delete_product.format(product_id),
                                     reply_markup=markup)


@rt.callback_query(ProductDelete.filter(F.id), AdminIs())
async def delete_pro_callback(query: CallbackQuery, callback_data: ProductDelete, sessions: SessionMiddleware,
                              locale: ExampleAdminConfig):
    product = (await sessions.bot.execute(select(Products).where(Products.id == callback_data.id))).scalar_one()
    await sessions.bot.delete(product)
    await sessions.bot.commit()
    await query.message.edit_caption(query.inline_message_id, locale.delete_product.format(callback_data.id))
    get_logger('bot')
    logging.info(f'delete <product: id={callback_data.id}> '
                 f'<admin: id={query.from_user.id}, username={query.from_user.username}>')


@rt.callback_query(ProductStatusCallbackFactory.filter(F.status == ProductStatus.add), AdminIs())
async def add_product_callback(query: CallbackQuery, state: FSMContext, locale: ExampleAdminConfig):
    await query.message.edit_text(locale.new_product_photo)
    await state.set_state(AdminState.new_product_photo)


@rt.message(F.photo, AdminState.new_product_photo, AdminIs())
async def new_product_photo_message(message: Message, state: FSMContext, locale: ExampleAdminConfig):
    await state.update_data(new_product_photo=message.photo[0].file_id)
    await message.answer(locale.new_product_title)
    await state.set_state(AdminState.new_product_title)


@rt.message(AdminState.new_product_title, AdminIs())
async def new_product_title_message(message: Message, state: FSMContext, locale: ExampleAdminConfig):
    await state.update_data(new_product_title=message.html_text)
    await message.answer(locale.new_product_desc)
    await state.set_state(AdminState.new_product_desc)


@rt.message(AdminState.new_product_desc, AdminIs())
async def new_product_desc_message(message: Message, state: FSMContext, locale: ExampleAdminConfig):
    await state.update_data(new_product_desc=message.html_text)
    await message.answer(locale.new_product_price)
    await state.set_state(AdminState.new_product_price)


@rt.message(AdminState.new_product_price, AdminIs(), F.text.isdigit())
async def new_product_price_message(message: Message, state: FSMContext, locale: ExampleAdminConfig):
    await state.update_data(new_product_price=int(message.text))
    await message.answer(locale.new_product_count)
    await state.set_state(AdminState.new_product_count)


@rt.message(AdminState.new_product_count, AdminIs(), F.text.isdigit())
async def new_product_count_message(message: Message, state: FSMContext, locale: ExampleAdminConfig):
    await state.update_data(new_product_count=int(message.text))
    data = await state.get_data()
    mess = await message.answer_photo(
        data['new_product_photo'],
        caption=locale.new_product_example.format(data['new_product_title'], data['new_product_desc'],
                                                  data['new_product_price'], data['new_product_count'],
                                                  data['new_product_count']))
    markup = await create_markup("inline", [
        [[locale.inline_add, NewProductAdd(title=data['new_product_title']).pack()]]])
    await mess.reply(locale.new_product_check, reply_markup=markup)


@rt.callback_query(NewProductAdd.filter(F.title), AdminIs())
async def new_product_add(query: CallbackQuery, locale: ExampleAdminConfig, sessions: SessionMiddleware,
                          state: FSMContext):
    data = await state.get_data()
    await state.clear()
    product = Products(photo=data['new_product_photo'],
                       title=data['new_product_title'],
                       desc=data['new_product_desc'],
                       price=data['new_product_price'],
                       count=data['new_product_count'],
                       fake_count=data['new_product_count'])
    sessions.bot.add(product)
    await sessions.bot.commit()
    await query.message.edit_text(locale.new_product_add)
    get_logger('bot')
    logging.info(f'add <product: id={product.id}> '
                 f'<admin: id={query.from_user.id}, username={query.from_user.username}>')
