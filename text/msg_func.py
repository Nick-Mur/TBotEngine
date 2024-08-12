from imports import *


from database.db_operation import db


MEDIA_PHOTO = 'media/photo/'


async def update_msg(msg: dict, user: Message, new_media=False):
    tg_id = user.id
    language = await db(table=0, filters={1: tg_id}, data=3)
    if 'text' in msg.keys():
        text = msg['text']
        var = await return_variable(f'{language}_{text}')
        text = await update_text(var, user=user)
        msg['text'] = text
    if 'media' in msg.keys():
        var = await return_variable(msg['media'])
        msg['media'] = await get_media(var, new_media)
    if 'keyboard' in msg.keys():
        var = await return_variable(msg['keyboard'])
        msg['keyboard'] = InlineKeyboardMarkup(inline_keyboard=var)
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
