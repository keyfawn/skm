from aiogram import Bot
from aiogram.types import BotCommandScopeAllPrivateChats, BotCommand, BotCommandScopeChat
from bot.utils.log import get_logger
import logging

from bot.data.config import admins_id


async def set_ui_commands(bot: Bot):
    """set commands for users"""
    await bot.set_my_commands(
        commands=[
            BotCommand(command="start", description="Start bot"),
            BotCommand(command="products", description="Products"),
            BotCommand(command="shopping", description="Shopping"),
            BotCommand(command="profile", description="Profile"),
            BotCommand(command="about", description="About us"),
            BotCommand(command='ru', description='set the Russian language'),
            BotCommand(command='en', description='set the English language'),
        ],
        scope=BotCommandScopeAllPrivateChats())
    get_logger('bot')
    logging.info('set ui commands for users')


async def set_admin_ui_commands(bot: Bot):
    """set commands for admins"""
    for _ in admins_id:
        await bot.set_my_commands(
            [
                BotCommand(command='start', description='Start bot'),
                BotCommand(command='view_stat', description='View statistics'),
                BotCommand(command='users', description='Users'),
                BotCommand(command='mailing', description='Mailing'),
                BotCommand(command='auto_mailing', description='Auto-mailing'),
                BotCommand(command='products', description='Products'),
                BotCommand(command='ru', description='set the Russian language'),
                BotCommand(command='en', description='set the English language'),
            ],
            scope=BotCommandScopeChat(chat_id=_))
    get_logger('bot')
    logging.info('set ui commands for admins')
