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
        tg_ids = await db(table=0, data=1, method=Method.ALL)
        for tg_id in tg_ids:
            subscription_results = await check_subscription(tg_id)
            # Получаем текущее количество токенов
            tokens = await db(table=3, filters={1: ('==', tg_id)}, data=8, method=Method.FIRST)
            # Проверка подписки на все каналы
            subscribed_count = sum(subscription_results.values())
            # Обновляем количество токенов
            await db(table=3, filters={1: ('==', tg_id)}, data={8: tokens + subscribed_count}, operation=Func.UPDATE)
        # Ждем 24 часа перед следующей проверкой
        await sleep(60 * 60 * 24)


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


async def get_user_language_phrases(tg_id: int, module: str):
    from importlib import import_module

    from database.db_operation import db
    from database.db_consts import Method, Func


    """
    Получает язык пользователя из базы данных и возвращает соответствующие фразы.
    """
    user_language = await db(
        table=0,  # Таблица User
        filters={1: ('==', tg_id)},  # 1 соответствует 'tg_id' в COLUMNS
        data=3,  # 3 соответствует 'language' в COLUMNS
        method=Method.FIRST,
        operation=Func.RETURN
    )

    module = import_module(f'text.phrases.{user_language}_phrases.{module}')
    return module.phrases

