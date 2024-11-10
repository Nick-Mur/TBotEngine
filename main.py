"""
Главный модуль для запуска бота TBotEngine.

Этот модуль инициализирует бота, устанавливает обработчики, настраивает вебхук или polling,
а также содержит функции для корректного запуска и завершения работы бота.
"""

# Импорты
from app.bot import dp, bot
from app.temporary_data import sent_messages

import asyncio
from aiohttp import web
from handlers import text_func, commands_func, callback_func
from database.core.db_session import global_init_async
from app.consts import DB_PATH, DEBUG
import logging
from datetime import datetime, timezone

from settings.special_func import get_webhook_host
from middlewares.middleware import IgnoreOldMessagesMiddleware

from database.core.db_consts import Tables, Columns, Method

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


async def on_startup() -> None:
    """
    Функция, выполняющаяся при запуске бота.

    Инициализирует базу данных, включает обработчики (роутеры),
    устанавливает вебхук (если используется), отправляет стартовые сообщения пользователям
    и запускает фоновую задачу для мониторинга подписок.
    """
    from settings.special_func import monitor_unsubscribes, get_user_language_phrases
    from database.db_operation import db
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    global monitor_task

    # Инициализируем базу данных
    await global_init_async(DB_PATH)

    # Включаем обработчики (роутеры)
    dp.include_routers(commands_func.router, text_func.router, callback_func.router)

    # Добавляем middleware для игнорирования старых сообщений
    dp.update.outer_middleware(IgnoreOldMessagesMiddleware(BOT_START_TIME))

    # Отправка сообщений пользователям перед началом обработки команд
    if WEBHOOK_HOST:
        # Устанавливаем вебхук
        await bot.set_webhook(WEBHOOK_URL)
        logging.info(f"Вебхук установлен: {WEBHOOK_URL}")
    else:
        # Удаляем вебхук, если он не используется
        await bot.delete_webhook()

    # Получаем список всех пользователей из базы данных
    tg_ids = await db(
        table=Tables.USER,
        data=Columns.TG_ID,
        method=Method.ALL
    )

    Button = InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[Button(text='❌', callback_data='close')]])

    logging.info("Отправляем стартовые сообщения пользователям...")
    for tg_id in tg_ids:
        if not DEBUG:
            try:
                phrase = await get_user_language_phrases(tg_id=tg_id, data='phrases_bot_start')
                await bot.send_message(tg_id, phrase, reply_markup=keyboard)
                await asyncio.sleep(0.1)
            except Exception:
                pass

    # Запуск фоновой задачи для мониторинга подписок
    logging.info("Запуск мониторинга подписок...")
    monitor_task = asyncio.create_task(monitor_unsubscribes())


async def on_shutdown() -> None:
    """
    Функция, выполняющаяся при завершении работы бота.

    Отменяет фоновые задачи, удаляет вебхук, очищает сессии, удаляет сообщения
    и корректно завершает все асинхронные операции.
    """
    global monitor_task

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
    tasks = [bot.delete_message(user_id, message_id) for message_id, user_id in sent_messages]

    # Выполняем все задачи удаления сообщений
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


async def handle_webhook(request: web.Request) -> web.Response:
    """
    Обработчик для входящих запросов от Telegram через вебхук.

    Параметры:
        request (web.Request): Входящий запрос от Telegram.

    Возвращает:
        web.Response: Ответ для подтверждения успешной обработки.
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


async def main() -> None:
    """
    Главная функция запуска бота.

    Инициализирует бота, запускает веб-сервер для вебхуков или polling в зависимости от настроек.
    """
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
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен")
