from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from bot.utils.log import get_logger
import logging
from sqlalchemy import select

from bot.data.loader import rt, bot
from bot.db import User
from bot.handlers.admin.start import AdminState
from bot.locales import ExampleAdminConfig
from bot.middlewares.session_middleware import SessionMiddleware
from bot.utils.adminka import AdminIs
from bot.utils.common import ButtonCallbackFactory
from bot.utils.keyboards import create_markup

from bot.locales.ru.text import admin as text_ru
from bot.locales.en.text import admin as text_en


@rt.message(Command('mailing'), AdminIs())
@rt.message(F.text == text_ru.btn_mailing, AdminIs())
@rt.message(F.text == text_en.btn_mailing, AdminIs())
async def mailing_message(message: Message, state: FSMContext, locale: ExampleAdminConfig):
    await state.clear()
    markup = await create_markup('inline', [[
        [locale.inline_mail_with_btn, ButtonCallbackFactory(status=2).pack()],
        [locale.inline_mail_without_btn, ButtonCallbackFactory(status=1).pack()]]])
    await message.answer(locale.mailing_with_btn, reply_markup=markup)


@rt.callback_query(ButtonCallbackFactory.filter(1 <= F.status <= 2), AdminIs())
async def btn_callback(query: CallbackQuery, callback_data: ButtonCallbackFactory, state: FSMContext,
                       locale: ExampleAdminConfig):
    await state.update_data(btn=callback_data.status - 1)
    if callback_data.status - 1:
        await state.set_state(AdminState.btn_with)
        await query.message.edit_text(locale.mailing_markup)
    else:
        await state.set_state(AdminState.message_mail)
        await query.message.edit_text(locale.mailing_text)


@rt.message(AdminState.btn_with, AdminIs())
async def btn_with_message(message: Message, state: FSMContext, locale: ExampleAdminConfig):
    try:
        l1st = []
        for i in message.text.split('\n'):
            _ = []
            for j in i.split(' '):
                x, z = j.split('::')
                _.append([x[1:], z[:-1]])
            l1st.append(_)
        await state.update_data(l1st=l1st)
        await state.set_state(AdminState.message_mail)
        await message.answer(locale.mailing_text)
    except Exception:
        await message.delete()


@rt.message(AdminState.message_mail, AdminIs())
async def message_mail_message(message: Message, state: FSMContext, locale: ExampleAdminConfig):
    await state.update_data(text=message.html_text)
    if message.photo:
        await state.update_data(doc='photo')
        await state.update_data(photo=message.photo[0].file_id)
    elif message.video:
        await state.update_data(doc='video')
        await state.update_data(video=message.video.file_id)
    else:
        await state.update_data(doc=None)

    markup = await create_markup('inline', [[['Да', ButtonCallbackFactory(status=3).pack()]]])
    await message.answer(locale.mailing_check, reply_markup=markup)

    data = await state.get_data()
    markup = await create_markup('inline', data['l1st']) if data['btn'] else None
    match data['doc']:
        case 'photo':
            await message.answer_photo(data['photo'], caption=data['text'], reply_markup=markup)
        case 'video':
            await message.answer_video(data['video'], caption=data['text'], reply_markup=markup)
        case _:
            await message.answer(data['text'], reply_markup=markup)
    await state.set_state(AdminState.check_mail)


@rt.callback_query(ButtonCallbackFactory.filter(F.status == 3), AdminIs(), AdminState.check_mail)
async def check_mail_callback(query: CallbackQuery, sessions: SessionMiddleware, state: FSMContext,
                              locale: ExampleAdminConfig):
    data = await state.get_data()
    markup = await create_markup('inline', data['l1st']) if data['btn'] else None
    await state.clear()
    users = (await sessions.bot.execute(select(User).where(User.dead == False))).scalars()
    result = {"ok": 0, "dead": 0}
    for user_ in users:
        try:
            if data['doc']:
                if data['doc'] == 'photo':
                    await bot.send_photo(user_.id, data['photo'], caption=data['text'], reply_markup=markup)
                elif data['doc'] == 'video':
                    await bot.send_video(user_.id, data['video'], caption=data['text'], reply_markup=markup)
            else:
                await bot.send_message(user_.id, data['text'], reply_markup=markup)
            result['ok'] += 1
        except Exception:
            user_.dead = True
            result['dead'] += 1
    await sessions.bot.commit()

    get_logger('bot')
    logging.info(f'mailing <admin: id={query.from_user.id}, username={query.from_user.username}> '
                 f'ok={result['ok']}, dead={result['dead']}')

    await query.answer(locale.mailing_finish)
    await query.message.answer(locale.mailing_stat.format(result['ok'], result['dead']))
