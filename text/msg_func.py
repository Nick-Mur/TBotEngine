from imports import *


from database.db_operation import db


MEDIA_PHOTO = 'media/photo/'


async def update_msg(msg: dict, user: Message, new_media=False):
    tg_id = user.id
    language = await db(table=0, filters={1: tg_id}, data=3)
    data = dict()
    if 'text' in msg.keys():
        text = msg['text']
        data.update({8: text})
        var = await return_variable(f'{language}_{text}')
        text = await update_text(var, user=user)
        msg['text'] = text
    if 'media' in msg.keys():
        data.update({9: msg['media']})
        var = await return_variable(msg['media'])
        msg['media'] = await get_media(var, new_media)
    if 'keyboard' in msg.keys():
        keyboard = msg['keyboard']
        data.update({10: keyboard})
        keyboard = await return_variable(keyboard)
        if keyboard:
            keyboard = await process_keyboard(keyboard=keyboard, language=language)
        msg['keyboard'] = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await db(table=1, filters={1: tg_id}, data=data, func=1)
    return msg


async def process_keyboard(keyboard, language):
    # Вспомогательная функция для обработки кнопок
    async def process_button(btn):
        if isinstance(btn, str):
            return await return_variable(f"{language}_{btn}")
        return btn

    # Обработка клавиатуры с помощью вспомогательной функции
    result = list()
    for row in keyboard:
        massive = list()
        for btn in row:
            btn = await process_button(btn)
            massive.append(btn)
        result.append(massive)
    return result


async def update_text(value: str, user: Message):
    first_name = user.first_name
    value = value.replace('*first_name*', first_name)
    return value


async def get_media(value: str, new_media):
    extension = value.split('.')[1]
    if extension in ['png', 'jpeg', 'jpg']:
        if new_media:
            return FSInputFile(MEDIA_PHOTO + value)
        return InputMediaPhoto(media=FSInputFile(MEDIA_PHOTO + value))
