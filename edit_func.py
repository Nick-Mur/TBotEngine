async def edit(msg, message):
    await message.edit_media(media=msg['media'])
    await message.edit_caption(caption=msg['text'], reply_markup=msg['keyboard'])
