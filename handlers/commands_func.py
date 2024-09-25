from database.db_operation import db


from text.msg_func import update_msg


from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice, PreCheckoutQuery

from consts import DEBUG
from traceback import print_exc

from bot import bot

from special.special_func import return_variable

import asyncio

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
        try:
            await bot.delete_message(chat_id=sent_message.chat.id, message_id=sent_message.message_id)
        except:
            if DEBUG:
                print_exc()


@router.message(Command("start"))
async def start(message: Message, command: CommandObject):
    from text.messages.messages_0 import message_0_0


    tg_id = message.from_user.id
    user = await db(table=0, filters={1: tg_id}, method=2, data=0)
    if not user:
        referral_link = command.args
        if referral_link.isdigit() and await db(table=0, filters={1: int(referral_link)}, method=2, data=0):
            tokens = await db(table=3, data=8, filters={1: referral_link})
            await db(table=3, filters={1: referral_link}, data=tokens + 1, func=1)
        await db(table=0, data={1: tg_id}, func=2)
        msg = await update_msg(msg=message_0_0[0], user=message.from_user, new_media=True)
        sent_message = await message.answer_photo(photo=msg['media'], caption=msg['text'], reply_markup=msg['keyboard'])
        # создаём save
        await db(data={1: tg_id, 11: sent_message.message_id}, func=2)
        # создаём game
        await db(table=3, data={1: tg_id}, func=2)
        # Удаляем сообщение от пользователя
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        # Ждем сутки (в секундах)
        await asyncio.sleep(24 * 60 * 60)
        # Удаляем сообщение
        try:
            await bot.delete_message(chat_id=sent_message.chat.id, message_id=sent_message.message_id)
        except:
            if DEBUG:
                print_exc()


@router.message(Command("ads"))
async def get_ads(message: Message):
    from text.messages.messages_1 import messages_1
    from random import choice

    Button = InlineKeyboardButton
    a_keyboard = InlineKeyboardMarkup(inline_keyboard=[[Button(text='❌', callback_data='close_ad')]])

    msg = await update_msg(msg=choice(messages_1), user=message.from_user, new_media=True)
    msg_timer, msg_text = msg['timer'], msg['text']

    # Отправляем начальное сообщение с таймером
    sent_message = await message.answer_photo(
        photo=msg['media'],
        caption=f"{msg_timer} секунд осталось\n\n{msg_text}"
    )

    # Обновляем сообщение каждую секунду
    for i in range(msg_timer - 1, 0, -1):
        try:
            await sent_message.edit_caption(caption=f"{i} секунд осталось\n\n{msg_text}")
            await asyncio.sleep(1)
        except Exception:
            if DEBUG:
                print_exc()
            return

    await sent_message.edit_caption(caption=msg_text, reply_markup=a_keyboard)

    await asyncio.sleep(24 * 60 * 60)

    try:
        await bot.delete_message(chat_id=sent_message.chat.id, message_id=sent_message.message_id)
    except:
        if DEBUG:
            print_exc()


@router.message(Command("balance"))
async def get_balance(message: Message):
    tg_id = message.from_user.id
    tokens = await db(table=3, filters={1: tg_id}, data=8)
    await send_func(message=message, text=f"Ваше количество токенов: {tokens}.")



@router.message(Command("ref"))
async def get_referral_link(message: Message):
    from special.decorate_text import link


    tg_id = message.from_user.id
    bot_username = (await bot.get_me()).username
    ref_link = link(text='ссылка', text_link=f'https://t.me/{bot_username}?start={tg_id}')
    await send_func(message=message, text=f"Ваша реферальная {ref_link}.")


@router.message(Command("buy"))
async def buy(message: Message):
    tg_id = message.from_user.id
    user = await db(table=0, filters={1: tg_id}, method=2, data=0)
    if not user: return
    Button = InlineKeyboardButton
    a_keyboard = InlineKeyboardMarkup(inline_keyboard=[[Button(text=f"Оплатить 100 ⭐️", pay=True)],
                                                       [Button(text='❌', callback_data='close')]])
    sent_message = await message.answer_invoice(
        title="Отключение рекламы",
        description="За 100 звёзд Вы можете забыть о рекламе и о токенах, играя в своё удовольствие! P.s. не забудьте ознакомиться с условиями",
        prices=[LabeledPrice(label="XTR", amount=100)],
        provider_token="",
        payload="no_ads",
        currency="XTR",
        reply_markup=a_keyboard
    )
    await asyncio.sleep(24 * 60 * 60)
    bot.refund_star_payment()

    try:
        await bot.delete_message(chat_id=sent_message.chat.id, message_id=sent_message.message_id)
    except:
        if DEBUG:
            print_exc()


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    tg_id = pre_checkout_query.from_user.id
    await db(table=3, filters={1: tg_id}, data={9: 1}, func=1)
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def on_successful_payment(message: Message):
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except:
        if DEBUG:
            print_exc()
    text = (f'id покупки: {message.successful_payment.telegram_payment_charge_id}.\n'
            f'Запомните его. Благодаря нему Вы сможете вернуться потраченные средства.')
    await send_func(message=message, text=text)


async def send_func(message: Message, text: str, keyboard: InlineKeyboardMarkup = None):
    if keyboard is None:
        Button = InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[Button(text='❌', callback_data='close')]])
    sent_message = await message.answer(
        text=text,
        reply_markup=keyboard
    )

    await asyncio.sleep(24 * 60 * 60)

    try:
        await bot.delete_message(chat_id=sent_message.chat.id, message_id=sent_message.message_id)
    except:
        if DEBUG:
            print_exc()
