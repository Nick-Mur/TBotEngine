from edit_func import edit

from find_message.find_message_0 import find_next_message_0, find_previous_message_0

from text.msg_func import update_msg

from bot import bot

from aiogram import Router
from aiogram.types import CallbackQuery

from database.db_operation import db
from database.db_consts import Func, Method

from consts import DEBUG

from special.special_func import return_variable

from traceback import print_exc


router = Router()


# На один этап один выбор максимум


@router.callback_query(lambda call: 'next_0' in call.data)
async def next_0_msg(call: CallbackQuery):
    tg_id = call.from_user.id
    data = call.data.split('_')[1:]

    db_data = dict()

    message_id, msg_id = await db(filters={1: ('==', tg_id)}, data=[2, 11], method=Method.FIRST)

    message = await return_variable(f'message_0_{message_id}')
    if len(message) > msg_id + 1:
        msg_id += 1
    else:
        if len(data) == 1:
            choice = None
        else:
            choice = data[1]
            await db(table=2, data={1: tg_id, 5: message_id, 6: choice}, operation=Func.ADD)
        message_id = await find_next_message_0(message_id, choice=choice)
        msg_id = 0
        db_data.update({2: message_id})
        message = await return_variable(f'message_0_{message_id}')

    await next_and_back(msg_id, call, message, tg_id, db_data)


@router.callback_query(lambda call: 'back_0' in call.data)
async def back_0_msg(call: CallbackQuery):
    tg_id = call.from_user.id

    db_data = dict()

    message_id, msg_id = await db(filters={1: ('==', tg_id)}, data=[2, 11], method=Method.FIRST)

    if msg_id > 0:
        message = await return_variable(f'message_0_{message_id}')
        msg_id -= 1
    else:
        message_id = await find_previous_message_0(message_id=message_id, tg_id=tg_id)
        message = await return_variable(f'message_0_{message_id}')
        msg_id = len(message) - 1
        db_data.update({2: message_id})

    await next_and_back(msg_id, call, message, tg_id, db_data)


async def next_and_back(msg_id, call, message, tg_id, db_data):
    db_data.update({11: msg_id})

    msg = message[msg_id]
    # Обновляем сообщение для пользователя
    msg = await update_msg(msg=msg, user=call.from_user)
    # Редактируем сообщение в чате
    await edit(msg=msg, message=call.message)

    await db(filters={1: ('==', tg_id)}, data=db_data, operation=Func.UPDATE)


@router.callback_query(lambda call: 'close' in call.data)
async def close_message(call: CallbackQuery):
    if 'ad' in call.data:
        tg_id = call.from_user.id

        # Получаем текущее количество токенов
        tokens = await db(table=3, filters={1: ('==', tg_id)}, data=8, method=Method.FIRST)

        # Обновляем количество токенов
        await db(table=3, filters={1: ('==', tg_id)}, data={8: tokens + 1}, operation=Func.UPDATE)

    try:
        # Удаляем сообщение
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    except Exception as e:
        if DEBUG:
            print_exc()


@router.callback_query()
async def handle_any_callback(call: CallbackQuery):
    print(1)
