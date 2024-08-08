from database.db_operation import *


from send_func import update_msg


from bot import *


router = Router()


@router.message(Command("save"))
async def save(message: Message):
    tg_id = message.from_user.id
    user = await db(table=0, filters={1: tg_id}, method=2, data=0)
    if not user: return await start(message)
    save_data = await db(filters={1: tg_id}, data=[8, 9, 10, 11])
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=save_data[3])
    except:
        pass
    msg = {'text': save_data[0], 'media': save_data[1], 'keyboard': save_data[2]}
    msg = await update_msg(msg=msg, user=message.from_user, new_media=True)
    media_file = msg['media']
    if isinstance(media_file, FSInputFile):
        await message.answer_photo(photo=media_file, caption=msg['text'], reply_markup=msg['keyboard'])


@router.message(Command("start"))
async def start(message: Message):
    tg_id = message.from_user.id
    user = await db(table=0, filters={1: tg_id}, method=2, data=0)
    if not user:
        await db(table=0, data={1: tg_id}, func=2, method=1)
        await db(data={1: tg_id, 11: message.message_id}, func=2, method=1)
        save_data = await db(filters={1: tg_id}, data=[8, 9, 10])
        msg = {'text': save_data[0], 'media': save_data[1], 'keyboard': save_data[2]}
        msg = await update_msg(msg=msg, user=message.from_user, new_media=True)
        await message.answer_photo(photo=msg['media'], caption=msg['text'], reply_markup=msg['keyboard'])
    else:
        await save(message)
