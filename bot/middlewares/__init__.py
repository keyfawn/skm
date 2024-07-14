from aiogram import Router
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.middlewares.session_middleware import DbSessionMiddleware, Engines
from bot.middlewares.rate_middleware import ThrottlingMiddleware
from bot.middlewares.schedule_middleware import SchedulerMiddleware


async def reg_middlewares(rt: Router, eng: Engines, scheduler: AsyncIOScheduler):
    rt.message.outer_middleware(DbSessionMiddleware(session_pool=eng))
    rt.callback_query.outer_middleware(DbSessionMiddleware(session_pool=eng))

    rt.message.outer_middleware(SchedulerMiddleware(scheduler=scheduler))
    rt.callback_query.outer_middleware(SchedulerMiddleware(scheduler=scheduler))

    rt.message.middleware(ThrottlingMiddleware())
    rt.callback_query.middleware(ThrottlingMiddleware())
