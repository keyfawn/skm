from random import randrange

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bot.utils.log import get_logger
import logging
from sqlalchemy import select

from bot.db.models import Products, Mailing
from bot.handlers.admin.auto_mailing import auto_mailing
from bot.middlewares import Engines
from bot.middlewares.session_middleware import SessionMiddleware


async def reset_fake_count(engine: SessionMiddleware):
    products = (await engine.bot.execute(select(Products))).scalars()
    for product in products:
        product.fake_count = product.count

    await engine.bot.commit()


async def every_hour_deficit(engine: SessionMiddleware):
    products = (await engine.bot.execute(select(Products))).scalars()
    for product in products:
        proz = randrange(1, 4) / 100
        minus = int(product.count * proz)

        if product.fake_count - minus >= 0 and minus:
            product.fake_count -= minus
        elif product.fake_count - 1 >= 0:
            product.fake_count -= 1

    await engine.bot.commit()


async def set_auto_mailing(id_: int, engine: SessionMiddleware, scheduler: AsyncIOScheduler):
    mail: Mailing = (await engine.bot.execute(select(Mailing).where(Mailing.id == id_))).scalar()
    sch = scheduler.add_job(auto_mailing, 'cron', hour=str(mail.date.hour), minute=str(mail.date.minute),
                            args=[engine, mail.id])
    mail.schedule_id = sch.id
    await engine.bot.commit()


async def delete_auto_mailing(id_: int, engine: SessionMiddleware, scheduler: AsyncIOScheduler):
    mail: Mailing = (await engine.bot.execute(select(Mailing).where(Mailing.id == id_))).scalar()
    scheduler.remove_job(mail.schedule_id)
    await engine.bot.delete(mail)
    await engine.bot.commit()


async def set_tasks(scheduler: AsyncIOScheduler, engine: Engines):
    async with engine.bot as session:
        scheduler.add_job(reset_fake_count, 'cron', hour='1', args=[SessionMiddleware(session=session)])
        scheduler.add_job(every_hour_deficit, 'interval', minutes=30, args=[SessionMiddleware(session=session)])

        mails: list[Mailing] = (await session.execute(select(Mailing))).scalars()
        for mail in mails:
            await set_auto_mailing(mail.id, SessionMiddleware(session=session), scheduler)

        get_logger('bot')
        logging.info('set tasks scheduler')
