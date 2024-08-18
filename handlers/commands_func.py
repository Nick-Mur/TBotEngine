from database.db_operation import *


from text.msg_func import update_msg


from bot import *


from text.messages.messages_0 import message_0_0


router = Router()


@router.message(Command("save"))
async def save(message: Message):
    tg_id = message.from_user.id
    user = await db(table=0, filters={1: tg_id}, method=2, data=0)
    if user:
        message_id = await db(filters={1: tg_id}, data=11)
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
        except:
            if DEBUG:
                print_exc()
        stage_id, phrase_id = await db(filters={1: tg_id}, data=[4, 7])
        message_var = await return_variable(f'message_0_{stage_id}')
        msg = message_var[phrase_id]
        media_file = await return_variable(msg['media'])
        media_extension = media_file.split('.')[1]
        msg = await update_msg(msg=msg, user=message.from_user, new_media=True)
        if media_extension in ['png', 'jpeg', 'jpg']:
            sent_message = await message.answer_photo(photo=msg['media'], caption=msg['text'], reply_markup=msg['keyboard'])
        # Удаляем сообщение от пользователя
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        # обновляем message_id
        await db(filters={1: tg_id, 2: 0}, data={11: sent_message.message_id}, func=1)
        # Ждем сутки (в секундах)
        await asyncio.sleep(24 * 60 * 60)
        # Удаляем сообщение
        await bot.delete_message(chat_id=sent_message.chat.id, message_id=sent_message.message_id)


@router.message(Command("start"))
async def start(message: Message):
    tg_id = message.from_user.id
    user = await db(table=0, filters={1: tg_id}, method=2, data=0)
    if not user:
        await db(table=0, data={1: tg_id}, func=2)
        msg = await update_msg(msg=message_0_0[0], user=message.from_user, new_media=True)
        sent_message = await message.answer_photo(photo=msg['media'], caption=msg['text'], reply_markup=msg['keyboard'])
        # создаём save
        await db(data={1: tg_id, 11: sent_message.message_id}, func=2)
        # Удаляем сообщение от пользователя
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        # Ждем сутки (в секундах)
        await asyncio.sleep(24 * 60 * 60)
        # Удаляем сообщение
        await bot.delete_message(chat_id=sent_message.chat.id, message_id=sent_message.message_id)
