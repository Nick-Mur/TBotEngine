from database.db_operation import db
from database.core.db_consts import Method, Tables, Columns, Operators

from app.consts import MEDIA_PHOTO

from settings.special_func import return_variable
from aiogram.types import Message, InlineKeyboardMarkup, InputMediaPhoto, FSInputFile


async def update_msg(msg: dict, user: Message, new_media: bool = False) -> dict:
    """
    Обновляет содержимое сообщения для пользователя.

    Функция обновляет текст, медиа и клавиатуру сообщения на основе языка пользователя и переданных данных.

    :param msg: Словарь с данными сообщения.
    :param user: Объект пользователя Telegram.
    :param new_media: Флаг, указывающий, нужно ли использовать новый медиафайл.
    :return: Обновленный словарь с данными сообщения.
    """
    tg_id = user.id
    msg = msg.copy()

    # Получаем язык пользователя из базы данных
    language = await db(
        table=Tables.USER,
        filters={Columns.TG_ID: (Operators.EQ, tg_id)},
        data=Columns.LANGUAGE,
        method=Method.FIRST
    )

    # Обновляем текст сообщения, если он присутствует
    if 'text' in msg:
        msg_text = msg['text']
        var = await return_variable(f'{language}_{msg_text}')
        msg_text = await update_text(var, user=user)
        msg['text'] = msg_text

    # Обновляем медиафайл сообщения, если он присутствует
    if 'media' in msg:
        msg_media = msg['media']
        var = await return_variable(msg_media)
        msg['media'] = await get_media(var, new_media)

    # Обновляем клавиатуру сообщения, если она присутствует
    if 'keyboard' in msg:
        msg_keyboard = msg['keyboard']
        var = await return_variable(msg_keyboard)
        msg['keyboard'] = InlineKeyboardMarkup(inline_keyboard=var)

    return msg


async def update_text(value: str, user: Message) -> str:
    """
    Обновляет текст сообщения, заменяя плейсхолдеры на данные пользователя.

    :param value: Текст сообщения с плейсхолдерами.
    :param user: Объект пользователя Telegram.
    :return: Обновленный текст сообщения.
    """
    first_name = user.first_name
    value = value.replace('*first_name*', first_name)
    return value


async def get_media(value: str, new_media: bool):
    """
    Получает медиафайл для отправки пользователю.

    :param value: Имя файла медиа.
    :param new_media: Флаг, указывающий, нужно ли использовать новый медиафайл.
    :return: Объект медиафайла для отправки.
    """
    extension = value.split('.')[1]
    file = FSInputFile(MEDIA_PHOTO + value)
    if extension in ['png', 'jpeg', 'jpg']:
        if new_media:
            return file
        return InputMediaPhoto(media=file)
