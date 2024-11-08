from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from settings.special_func import get_bot_token


# Объект бота
# Для записей с типом Secret* необходимо
# вызывать метод get_secret_value(),
# чтобы получить настоящее содержимое вместо '*******'
default = DefaultBotProperties(parse_mode=ParseMode.HTML)
bot = Bot(token=get_bot_token(), default=default)

# Диспетчер
dp = Dispatcher()
