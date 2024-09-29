from database.db_operation import db
from database.db_consts import Method


from consts import MEDIA_PHOTO

from special.special_func import return_variable
from aiogram.types import Message, InlineKeyboardMarkup, InputMediaPhoto, FSInputFile


async def update_msg(msg: dict, user: Message, new_media=False):
    tg_id = user.id
    msg = msg.copy()

    # Получаем язык пользователя
    language = await db(table=0, filters={1: ('==', tg_id)}, data=3, method=Method.FIRST)

    # Обновляем текст, если он есть в сообщении
    if 'text' in msg.keys():
        msg_text = msg['text']
        var = await return_variable(f'{language}_{msg_text}')
        msg_text = await update_text(var, user=user)
        msg['text'] = msg_text

    # Обновляем медиа, если оно есть в сообщении
    if 'media' in msg.keys():
        msg_media = msg['media']
        var = await return_variable(msg_media)
        msg['media'] = await get_media(var, new_media)

    # Обновляем клавиатуру, если она есть в сообщении
    if 'keyboard' in msg.keys():
        msg_keyboard = msg['keyboard']
        var = await return_variable(msg_keyboard)
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
