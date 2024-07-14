from datetime import time

from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bot.utils.log import get_logger
import logging
from sqlalchemy import select

from bot.data.config import admins_id
from bot.data.loader import rt, bot
from bot.db import User
from bot.db.models import Mailing
from bot.handlers.admin.start import AdminState
from bot.locales import ExampleAdminConfig
from bot.middlewares.session_middleware import SessionMiddleware
from bot.utils.adminka import AdminIs
from bot.utils.common import ButtonCallbackFactory, AutoMailingCallbackFactory, AutoMailingStatusFactory, \
    AutoMailingStatus, DeleteAutoMailingCallbackFactory, AutoButtonCallbackFactory
from bot.utils.keyboards import create_markup

from bot.locales.ru.text import admin as text_ru
from bot.locales.en.text import admin as text_en


@rt.message(Command('auto_mailing'), AdminIs())
@rt.message(F.text == text_ru.btn_auto_mailing, AdminIs())
@rt.message(F.text == text_en.btn_auto_mailing, AdminIs())
async def auto_mailing_message(message: Message, state: FSMContext, locale: ExampleAdminConfig,
                               sessions: SessionMiddleware, cancel: bool = False):
    await state.clear()
    auto_mails = (await sessions.bot.execute(select(Mailing))).scalars()
    markup = await create_markup('inline', [
        *[[[locale.inline_auto_mail.format(auto_mail.id), AutoMailingCallbackFactory(id=auto_mail.id).pack()]]
          for auto_mail in auto_mails],
        [[locale.inline_auto_mail_add, AutoMailingStatusFactory(status=AutoMailingStatus.add).pack()]]
    ])
    if cancel:
        if message.photo:
            await message.delete()
            await message.answer(locale.auto_mailing, reply_markup=markup)
        elif message.video:
            await message.delete()
            await message.answer(locale.auto_mailing, reply_markup=markup)
        else:
            await message.edit_text(locale.auto_mailing, reply_markup=markup)
    else:
        await message.answer(locale.auto_mailing, reply_markup=markup)


@rt.callback_query(AutoMailingCallbackFactory.filter(F.id), AdminIs())
async def auto_mail_callback(query: CallbackQuery, locale: ExampleAdminConfig,
                             sessions: SessionMiddleware, callback_data: AutoMailingCallbackFactory):
    auto_mail: Mailing = (await sessions.bot.execute(select(Mailing).where(Mailing.id == callback_data.id))).scalar()

    l1st = []
    if auto_mail.markup:
        for i in auto_mail.markup.split('\n'):
            _ = []
            for j in i.split(' '):
                x, z = j.split('::')
                _.append([x[1:], z[:-1]])
            l1st.append(_)
    l1st.append([[locale.inline_auto_mail_delete, DeleteAutoMailingCallbackFactory(id=auto_mail.id).pack()]])
    l1st.append([[locale.inline_auto_mail_cancel, AutoMailingStatusFactory(status=AutoMailingStatus.cancel).pack()]])
    markup = await create_markup('inline', l1st) if l1st else None

    text = locale.auto_mail.format(auto_mail.id, auto_mail.text, auto_mail.date.hour, auto_mail.date.minute)

    if auto_mail.photo:
        await query.message.delete()
        await query.message.answer_photo(auto_mail.photo, caption=text, reply_markup=markup)
    if auto_mail.video:
        await query.message.delete()
        await query.message.answer_video(auto_mail.video, caption=text, reply_markup=markup)
    else:
        try:
            await query.message.edit_text(text, reply_markup=markup)
        except Exception:
            ...


@rt.callback_query(DeleteAutoMailingCallbackFactory.filter(F.id), AdminIs())
async def delete_auto_mail_callback(query: CallbackQuery, locale: ExampleAdminConfig,
                                    callback_data: DeleteAutoMailingCallbackFactory,
                                    sessions: SessionMiddleware):
    auto_mail: Mailing = (await sessions.bot.execute(select(Mailing).where(Mailing.id == callback_data.id))).scalar()
    await sessions.bot.delete(auto_mail)
    await sessions.bot.commit()
    markup = await create_markup('inline',
                                 [[[locale.inline_auto_mail_cancel,
                                    AutoMailingStatusFactory(status=AutoMailingStatus.cancel).pack()]]])
    await query.message.answer(locale.auto_mail_delete, reply_markup=markup)


@rt.callback_query(AutoMailingStatusFactory.filter(F.status == AutoMailingStatus.cancel), AdminIs())
async def cancel_auto_mail_callback(query: CallbackQuery, state: FSMContext, locale: ExampleAdminConfig,
                                    sessions: SessionMiddleware):
    await auto_mailing_message(query.message, state, locale, sessions, cancel=True)


@rt.callback_query(AutoMailingStatusFactory.filter(F.status == AutoMailingStatus.add), AdminIs())
async def add_auto_mail_callback(query: CallbackQuery, locale: ExampleAdminConfig, ):
    markup = await create_markup('inline', [[
        [locale.inline_mail_with_btn, AutoButtonCallbackFactory(status=2).pack()],
        [locale.inline_mail_without_btn, AutoButtonCallbackFactory(status=1).pack()]]])
    await query.message.answer(locale.mailing_with_btn, reply_markup=markup)


@rt.callback_query(AutoButtonCallbackFactory.filter(1 <= F.status <= 2), AdminIs())
async def auto_btn_callback(query: CallbackQuery, callback_data: ButtonCallbackFactory, state: FSMContext,
                            locale: ExampleAdminConfig):
    await state.update_data(btn=callback_data.status - 1)
    if callback_data.status - 1:
        await state.set_state(AdminState.auto_btn_with)
        await query.message.edit_text(locale.mailing_markup)
    else:
        await state.set_state(AdminState.auto_message_mail)
        await query.message.edit_text(locale.mailing_text)


@rt.message(AdminState.auto_btn_with, AdminIs())
async def auto_btn_with_message(message: Message, state: FSMContext, locale: ExampleAdminConfig):
    try:
        l1st = []
        for i in message.text.split('\n'):
            _ = []
            for j in i.split(' '):
                x, z = j.split('::')
                _.append([x[1:], z[:-1]])
            l1st.append(_)
        await state.update_data(l1st=l1st, non_work_markup=message.text)
        await state.set_state(AdminState.auto_message_mail)
        await message.answer(locale.mailing_text)
    except Exception:
        await message.delete()


@rt.message(AdminState.auto_message_mail, AdminIs())
async def auto_message_mail_message(message: Message, state: FSMContext, locale: ExampleAdminConfig):
    await state.update_data(text=message.html_text)
    if message.photo:
        await state.update_data(doc='photo')
        await state.update_data(photo=message.photo[0].file_id)
    elif message.video:
        await state.update_data(doc='video')
        await state.update_data(video=message.video.file_id)
    else:
        await state.update_data(doc=None)

    await state.set_state(AdminState.auto_mail_time)
    await message.answer(locale.auto_mail_add_time)


@rt.message(AdminState.auto_mail_time, AdminIs())
async def auto_mail_time_message(message: Message, state: FSMContext, locale: ExampleAdminConfig):
    try:
        hour, minute = [int(_) for _ in message.text.split(":")]
        await state.update_data(hour=hour, minute=minute)

        markup = await create_markup('inline', [[[locale.inline_yes, AutoButtonCallbackFactory(status=3).pack()]]])
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
        await state.set_state(AdminState.auto_check_mail)
    except Exception:
        await message.delete()


@rt.callback_query(AutoButtonCallbackFactory.filter(F.status == 3), AdminIs(), AdminState.auto_check_mail)
async def auto_check_mail_callback(query: CallbackQuery, sessions: SessionMiddleware, state: FSMContext,
                                   locale: ExampleAdminConfig, scheduler: AsyncIOScheduler):
    get_logger('bot')
    logging.info(f'new auto-mailing <admin: id={query.from_user.id}, username={query.from_user.username}>')

    data = await state.get_data()
    await state.clear()
    auto_mail = Mailing(
        text=data['text'],
        photo=data['photo'] if data.get('photo') else None,
        video=data['video'] if data.get('video') else None,
        markup=data['non_work_markup'] if data.get('non_work_markup') else None,
        date=time(hour=data['hour'], minute=data['minute']),
    )
    sessions.bot.add(auto_mail)
    await sessions.bot.commit()

    from bot.utils.sched import set_auto_mailing
    await set_auto_mailing(auto_mail.id, sessions, scheduler)

    await query.message.answer(locale.auto_mailing_finish)


async def get_locale(sessions: SessionMiddleware, user_id: int) -> ExampleAdminConfig:
    admin: User = (await sessions.bot.execute(select(User).where(User.id == user_id))).scalar()
    match admin.locale:
        case "ru":
            from bot.locales.ru import text
            return text.admin
        case "en":
            from bot.locales.en import text
            return text.admin


async def auto_mailing(sessions: SessionMiddleware, id_: int):
    users = (await sessions.bot.execute(select(User).where(User.dead == False))).scalars()
    result = {"ok": 0, "dead": 0}
    data: Mailing = (await sessions.bot.execute(select(Mailing).where(Mailing.id == id_))).scalar()

    l1st = []
    if data.markup:
        for i in data.markup.split('\n'):
            _ = []
            for j in i.split(' '):
                x, z = j.split('::')
                _.append([x[1:], z[:-1]])
            l1st.append(_)
    markup = await create_markup("inline", l1st)

    for user_ in users:
        try:
            if data.photo:
                await bot.send_photo(user_.id, data.photo, caption=data.text, reply_markup=markup)
            elif data.video:
                await bot.send_video(user_.id, data.video, caption=data.text, reply_markup=markup)
            else:
                await bot.send_message(user_.id, data.text, reply_markup=markup)
            result['ok'] += 1
        except Exception:
            user_.dead = True
            result['dead'] += 1
    await sessions.bot.commit()

    get_logger('bot')
    logging.info(f'<auto-mailing: id={data.id}, time={data.date.hour}:{data.date.minute}, ok={result["ok"]}, '
                 f'dead={result["dead"]}>')

    for admin in admins_id:
        await bot.send_message(admin, (await get_locale(sessions, admin)).mailing_finish)
        await bot.send_message(admin,
                               (await get_locale(sessions, admin)).mailing_stat.format(result['ok'], result['dead']))
