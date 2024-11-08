"""
Модуль для обработки переходов между сообщениями на этапе 0.

Этот модуль содержит функции для определения следующего и предыдущего сообщения в зависимости от текущего состояния пользователя.
"""

from database.db_operation import db
from database.core.db_consts import Func, Method, Tables, Columns, Operators


async def find_next_message_0(message_id: int, choice: str = None, tg_id: int = None) -> int:
    """
    Определяет ID следующего сообщения на этапе 0 на основе текущего message_id и выбора пользователя.

    :param message_id: Текущий идентификатор сообщения.
    :param choice: Выбор пользователя, влияющий на переход.
    :param tg_id: Telegram ID пользователя (не используется в текущей реализации).
    :return: Идентификатор следующего сообщения.
    """
    if message_id == 0:
        if choice == 'a':
            return 1
        return 2
    elif message_id < 3:
        return 3


async def find_previous_message_0(message_id: int, tg_id: int) -> int:
    """
    Определяет ID предыдущего сообщения на этапе 0 на основе текущего message_id и Telegram ID пользователя.

    :param message_id: Текущий идентификатор сообщения.
    :param tg_id: Telegram ID пользователя.
    :return: Идентификатор предыдущего сообщения.
    """
    if message_id < 3:
        # Удаляем запись в таблице выбора
        await db(
            table=Tables.CHOICES,
            filters={
                Columns.TG_ID: (Operators.EQ, tg_id),
                Columns.MESSAGE_ID: (Operators.EQ, 0)
            },
            operation=Func.DELETE
        )
        return 0
    elif message_id == 3:
        # Получаем выбор пользователя (choice) из таблицы выбора
        choice = await db(
            table=Tables.CHOICES,
            filters={
                Columns.TG_ID: (Operators.EQ, tg_id),
                Columns.MESSAGE_ID: (Operators.EQ, 0)
            },
            data=Columns.RESULT_CHOICES,
            method=Method.FIRST
        )

        # Возвращаем соответствующий stage_id на основе выбора
        if choice == 'a':
            return 1
        return 2
