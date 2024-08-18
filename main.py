# импорты
from bot import *

from handlers import text_func, commands_func, callback_func


async def main():

    dp.include_routers(commands_func.router, text_func.router, callback_func.router)

    # Запускаем бота и пропускаем все накопленные входящие
    # Этот метод можно вызвать даже если у вас поллинг
    await bot.delete_webhook(drop_pending_updates=False)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
