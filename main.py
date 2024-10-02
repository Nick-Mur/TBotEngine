# импорты
from bot import dp, bot
import asyncio
from aiohttp import web
from handlers import text_func, commands_func, callback_func
from database.data.db_session import global_init_async
from consts import DB_PATH
import logging

from special.special_func import get_webhook_host

# Настройка переменных вебхука
WEBHOOK_HOST = get_webhook_host()
WEBHOOK_HOST = None if WEBHOOK_HOST == 'None' else WEBHOOK_HOST
WEBHOOK_PATH = '/webhook'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}" if WEBHOOK_HOST else None

# Порт для прослушивания вебхуков (обычно 443 для HTTPS)
WEBAPP_PORT = 443  # HTTPS-сервер обычно работает на порту 443 для вебхуков

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)


async def on_startup(app=None):
    """
    Устанавливаем вебхук при старте приложения, если вебхук включён.
    Если вебхук не используется, удаляем активный вебхук.
    """
    # Инициализируем базу данных
    await global_init_async(DB_PATH)

    # Включаем обработчики (роутеры)
    dp.include_routers(commands_func.router, text_func.router, callback_func.router)

    if WEBHOOK_HOST:
        # Устанавливаем вебхук
        await bot.set_webhook(WEBHOOK_URL)
        logging.info(f"Вебхук установлен: {WEBHOOK_URL}")
    else:
        # Удаляем активный вебхук, если используется polling
        await bot.delete_webhook()
        logging.info("Вебхук удалён, запущен polling...")


async def on_shutdown(app=None):
    """
    Завершаем работу бота при завершении программы
    """
    if WEBHOOK_HOST:
        logging.info("Удаление вебхука...")
        await bot.delete_webhook()
        logging.info("Вебхук удалён.")

    # Закрываем сессию бота
    await bot.session.close()


async def handle_webhook(request):
    """
    Обработчик для входящих запросов от Telegram через вебхук
    """
    try:
        request_data = await request.json()
        logging.info(f"Получен вебхук: {request_data}")  # Логирование полученных данных
        update = dp.update_factory(request_data)
        await dp.process_update(update)
        return web.Response()
    except Exception as e:
        logging.error(f"Ошибка обработки вебхука: {e}")
        return web.Response(status=500)


async def main():
    if WEBHOOK_HOST:
        # Настраиваем приложение aiohttp для работы с вебхуками
        app = web.Application()

        # Маршрут для обработки вебхуков
        app.router.add_post(WEBHOOK_PATH, handle_webhook)

        # Настраиваем события старта и завершения
        app.on_startup.append(on_startup)
        app.on_shutdown.append(on_shutdown)

        # Запускаем веб-сервер
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', WEBAPP_PORT)
        await site.start()

        logging.info(f"Запуск веб-сервера на порту {WEBAPP_PORT}...")

        # Бесконечный цикл, чтобы сервер не завершился сразу
        await asyncio.Event().wait()
    else:
        # Если вебхук не используется, запускаем polling
        await on_startup()  # Выполняем инициализацию
        await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())  # Используем asyncio.run вместо get_event_loop
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен")
