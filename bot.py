from imports import *

# Объект бота
# Для записей с типом Secret* необходимо
# вызывать метод get_secret_value(),
# чтобы получить настоящее содержимое вместо '*******'
default = DefaultBotProperties(parse_mode=ParseMode.HTML)
bot = Bot(token=get_bot_token(), default=default)

# Диспетчер
dp = Dispatcher()
