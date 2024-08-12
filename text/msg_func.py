from imports import *


from database.db_operation import db


MEDIA_PHOTO = 'media/photo/'


async def update_msg(msg: dict, user: Message, new_media=False, type_id=0):
    tg_id = user.id
    language = await db(table=0, filters={1: tg_id}, data=3)
    text_now, media_now, keyboard_now = await db(filters={1: tg_id, 2: type_id}, data=[8, 9, 10])
    await db(filters={1: tg_id, 2: type_id}, data={12: text_now, 13: media_now, 14: keyboard_now}, func=1)
    data = dict()
    if 'text' in msg.keys():
        text = msg['text']
        data.update({8: text})
        var = await return_variable(f'{language}_{text}')
        text = await update_text(var, user=user)
        msg['text'] = text
    if 'media' in msg.keys():
        media = msg['media']
        data.update({9: media})
        var = await return_variable(media)
        msg['media'] = await get_media(var, new_media)
    if 'keyboard' in msg.keys():
        keyboard = msg['keyboard']
        data.update({10: keyboard})
        var = await return_variable(keyboard)
        msg['keyboard'] = InlineKeyboardMarkup(inline_keyboard=var)
    await db(filters={1: tg_id, 2: type_id}, data=data, func=1)
    return msg


async def update_text(value: str, user: Message):
    first_name = user.first_name
    value = value.replace('*first_name*', first_name)
    return value


async def get_media(value: str, new_media):
    extension = value.split('.')[1]
    file = FSInputFile(MEDIA_PHOTO + value)
    if extension in ['png', 'jpeg', 'jpg']:
        if new_media:
            return file
        return InputMediaPhoto(media=file)
