"""
Модуль для обработки переходов между сообщениями на этапе 0.

Этот модуль содержит функции для определения следующего и предыдущего сообщения в зависимости от текущего состояния пользователя.
"""

from database.db_operation import db
from database.core.db_consts import Func, Method, Tables, Columns, Operators

from typing import Dict, List, Tuple, Optional

from utils.message_map import load_message_map

from app.consts import MESSAGE_MAP


# Загрузка карты сообщений при инициализации модуля
message_map_0 = load_message_map(MESSAGE_MAP + 'map_0.txt')

async def find_next_message_0(message_id: int, choice: Optional[str] = None, tg_id: Optional[int] = None) -> int:
    """
    Определяет ID следующего сообщения на этапе 0 на основе текущего message_id и выбора пользователя.

    :param message_id: Текущий идентификатор сообщения.
    :param choice: Выбор пользователя на текущем сообщении.
    :param tg_id: Telegram ID пользователя.
    :return: Идентификатор следующего сообщения.
    """
    transitions = message_map_0.get(message_id)
    if not transitions:
        return message_id  # Нет переходов, остаёмся на текущем сообщении

    # Сохраняем выбор пользователя в базе данных, если указан tg_id и выбор
    if tg_id and choice is not None:
        await db(
            table=Tables.CHOICES,
            data={
                Columns.TG_ID: tg_id,
                Columns.MESSAGE_ID: message_id,
                Columns.CHOICE: choice
            },
            operation=Func.ADD
        )

    # Получаем выборы пользователя из базы данных
    user_choices = {}
    if tg_id:
        records = await db(
            table=Tables.CHOICES,
            filters={
                Columns.TG_ID: (Operators.EQ, tg_id)
            },
            data=[Columns.MESSAGE_ID, Columns.CHOICE],
            method=Method.ALL,
            operation=Func.RETURN
        )
        if records:
            for msg_id, user_choice in records:
                user_choices[msg_id] = user_choice

    # Ищем подходящий переход
    for to_id, conditions in transitions:
        if conditions is None:
            return to_id  # Безусловный переход
        elif ('else', None) in conditions:
            return to_id  # Переход по else
        else:
            if check_conditions(conditions, user_choices):
                return to_id

    # Если не нашли подходящий переход, остаёмся на текущем сообщении
    return message_id

def check_conditions(conditions: List[Tuple[int, str]], user_choices: Dict[int, str]) -> bool:
    """
    Проверяет выполнение условий перехода на основе выборов пользователя.

    :param conditions: Список условий в виде кортежей (message_id, choice).
    :param user_choices: Словарь выборов пользователя {message_id: choice}.
    :return: True, если условия выполнены, иначе False.
    """
    for condition in conditions:
        if condition == ('else', None):
            return True
        msg_id, expected_choice = condition
        user_choice = user_choices.get(msg_id)
        if user_choice != expected_choice:
            return False
    return True


async def find_previous_message_0(message_id: int, tg_id: int) -> int:
    """
    Определяет ID предыдущего сообщения на этапе 0 на основе текущего message_id и Telegram ID пользователя.

    :param message_id: Текущий идентификатор сообщения.
    :param tg_id: Telegram ID пользователя.
    :return: Идентификатор предыдущего сообщения.
    """
    # Ищем все переходы, ведущие к текущему сообщению
    previous_messages = []
    for from_id, transitions in message_map_0.items():
        for to_id, conditions in transitions:
            if to_id == message_id:
                previous_messages.append((from_id, conditions))

    if not previous_messages:
        return 0  # Нет предыдущих сообщений, возвращаемся к началу

    # Получаем выборы пользователя из базы данных
    user_choices = {}
    records = await db(
        table=Tables.CHOICES,
        filters={
            Columns.TG_ID: (Operators.EQ, tg_id)
        },
        data=[Columns.MESSAGE_ID, Columns.CHOICE],
        method=Method.ALL,
        operation=Func.RETURN
    )
    if records:
        for msg_id, user_choice in records:
            user_choices[msg_id] = user_choice

    # Ищем подходящий предыдущий переход
    for from_id, conditions in previous_messages:
        if conditions is None or ('else', None) in conditions:
            # Удаляем выбор на предыдущем сообщении (from_id)
            await delete_user_choice(tg_id, from_id)
            return from_id
        else:
            if check_conditions(conditions, user_choices):
                # Удаляем выбор на предыдущем сообщении (from_id)
                await delete_user_choice(tg_id, from_id)
                return from_id

    # Если не нашли подходящего предыдущего сообщения, остаёмся на текущем
    return message_id


async def delete_user_choice(tg_id: int, message_id: int) -> None:
    """
    Удаляет выбор пользователя для указанного сообщения.

    :param tg_id: Telegram ID пользователя.
    :param message_id: Идентификатор сообщения.
    """
    await db(
        table=Tables.CHOICES,
        filters={
            Columns.TG_ID: (Operators.EQ, tg_id),
            Columns.MESSAGE_ID: (Operators.EQ, message_id)
        },
        operation=Func.DELETE
    )
