import json
import os

from betterconf.config import AbstractProvider
from dotenv import load_dotenv
from betterconf import Config as Con, field
from bot.utils.log import get_logger
import logging


def _raise(ex: str):
    get_logger('bot')
    logging.critical(ex)
    exit(1)


def get_config():
    class JSONProvider(AbstractProvider):
        SETTINGS_JSON_FILE = "config.json"

        def __init__(self):
            try:
                with open(self.SETTINGS_JSON_FILE, "r") as f:
                    self._settings = json.load(f)
            except Exception:
                self.SETTINGS_JSON_FILE = '../config.json'
                with open(self.SETTINGS_JSON_FILE, "r") as f:
                    self._settings = json.load(f)

        def get(self, name):
            return self._settings.get(name)

    provider = JSONProvider()

    class Config(Con):
        admins_id = field("admins_id", default=lambda: _raise('not found "admins_id" in config.json'),
                          provider=provider)
        url_ngrok = field("url_ngrok", default=lambda: _raise('not found "url_ngrok" in config.json'),
                          provider=provider)
        epai_id = field("epai_id", default=lambda: _raise('not found "epai_id" in config.json'),
                        provider=provider)

    return Config()


admins_id = get_config().admins_id
url_ngrok = get_config().url_ngrok
epai_id = get_config().epai_id

load_dotenv()
BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
CRYPTO_TOKEN = str(os.getenv("CRYPTO_TOKEN"))
EPAY_TOKEN = str(os.getenv("EPAY_TOKEN"))
NGROK_TOKEN = str(os.getenv("NGROK_TOKEN"))
