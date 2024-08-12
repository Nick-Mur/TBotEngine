from text.msg_func import *
from text.messages import *

from bot import *

from database.db_operation import db


async def edit(tg_id, msg, message: Message):
    msg_media = None if 'media' not in msg else msg['media']
    msg_text = message.caption if 'text' not in msg else msg['text']
    msg_keyboard = message.reply_markup if 'keyboard' not in msg else msg['keyboard']

    if msg_media:
        await message.edit_media(media=msg_media, text=msg_text, reply_markup=msg_keyboard)
    else:
        await message.edit_caption(caption=msg_text, reply_markup=msg_keyboard)
