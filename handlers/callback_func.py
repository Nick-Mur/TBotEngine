"""
Обработчики callback-запросов для TBotEngine.
Этот модуль содержит функции для обработки различных callback-запросов от inline-кнопок, таких как навигация вперед и назад, закрытие сообщений, а также обработка любых других callback-запросов.
"""
from utils.edit_func import edit
from utils.find_message import find_next_message_0, find_previous_message_0
from utils.msg_func import update_msg

from aiogram import Router
from aiogram.types import CallbackQuery

from database.db_operation import db
from database.core.db_consts import Func, Method, Tables, Columns, Operators

from app.consts import DEBUG
from app.temporary_data import sent_messages

from settings.special_func import return_variable

from traceback import print_exc

from typing import Dict, Any, List

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

    message = await return_variable(f'message_0_{message_id}')
    if len(message) > msg_id + 1:
        msg_id += 1
    else:
        choice = data[1] if len(data) > 1 else None
        message_id = await find_next_message_0(message_id=message_id, choice=choice, tg_id=tg_id)
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
        await call.message.delete()
    except Exception as e:
        if DEBUG:
            print_exc()


@router.callback_query(lambda call: 'language' in call.data)
async def language_selection(callback: CallbackQuery) -> None:
    """
    Обработчик выбора языка пользователем.

    Обновляет язык пользователя в базе данных и удаляет сообщение.
    """
    from settings.special_func import get_user_language_phrases  # Импортируйте при необходимости

    tg_id = callback.from_user.id
    selected_language = callback.data.split('_')[1]

    # Обновляем язык пользователя в базе данных
    await db(
        table=Tables.USER,
        filters={Columns.TG_ID: (Operators.EQ, tg_id)},
        data={Columns.LANGUAGE: selected_language},
        operation=Func.UPDATE
    )

    # Удаляем сообщение с выбором языка
    try:
        await callback.message.delete()
    except Exception as e:
        if DEBUG:
            print_exc()


@router.callback_query(lambda call: 'confirm_restart' in call.data)
async def confirm_restart(callback: CallbackQuery) -> None:
    """
    Обработчик сброса сюжета.

    Перезапускает игру.
    """
    tg_id = callback.from_user.id
    await db(
        table=Tables.CHOICES,
        filters={Columns.TG_ID: (Operators.EQ, tg_id)},
        operation=Func.DELETE,
        method=Method.ALL
    )
    await db(
        table=Tables.GAME,
        filters={Columns.TG_ID: (Operators.EQ, tg_id)},
        data={Columns.MESSAGE_ID: 0, Columns.MSG_ID: 0},
        operation=Func.UPDATE
    )
    try:
        await callback.message.delete()

        # start

        from resources.messages.messages_0 import message_0_0
        from app.bot import bot

        # Получаем идентификатор отправленного сообщения
        sent_message_id = await db(
            table=Tables.GAME,
            filters={Columns.TG_ID: (Operators.EQ, tg_id)},
            data=Columns.SENT_MESSAGE_ID,
            method=Method.FIRST,
        )

        # Пытаемся удалить старое сообщение пользователя
        try:
            await bot.delete_message(chat_id=callback.message.chat.id, message_id=sent_message_id)
        except Exception:
            pass

        msg = await update_msg(msg=message_0_0[0], user=callback.from_user, new_media=True)
        sent_message = await bot.send_photo(photo=msg["media"], caption=msg["text"], reply_markup=msg["keyboard"], chat_id=callback.message.chat.id)
        sent_messages.append((sent_message.message_id, tg_id))

    except Exception as e:
        if DEBUG:
            print_exc()



@router.callback_query()
async def handle_any_callback(call: CallbackQuery) -> None:
    """
    Обработчик всех остальных callback-запросов.

    :param call: CallbackQuery объект, содержащий данные запроса.
    """
    print(1)
