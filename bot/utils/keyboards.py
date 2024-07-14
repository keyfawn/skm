from aiogram.types import (KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton,
                           InlineKeyboardMarkup)
import validators


async def create_markup(tip, keyboard: list[list[list]],
                        input_field_placeholder: str = None) -> InlineKeyboardMarkup | ReplyKeyboardMarkup:
    """
    create markup
    :param input_field_placeholder: text for reply-markup
    :param tip: "inline" or "reply"
    :param keyboard: [ [ ["lol"] ] , [ ["as", "https://ya.ru"] , ["ooo", "tg://user?id=1234", ":tg:"] ] ]
    :return: markup
    """
    if tip == 'inline':
        markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=lvl2[0], url=lvl2[1])
                                                        if ":tg:" in lvl2 or validators.url(lvl2[1])
                                                        else InlineKeyboardButton(text=lvl2[0], callback_data=lvl2[1])
                                                        for lvl2 in lvl1] for lvl1 in keyboard])

    else:
        markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=lvl2[0]) for lvl2 in lvl1] for lvl1 in keyboard],
                                     resize_keyboard=True, input_field_placeholder=input_field_placeholder)
    return markup


async def remove_markup() -> ReplyKeyboardRemove:
    """delete reply-markup"""
    markup = ReplyKeyboardRemove()
    return markup
