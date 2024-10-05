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


async def monitor_unsubscribes():
    from database.db_operation import db
    from database.db_consts import Method, Func
    from asyncio import sleep

    """
    Фоновая задача для проверки подписок пользователей.
    """
    while True:
        # Получаем список всех пользователей
        tg_ids = await db(table=0, data=1, method=Method.ALL)
        total_users = len(tg_ids)

        if total_users > 1440:
            interval = 10 * 60  # Проверяем каждые 10 минуту
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
                tokens = await db(table=3, filters={1: ('==', tg_id)}, data=8, method=Method.FIRST)
                # Проверка подписки на все каналы
                subscribed_count = sum(subscription_results.values())
                # Обновляем количество токенов
                await db(
                    table=3,
                    filters={1: ('==', tg_id)},
                    data={8: tokens + subscribed_count},
                    operation=Func.UPDATE
                )
            # Ждем перед обработкой следующего батча
            await sleep(interval)
        # После обработки всех батчей, цикл начнется заново



async def check_subscription(user_id: int) -> dict:
    from bot import bot
    from consts import CHANNEL_IDS


    """
    Проверяет подписку пользователя на несколько каналов.

    Параметры:
        bot (Bot): Экземпляр бота для выполнения запроса.
        user_id (int): ID пользователя, которого нужно проверить.
        channel_ids (list): Список ID или username каналов, например "@channelname".

    Возвращает:
        dict: Словарь с результатами проверки подписки для каждого канала.
              Формат: {channel_id: True/False}
    """
    results = {}
    for channel_id in CHANNEL_IDS:
        try:
            member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            # Проверяем статус пользователя: он должен быть подписан (member, administrator, owner)
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
    from database.db_operation import db
    from database.db_consts import Method, Func
    from importlib import import_module

    # Создаем сессию для взаимодействия с базой данных
    # Получаем язык пользователя из базы данных
    user_language = await db(
        table=0,  # Таблица User
        filters={1: ('==', tg_id)},  # 1 соответствует 'tg_id' в COLUMNS
        data=3,  # 3 соответствует 'language' в COLUMNS
        method=Method.FIRST,
        operation=Func.RETURN
    )

    # Импортируем модуль с фразами для нужного языка
    module = import_module(f'text.phrases.{user_language}_phrases.special_phrases')

    # Возвращаем объект (например, массив), который соответствует строке `data`
    phrases = getattr(module, data, None)

    # Если объект не найден, можно вернуть значение по умолчанию или вызвать исключение
    if phrases is None:
        raise ValueError(f"Не удалось найти объект '{data}' в модуле '{module.__name__}'")

    return phrases

