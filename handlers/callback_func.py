from imports import *

from database.db_operation import *

from edit_func import edit

from find_message.find_message_0 import *

from text.msg_func import update_msg


router = Router()


@router.callback_query(lambda call: 'next_0' in call.data)
async def next_0_msg(call: CallbackQuery):
    tg_id = call.from_user.id
    data = call.data.split('_')[1:]
    stage_id, phrase_id = await db(filters={1: tg_id}, data=[4, 7])
    if len(data) == 2:
        choice = data[1]
        choice_id = f'0_{stage_id}_{phrase_id}'
        await db(table=2, filters={1: tg_id}, data={5: choice_id, 6: choice}, func=2)
    else:
        choice = None
    message = await return_variable(f'message_0_{stage_id}')
    if phrase_id + 1 < len(message):
        if not choice:
            phrase_id += 1
            msg = message[phrase_id]
    else:
        phrase_id = 0
        stage_id = await find_message_0(stage_id=stage_id, choice=choice)
        message = await return_variable(f'message_0_{stage_id}')
        msg = message[0]
    msg = update_msg(msg=msg, user=call.from_user)
    await db(filters={1: tg_id, 2: 0}, data={4: stage_id, 7: phrase_id}, func=1)
    await edit(tg_id=tg_id, msg=msg, message=call.message)


@router.callback_query()
async def handle_any_callback(call: CallbackQuery):
    print(1)
