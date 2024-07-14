import logging
import os

from bot.utils.log import get_logger
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine

from bot.db.models import Base


async def run_tables(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    get_logger('bot')
    logging.info('create tables')


class Engine:
    """Engine for get his"""
    def __init__(self, path):
        if not os.path.isdir('db'):
            os.mkdir('db')
        self.engine = create_async_engine(url=path)

    def get_engine(self):
        return self.engine
