"""
Обработчики callback-запросов для TBotEngine.
Этот модуль содержит функции для обработки различных callback-запросов от inline-кнопок, таких как навигация вперед и назад, закрытие сообщений, а также обработка любых других callback-запросов.
"""

from utils.edit_func import edit
from utils.find_message import find_next_message_0, find_previous_message_0
from utils.msg_func import update_msg
from app.bot import bot
from aiogram import Router
from aiogram.types import CallbackQuery
from database.db_operation import db
from database.core.db_consts import Func, Method, Tables, Columns, Operators
from app.consts import DEBUG
from settings.special_func import return_variable
from traceback import print_exc
from typing import Dict, Any, List, Optional

router = Router()


@router.callback_query(lambda call: 'next_0' in call.data)
async def next_0_msg(call: CallbackQuery) -> None:
    """
    Обработчик callback-запроса для перехода к следующему сообщению на этапе 0.

    :param call: CallbackQuery объект, содержащий данные запроса.
    """
    tg_id: int = call.from_user.id
    data: List[str] = call.data.split('_')[1:]

    db_data: Dict[Columns, Any] = {}

    message_id: int
    msg_id: int
    message_id, msg_id = await db(
        filters={Columns.TG_ID: (Operators.EQ, tg_id)},
        data=[Columns.MESSAGE_ID, Columns.MSG_ID],
        method=Method.FIRST
    )

    message: List[Dict[str, Any]] = await return_variable(f'message_0_{message_id}')
    if len(message) > msg_id + 1:
        msg_id += 1
    else:
        choice: Optional[str] = data[1] if len(data) > 1 else None
        if choice:
            await db(
                table=Tables.CHOICES,
                data={
                    Columns.TG_ID: tg_id,
                    Columns.MESSAGE_ID: message_id,
                    Columns.RESULT_CHOICES: choice
                },
                operation=Func.ADD
            )
        message_id = await find_next_message_0(message_id, choice=choice)
        msg_id = 0
        db_data.update({Columns.MESSAGE_ID: message_id})
        message = await return_variable(f'message_0_{message_id}')

    await next_and_back_0(msg_id, call, message, tg_id, db_data)


@router.callback_query(lambda call: 'back_0' in call.data)
async def back_0_msg(call: CallbackQuery) -> None:
    """
    Обработчик callback-запроса для перехода к предыдущему сообщению на этапе 0.

    :param call: CallbackQuery объект, содержащий данные запроса.
    """
    tg_id: int = call.from_user.id

    db_data: Dict[Columns, Any] = {}

    message_id: int
    msg_id: int
    message_id, msg_id = await db(
        filters={Columns.TG_ID: (Operators.EQ, tg_id)},
        data=[Columns.MESSAGE_ID, Columns.MSG_ID],
        method=Method.FIRST
    )

    if msg_id > 0:
        message: List[Dict[str, Any]] = await return_variable(f'message_0_{message_id}')
        msg_id -= 1
    else:
        message_id = await find_previous_message_0(message_id=message_id, tg_id=tg_id)
        message = await return_variable(f'message_0_{message_id}')
        msg_id = len(message) - 1
        db_data.update({Columns.MESSAGE_ID: message_id})

    await next_and_back_0(msg_id, call, message, tg_id, db_data)


async def next_and_back_0(
    msg_id: int,
    call: CallbackQuery,
    message: List[Dict[str, Any]],
    tg_id: int,
    db_data: Dict[Columns, Any]
) -> None:
    """
    Обновляет сообщение и сохраняет состояние в базе данных.

    :param msg_id: Индекс текущего сообщения в последовательности.
    :param call: CallbackQuery объект, содержащий данные запроса.
    :param message: Список словарей с данными сообщений.
    :param tg_id: Telegram ID пользователя.
    :param db_data: Словарь данных для обновления в базе данных.
    """
    db_data.update({Columns.MSG_ID: msg_id})

    msg: Dict[str, Any] = message[msg_id]
    if 'keyboard' not in msg:
        msg['keyboard'] = 'basic_0'
    # Обновляем сообщение для пользователя
    msg = await update_msg(msg=msg, user=call.from_user)
    # Редактируем сообщение в чате
    await edit(msg=msg, message=call.message)

    await db(
        filters={Columns.TG_ID: (Operators.EQ, tg_id)},
        data=db_data,
        operation=Func.UPDATE
    )


@router.callback_query(lambda call: 'close' in call.data)
async def close_message(call: CallbackQuery) -> None:
    """
    Обработчик callback-запроса для закрытия сообщения.

    Если в данных запроса присутствует 'ad', увеличивает количество токенов пользователя.

    :param call: CallbackQuery объект, содержащий данные запроса.
    """
    if 'ad' in call.data:
        tg_id: int = call.from_user.id

        # Получаем текущее количество токенов
        tokens: int = await db(
            table=Tables.GAME,
            filters={Columns.TG_ID: (Operators.EQ, tg_id)},
            data=Columns.TOKENS,
            method=Method.FIRST
        )

        # Обновляем количество токенов
        await db(
            table=Tables.GAME,
            filters={Columns.TG_ID: (Operators.EQ, tg_id)},
            data={Columns.TOKENS: tokens + 1},
            operation=Func.UPDATE
        )

    try:
        # Удаляем сообщение
        await bot.delete_message(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
    except Exception:
        if DEBUG:
            print_exc()


@router.callback_query()
async def handle_any_callback(call: CallbackQuery) -> None:
    """
    Обработчик всех остальных callback-запросов.

    :param call: CallbackQuery объект, содержащий данные запроса.
    """
    print(1)
