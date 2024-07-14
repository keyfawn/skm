from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.data.loader import rt
from bot.locales import ExampleUserConfig
from bot.locales.en.text import user as text_en
from bot.locales.ru.text import user as text_ru


@rt.message(Command('about'))
@rt.message(F.text == text_ru.btn_about)
@rt.message(F.text == text_en.btn_about)
async def about_message(message: Message, state: FSMContext, locale: ExampleUserConfig):
    await state.clear()
    await message.answer(locale.about)
