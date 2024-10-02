from settings.config_reader import config

from text.phrases.ru_phrases.phrases_0 import *
from text.buttons.buttons_0 import *
from text.media.media_0 import *
from text.keyboards.keyboards_0 import *
from text.messages.messages_0 import *

from text.phrases.ru_phrases.phrases_1 import *
from text.media.media_1 import *
from text.messages.messages_1 import *


def get_bot_token():
    return config.bot_token.get_secret_value()


def get_webhook_host():
    return config.webhook_host.get_secret_value()


async def return_variable(value):
    if value in globals():
        return globals()[value]
    else:
        return None
