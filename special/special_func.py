from settings.config_reader import config

from text.phrases.ru_phrases import *
from text.buttons.ru_buttons import *
from text.media import *
from text.keyboards import *


async def get_payment_token():
    return config.payment_token.get_secret_value()


def get_bot_token():
    return config.bot_token.get_secret_value()


async def like(value):
    return f'%{value}%'


async def return_variable(value):
    if value in globals():
        return globals()[value]
    else:
        return None
