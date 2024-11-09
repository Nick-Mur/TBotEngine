from app.consts import SPECIAL_PHRASES
from settings.config_reader import config

from resources.buttons import *
from resources.keyboards import *

from resources.phrases.ru.phrases_0 import *
from resources.media.media_py.media_0 import *
from resources.messages.messages_0 import *

from resources.phrases.ru.phrases_1 import *
from resources.media.media_py.media_1 import *
from resources.messages.messages_1 import *

from database.core.db_consts import Method, Func, Tables, Columns, Operators


def get_bot_token() -> str:
    """
    Получает токен бота из настроек конфигурации.

    Возвращает:
        str: Токен бота.
    """
    return config.bot_token.get_secret_value()


def get_webhook_host() -> str:
    """
    Получает хост вебхука из настроек конфигурации.

    Возвращает:
        str: Хост вебхука.
    """
    return config.webhook_host.get_secret_value()


async def return_variable(value: str):
    """
    Возвращает значение глобальной переменной по её имени.

    Параметры:
        value (str): Имя переменной.

    Возвращает:
        Any: Значение переменной, если переменная существует в глобальной области видимости, иначе None.
    """
    if value in globals():
        return globals()[value]
    else:
        return None


async def monitor_unsubscribes() -> None:
    """
    Фоновая задача для периодической проверки подписок пользователей и обновления их баланса токенов.

    Функция выполняет циклическую проверку подписок всех пользователей на каналы,
    обновляет количество токенов в зависимости от количества подписок, и распределяет нагрузку на сервер,
    разбивая пользователей на батчи и устанавливая интервал между проверками.
    """
    from database.db_operation import db
    from asyncio import sleep

    while True:
        # Получаем список всех пользователей
        tg_ids = await db(table=Tables.USER, data=Columns.TG_ID, method=Method.ALL)
        total_users = len(tg_ids)

        if total_users > 1440:
            interval = 10 * 60  # Проверяем каждые 10 минут
            batches = 144
        elif total_users > 100:
            interval = 60 * 60  # Проверяем каждый час
            batches = 24
        else:
            interval = 60 * 60 * 24  # Проверяем раз в сутки
            batches = 1

        batch_size = (total_users + batches - 1) // batches  # Округляем вверх

        for i in range(0, total_users, batch_size):
            batch = tg_ids[i:i + batch_size]
            for tg_id in batch:
                # Обрабатываем каждого пользователя
                subscription_results = await check_subscription(tg_id)
                # Получаем текущее количество токенов
                tokens = await db(
                    table=Tables.GAME,
                    filters={Columns.TG_ID: (Operators.EQ, tg_id)},
                    data=Columns.TOKENS,
                    method=Method.FIRST
                )
                # Проверка подписки на все каналы
                subscribed_count = sum(subscription_results.values())
                # Обновляем количество токенов
                await db(
                    table=Tables.GAME,
                    filters={Columns.TG_ID: (Operators.EQ, tg_id)},
                    data={Columns.TOKENS: tokens + subscribed_count},
                    operation=Func.UPDATE
                )
            # Ждем перед обработкой следующего батча
            await sleep(interval)
        # После обработки всех батчей, цикл начнется заново


async def check_subscription(user_id: int) -> dict:
    """
    Проверяет подписку пользователя на указанные каналы.

    Параметры:
        user_id (int): Telegram ID пользователя, которого нужно проверить.

    Возвращает:
        dict: Словарь с результатами проверки подписки для каждого канала.
              Формат: {channel_id: True/False}, где True означает, что пользователь подписан на канал.
    """
    from app.bot import bot
    from app.consts import CHANNEL_IDS

    results = {}
    for channel_id in CHANNEL_IDS:
        try:
            member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            # Проверяем статус пользователя: он должен быть подписан (member, administrator, creator)
            if member.status in ['member', 'administrator', 'creator']:
                results[channel_id] = True
            else:
                results[channel_id] = False
        except Exception as e:
            # Если произошла ошибка, например пользователь не найден или бот не имеет доступа к каналу
            print(f"Ошибка при проверке подписки на канал {channel_id}: {e}")
            results[channel_id] = False
    return results


async def get_user_language_phrases(tg_id: int, data: str):
    """
    Получает фразы на языке пользователя для указанного ключа.

    Параметры:
        tg_id (int): Telegram ID пользователя.
        data (str): Ключ для доступа к фразам.

    Возвращает:
        Any: Объект с фразами, соответствующий указанному ключу.
    """
    from database.db_operation import db
    from importlib import import_module

    # Получаем язык пользователя из базы данных
    user_language = await db(
        table=Tables.USER,
        filters={Columns.TG_ID: (Operators.EQ, tg_id)},
        data=Columns.LANGUAGE,
        method=Method.FIRST
    )
    # Импортируем модуль с фразами для нужного языка
    module = import_module(f'{SPECIAL_PHRASES}.{user_language}.special_phrases')

    # Возвращаем объект (например, массив), который соответствует строке `data`
    phrases = getattr(module, data, None)

    # Если объект не найден, вызываем исключение
    if phrases is None:
        raise ValueError(f"Не удалось найти объект '{data}' в модуле '{module.__name__}'")

    return phrases
