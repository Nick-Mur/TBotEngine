from settings.config_reader import config

from text.phrases.ru_phrases.phrases_0.phrases import *
from text.buttons.buttons_0 import *
from text.media.media_0 import *
from text.keyboards.keyboards_0 import *
from text.messages.messages_0 import *


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
