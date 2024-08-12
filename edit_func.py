from text.msg_func import *
from text.messages import *

from bot import *

from database.db_operation import db


async def edit(tg_id, msg):
    if call:
        user = call.from_user
        message = call.message
    else:
        user = message.from_user
    tg_id = user.id
    msg = await find_plot_message(tg_id, back)

    msg_media = None if 'media' not in msg else msg['media']
    msg_text = message.caption if 'text' not in msg else msg['text']
    msg_keyboard = message.reply_markup if 'keyboard' not in msg else msg['keyboard']

    if msg_media:
        await message.edit_media(media=msg_media, text=msg_text, reply_markup=msg_keyboard)
    else:
        await message.edit_caption(caption=msg_text, reply_markup=msg_keyboard)


async def find_plot_message(tg_id: int, back, last_phrase=False):
    stage, phrase_id = await db(filters={1: tg_id}, data=[4, 7])
    msg = f'stage_{stage}'
    if msg in globals():
        msg = globals()[msg]
    else:
        if stage == 1:
            result = await db(table=2, filters={1: tg_id, 5: stage}, data=6)
        msg = globals()[f'{msg}_{result}']
    if phrase_id + 1 > len(msg):
        await db(filters={1: tg_id}, func=1, data={4: stage + 1, 7: 0})
        return await find_plot_message(tg_id, back)
    elif phrase_id < 0 and not last_phrase:
        await db(filters={1: tg_id}, func=1, data={4: stage - 1})
        return await find_plot_message(tg_id, last_phrase=True, back=back)
    elif phrase_id < 0:
        phrase_id = len(msg) - 1
        await db(filters={1: tg_id}, func=1, data={7: phrase_id})
    if back:
        save_data = await db(filters={1: tg_id}, data=[8, 9, 10])

    return msg[phrase_id]
