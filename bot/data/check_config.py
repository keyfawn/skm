from bot.utils.log import get_logger
import logging

from bot.data.config import admins_id, url_ngrok, epai_id
from bot.data.config import _raise
import validators


async def check_config():
    if type(admins_id) is not list:
        _raise("admins_id is not a list[int]")
    if any([type(x) is not int for x in admins_id]):
        _raise("admins_id is not a list[int]")

    if type(epai_id) is not int:
        _raise("epai_id is not a int")

    if not validators.url(url_ngrok):
        _raise("url_ngrok invalid url")

    get_logger('bot')
    logging.info('Config check complete')
