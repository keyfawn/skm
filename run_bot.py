import asyncio
from bot.data.check_config import check_config
from bot.data.loader import bot, dp, scheduler
from bot.db import create_db, Engine
from bot.middlewares import reg_middlewares
from bot.utils.sched import set_tasks
from bot.utils.ui_commands import set_ui_commands, set_admin_ui_commands
from bot.utils.log import get_logger
import logging


engine = Engine('sqlite+aiosqlite:///db/bot.db')


async def main_bot():
    await check_config()

    from bot.handlers import rt
    eng = await create_db(engine_users=engine)
    await reg_middlewares(rt, eng, scheduler)

    await set_tasks(scheduler, eng)
    scheduler.start()

    dp.include_router(rt)

    await set_ui_commands(bot)
    await set_admin_ui_commands(bot)

    get_logger('bot')
    logging.info('Bot started')
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), handle_signals=False)


if __name__ == "__main__":
    try:
        asyncio.run(main_bot())
    except (KeyboardInterrupt, SystemExit):
        get_logger('bot')
        logging.info('Bot stopped')
