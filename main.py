# Импорты
from app.bot import dp, bot
import asyncio
from aiohttp import web
from handlers import text_func, commands_func, callback_func
from database.core.db_session import global_init_async
from app.consts import DB_PATH, DEBUG
import logging
from datetime import datetime, timezone

from settings.special_func import get_webhook_host
from middlewares.middleware import IgnoreOldMessagesMiddleware


# Настройка переменных вебхука
WEBHOOK_HOST = get_webhook_host()
WEBHOOK_HOST = None if WEBHOOK_HOST == 'None' else WEBHOOK_HOST
WEBHOOK_PATH = '/webhook'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}" if WEBHOOK_HOST else None

# Порт для прослушивания вебхуков (обычно 443 для HTTPS)
WEBAPP_PORT = 443  # HTTPS-сервер обычно работает на порту 443 для вебхуков

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logging.getLogger("aiogram.event").setLevel(logging.WARNING)  # Убираем подробные логи о каждом обновлении

monitor_task = None


BOT_START_TIME = datetime.now(timezone.utc)


async def on_startup():
    from settings.special_func import monitor_unsubscribes, get_user_language_phrases
    from database.db_operation import db, Method
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    global monitor_task

    # Инициализируем базу данных
    await global_init_async(DB_PATH)

    # Включаем обработчики (роутеры)
    dp.include_routers(commands_func.router, text_func.router, callback_func.router)

    dp.update.outer_middleware(IgnoreOldMessagesMiddleware(BOT_START_TIME))

    # Отправка сообщений пользователям перед началом обработки команд (если не используется вебхук)
    if WEBHOOK_HOST:
        # Устанавливаем вебхук
        await bot.set_webhook(WEBHOOK_URL)
        logging.info(f"Вебхук установлен: {WEBHOOK_URL}")
    else:
        await bot.delete_webhook()
    tg_ids = await db(table=0, data=1, method=Method.ALL)

    Button = InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[Button(text='❌', callback_data='close')]])

    logging.info("Отправляем сообщения...")
    if not DEBUG:
        for tg_id in tg_ids:
            try:
                phrase = await get_user_language_phrases(tg_id=tg_id, data='phrases_bot_start')
                await bot.send_message(tg_id, phrase, reply_markup=keyboard)
                await asyncio.sleep(0.1)
            except Exception as e:
                pass

    # Запуск фоновой задачи для мониторинга подписок
    logging.info("Запуск мониторинга подписок...")
    monitor_task = asyncio.create_task(monitor_unsubscribes())


async def on_shutdown():
    global monitor_task
    """
    Завершаем работу бота при завершении программы
    """
    if WEBHOOK_HOST:
        logging.info("Удаление вебхука...")
        try:
            await bot.delete_webhook()
            logging.info("Вебхук удалён.")
        except Exception as e:
            logging.error(f"Ошибка при удалении вебхука: {e}")

    if monitor_task:
        logging.info("Отмена фоновой задачи...")
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            logging.info("Фоновая задача была успешно отменена.")

    logging.info("Удаление всех сообщений из чата...")
    tasks = [bot.delete_message(user_id, message_id) for message_id, user_id in commands_func.sent_messages]

    # Выполняем все задачи
    await asyncio.gather(*tasks, return_exceptions=True)

    # Закрываем сессию бота
    try:
        await bot.session.close()
        logging.info("Сессия бота закрыта.")
    except Exception as e:
        logging.error(f"Ошибка при закрытии сессии бота: {e}")

    # Завершаем все оставшиеся задачи
    loop = asyncio.get_running_loop()
    pending = asyncio.all_tasks(loop=loop)
    for task in pending:
        if task is not asyncio.current_task():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    dp.shutdown()


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
    # Инициализация перед началом работы
    await on_startup()

    if WEBHOOK_HOST:
        # Настраиваем приложение aiohttp для работы с вебхуками
        app = web.Application()

        # Маршрут для обработки вебхуков
        app.router.add_post(WEBHOOK_PATH, handle_webhook)

        # Настраиваем события завершения
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
        logging.info("Запуск polling...")
        try:
            await dp.start_polling(bot)
        except asyncio.CancelledError:
            logging.info("Polling был отменён.")

if __name__ == "__main__":
    try:
        asyncio.run(main())  # Используем asyncio.run вместо get_event_loop
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен")
