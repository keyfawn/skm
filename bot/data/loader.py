from aiocryptopay import AioCryptoPay, Networks
from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.data.config import BOT_TOKEN, CRYPTO_TOKEN, _raise

rt = Router()

try:
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
except Exception:
    _raise('error with token of bot')

dp = Dispatcher()

scheduler = AsyncIOScheduler({'apscheduler.timezone': 'Europe/Moscow'})

try:
    crypto = AioCryptoPay(token=CRYPTO_TOKEN, network=Networks.TEST_NET)
except Exception:
    _raise('error with token of cryptopay')
