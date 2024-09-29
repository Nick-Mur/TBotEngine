# импорты
from bot import dp, bot
from asyncio import run

from handlers import text_func, commands_func, callback_func

from database.data.db_session import global_init_async
from consts import DB_PATH


async def main():

    dp.include_routers(commands_func.router, text_func.router, callback_func.router)
    await global_init_async(DB_PATH)

    # Запускаем бота и пропускаем все накопленные входящие
    # Этот метод можно вызвать даже если у вас поллинг
    await bot.delete_webhook(drop_pending_updates=False)
    await dp.start_polling(bot)


if __name__ == "__main__":
    run(main())
