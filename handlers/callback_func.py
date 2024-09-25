from edit_func import edit

from find_message.find_message_0 import find_next_message_0, find_previous_message_0

from text.msg_func import update_msg

from bot import bot

from aiogram import Router
from aiogram.types import CallbackQuery

from database.db_operation import db

from consts import DEBUG

from special.special_func import return_variable

from traceback import print_exc


router = Router()


# На один этап один выбор максимум


@router.callback_query(lambda call: 'next_0' in call.data)
async def next_0_msg(call: CallbackQuery):
    tg_id = call.from_user.id
    data = call.data.split('_')[1:]
    stage_id, phrase_id = await db(filters={1: tg_id}, data=[4, 7])
    if len(data) == 2:
        choice = data[1]
        choice_id = f'0_{stage_id}'
        await db(table=2, data={1: tg_id, 5: choice_id, 6: choice}, func=2)
    else:
        choice = None
    message = await return_variable(f'message_0_{stage_id}')
    if phrase_id + 1 < len(message):
        phrase_id += 1
        msg = message[phrase_id]
    else:
        phrase_id = 0
        stage_id = await find_next_message_0(stage_id=stage_id, choice=choice)
        message = await return_variable(f'message_0_{stage_id}')
        msg = message[0]
    msg = await update_msg(msg=msg, user=call.from_user)
    await db(filters={1: tg_id, 2: 0}, data={4: stage_id, 7: phrase_id}, func=1)
    await edit(msg=msg, message=call.message)


@router.callback_query(lambda call: 'back_0' in call.data)
async def back_0_msg(call: CallbackQuery):
    tg_id = call.from_user.id
    stage_id, phrase_id = await db(filters={1: tg_id}, data=[4, 7])
    phrase_id -= 1
    if phrase_id < 0:
        stage_id = await find_previous_message_0(stage_id=stage_id, tg_id=tg_id)
    message = await return_variable(f'message_0_{stage_id}')
    msg = message[phrase_id]
    if phrase_id < 0:
        phrase_id = len(msg) - 1
    msg = await update_msg(msg=msg, user=call.from_user)
    await db(filters={1: tg_id, 2: 0}, data={4: stage_id, 7: phrase_id}, func=1)
    await edit(msg=msg, message=call.message)


@router.callback_query(lambda call: 'close' in call.data)
async def close_message(call: CallbackQuery):
    if 'ad' in call.data:
        tg_id = call.from_user.id
        tokens = await db(table=3, data=8, filters={1: tg_id})
        await db(table=3, filters={1: tg_id}, data={8: tokens + 1}, func=1)
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    except:
        if DEBUG:
            print_exc()


@router.callback_query()
async def handle_any_callback(call: CallbackQuery):
    print(1)
