from aiogram.exceptions import TelegramBadRequest

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
        # обновляем message_id
        await db(filters={1: tg_id, 2: 0}, data={11: sent_message.message_id}, func=1)
        # Ждем сутки (в секундах)
        await del_message(sent_message, message)


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
        await del_message(sent_message, message)


@router.message(Command("ads"))
async def get_ads(message: Message):
    from random import choice
    from text.messages.messages_1 import messages_1


    tg_id = message.from_user.id
    user_language = await db(table=0, filters={1: tg_id}, data=3)
    if user_language == 'ru':
        text = 'секунд осталось'
    Button = InlineKeyboardButton
    a_keyboard = InlineKeyboardMarkup(inline_keyboard=[[Button(text='❌', callback_data='close_ad')]])

    msg = await update_msg(msg=choice(messages_1), user=message.from_user, new_media=True)
    msg_timer, msg_text = msg['timer'], msg['text']

    # Отправляем начальное сообщение с таймером
    sent_message = await message.answer_photo(
        photo=msg['media'],
        caption=f"{text}: {msg_timer}\n\n{msg_text}"
    )
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    # Обновляем сообщение каждую секунду
    for i in range(msg_timer - 1, 0, -1):
        try:
            await sent_message.edit_caption(caption=f"{text}: {i}\n\n{msg_text}")
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
    user_language = await db(table=0, filters={1: tg_id}, data=3)
    if user_language == 'ru':
        text = f"Ваше количество токенов: {tokens}."
    await send_func(message=message, text=text)


@router.message(Command("ref"))
async def get_referral_link(message: Message):
    from special.decorate_text import link


    tg_id = message.from_user.id
    bot_username = (await bot.get_me()).username
    user_language = await db(table=0, filters={1: tg_id}, data=3)
    ref_link = f'https://t.me/{bot_username}?start={tg_id}'
    if user_language == 'ru':
        ref_link = link(text='ссылка', text_link=ref_link)
        text = f"Ваша реферальная {ref_link}."
    await send_func(message=message, text=text)


@router.message(Command("buy"))
async def buy(message: Message):
    tg_id = message.from_user.id
    user = await db(table=0, filters={1: tg_id}, method=2, data=0)
    if not user: return
    user_language = await db(table=0, filters={1: tg_id}, data=3)
    if user_language == 'ru':
        button_text = f"Оплатить 100 ⭐️"
        title_text = "Отключение рекламы"
        description_text = "За 100 звёзд Вы можете забыть о рекламе и о токенах, играя в своё удовольствие! P.s. не забудьте ознакомиться с условиями"
    Button = InlineKeyboardButton
    a_keyboard = InlineKeyboardMarkup(inline_keyboard=[[Button(text=button_text, pay=True)],
                                                       [Button(text='❌', callback_data='close')]])
    sent_message = await message.answer_invoice(
        title=title_text,
        description=description_text,
        prices=[LabeledPrice(label="XTR", amount=100)],
        provider_token="",
        payload="no_ads",
        currency="XTR",
        reply_markup=a_keyboard
    )
    await del_message(sent_message, message)


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    tg_id = pre_checkout_query.from_user.id
    await db(table=3, filters={1: tg_id}, data={9: 1}, func=1)
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def on_successful_payment(message: Message):
    from datetime import datetime


    tg_id = message.from_user.id
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except:
        if DEBUG:
            print_exc()
    await db(table=4, data={1: tg_id, 10: message.successful_payment.telegram_payment_charge_id, 13: datetime.now()}, func=2)
    user_language = await db(table=0, filters={1: tg_id}, data=3)
    if user_language == 'ru':
        text = (f'id транзакции: {message.successful_payment.telegram_payment_charge_id}.\n'
                f'Запомните его. Благодаря нему Вы сможете вернуться потраченные средства.')
    await send_func(message=message, text=text)


@router.message(Command("refund"))
async def refund(message: Message, command: CommandObject):
    from datetime import datetime


    tg_id = message.from_user.id
    user_language = await db(table=0, filters={1: tg_id}, data=3)
    if user_language == 'ru':
        from text.phrases.ru_phrases.phrases_2 import phrases
    transaction_id = command.args
    if transaction_id is None:
        text = phrases[0]
    else:
        try:
            date = await db(table=4, filters={10: transaction_id}, data=13)
            time_difference = datetime.now() - date
            if time_difference.total_seconds() > 3600:
               text = phrases[1]
            elif await db(table=3, filters={1: tg_id}, data=13):
                text = phrases[5]
            else:
                await db(table=3, filters={1: tg_id}, data={13: 1}, func=1)
                await bot.refund_star_payment(user_id=tg_id, transaction_id=transaction_id)
                text = phrases[2]
        except TelegramBadRequest as error:
            if "CHARGE_ALREADY_REFUNDED" in error.message:
                text = phrases[3]
            else:
                text = phrases[4]
    await send_func(message, text)



async def send_func(message: Message, text: str, keyboard: InlineKeyboardMarkup = None):
    if keyboard is None:
        Button = InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[Button(text='❌', callback_data='close')]])
    sent_message = await message.answer(
        text=text,
        reply_markup=keyboard
    )

    await del_message(sent_message, message)


async def del_message(sent_message: Message, message: Message):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    await asyncio.sleep(24 * 60 * 60)

    try:
        await bot.delete_message(chat_id=sent_message.chat.id, message_id=sent_message.message_id)
    except:
        if DEBUG:
            print_exc()
