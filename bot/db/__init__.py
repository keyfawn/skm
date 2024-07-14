from sqlalchemy.ext.asyncio import async_sessionmaker

from bot.db.base import Base
from bot.db.create import Engine
from bot.db.models import User
from bot.middlewares import Engines


async def create_db(engine_users):
    session_maker = async_sessionmaker(engine_users.get_engine(), expire_on_commit=False)

    await create.run_tables(engine_users.get_engine())

    return Engines(session=session_maker)
