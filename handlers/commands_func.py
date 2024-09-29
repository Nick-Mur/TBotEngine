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

from database.db_consts import Func, Method


router = Router()


@router.message(Command("save"))
async def save(message: Message):
    tg_id = message.from_user.id

    # Проверяем, существует ли пользователь
    user = await db(table=0, filters={1: ('==', tg_id)}, method=Method.COUNT, data=0)
    if user:
        # Получаем message_id
        message_id = await db(table=1, filters={1: ('==', tg_id)}, data=11, method=Method.FIRST)

        # Пытаемся удалить старое сообщение
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
        except Exception as e:
            if DEBUG:
                print_exc()

        # Получаем текущие stage_id и phrase_id
        stage_id, phrase_id = await db(table=0, filters={1: ('==', tg_id)}, data=[4, 7], method=Method.FIRST)

        # Получаем сообщение для текущего этапа
        message_var = await return_variable(f'message_0_{stage_id}')
        msg = message_var[phrase_id]

        # Получаем медиафайл и расширение
        media_file = await return_variable(msg['media'])
        media_extension = media_file.split('.')[1]

        # Обновляем сообщение
        msg = await update_msg(msg=msg, user=message.from_user, new_media=True)

        # Отправляем сообщение с фото или другим медиа
        if media_extension in ['png', 'jpeg', 'jpg']:
            sent_message = await message.answer_photo(photo=msg['media'], caption=msg['text'],
                                                      reply_markup=msg['keyboard'])

        # Обновляем message_id в базе данных
        await db(table=1, filters={1: ('==', tg_id), 2: ('==', 0)}, data={11: sent_message.message_id},
                 operation=Func.UPDATE)

        # Ждем сутки (в секундах) и удаляем сообщение
        await del_message(sent_message, message)


@router.message(Command("start"))
async def start(message: Message, command: CommandObject):
    from text.messages.messages_0 import message_0_0

    tg_id = message.from_user.id
    # Поиск пользователя по tg_id
    user = await db(table=0, filters={1: ('==', tg_id)}, method=Method.COUNT, data=0)

    if not user:
        referral_link = command.args
        if referral_link and referral_link.isdigit() and await db(table=0, filters={1: ('==', int(referral_link))}, method=Method.COUNT,
                                                data=0):
            tokens = await db(table=3, filters={1: ('==', referral_link)}, data=8, method=Method.FIRST)
            await db(table=3, filters={1: ('==', referral_link)}, data={8: tokens + 1}, operation=Func.UPDATE)

        # Создаем новую запись пользователя
        await db(table=0, data={1: tg_id}, operation=Func.ADD)

        # Отправляем сообщение пользователю
        msg = await update_msg(msg=message_0_0[0], user=message.from_user, new_media=True)
        sent_message = await message.answer_photo(photo=msg['media'], caption=msg['text'], reply_markup=msg['keyboard'])

        # Создаем новую запись в таблице Save
        await db(table=1, data={1: tg_id, 11: sent_message.message_id}, operation=Func.ADD)

        # Создаем новую запись в таблице Game
        await db(table=3, data={1: tg_id}, operation=Func.ADD)

        # Удаляем сообщение пользователя
        await del_message(sent_message, message)


@router.message(Command("ads"))
async def get_ads(message: Message):
    from random import choice
    from text.messages.messages_1 import messages_1
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    import asyncio

    tg_id = message.from_user.id

    # Получаем язык пользователя (поле language)
    user_language = await db(table=0, filters={1: ('==', tg_id)}, data=3, method=Method.FIRST)

    # Устанавливаем текст на русском или ином языке
    if user_language == 'ru':
        text = 'секунд осталось'
    else:
        text = 'seconds left'

    # Клавиатура с кнопкой закрытия
    Button = InlineKeyboardButton
    a_keyboard = InlineKeyboardMarkup(inline_keyboard=[[Button(text='❌', callback_data='close_ad')]])

    # Выбираем случайное сообщение из messages_1
    msg = await update_msg(msg=choice(messages_1), user=message.from_user, new_media=True)
    msg_timer, msg_text = msg['timer'], msg['text']

    # Отправляем начальное сообщение с таймером
    sent_message = await message.answer_photo(
        photo=msg['media'],
        caption=f"{text}: {msg_timer}\n\n{msg_text}"
    )

    # Удаляем исходное сообщение пользователя
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    # Обновляем сообщение каждую секунду
    for i in range(msg_timer - 1, 0, -1):
        try:
            await sent_message.edit_caption(caption=f"{text}: {i}\n\n{msg_text}")
            await asyncio.sleep(1)
        except Exception as e:
            if DEBUG:
                print_exc()
            return

    # По окончании таймера выводим окончательное сообщение с кнопкой закрытия
    await sent_message.edit_caption(caption=msg_text, reply_markup=a_keyboard)

    # Ждём 24 часа перед удалением рекламы
    await asyncio.sleep(24 * 60 * 60)

    # Пытаемся удалить сообщение с рекламой
    try:
        await bot.delete_message(chat_id=sent_message.chat.id, message_id=sent_message.message_id)
    except Exception as e:
        if DEBUG:
            print_exc()


@router.message(Command("balance"))
async def get_balance(message: Message):
    tg_id = message.from_user.id

    # Получаем количество токенов из таблицы Game (индекс 8 для tokens)
    tokens = await db(table=3, filters={1: ('==', tg_id)}, data=8, method=Method.FIRST)

    # Получаем язык пользователя из таблицы User (индекс 3 для language)
    user_language = await db(table=0, filters={1: ('==', tg_id)}, data=3, method=Method.FIRST)

    # Формируем сообщение в зависимости от языка пользователя
    if user_language == 'ru':
        text = f"Ваше количество токенов: {tokens}."
    else:
        text = f"Your token balance: {tokens}."

    # Отправляем сообщение пользователю
    await send_func(message=message, text=text)


@router.message(Command("ref"))
async def get_referral_link(message: Message):
    from special.decorate_text import link

    tg_id = message.from_user.id
    bot_username = (await bot.get_me()).username

    # Получаем язык пользователя из таблицы User (индекс 3 для language)
    user_language = await db(table=0, filters={1: ('==', tg_id)}, data=3, method=Method.FIRST)

    # Генерируем реферальную ссылку
    ref_link = f'https://t.me/{bot_username}?start={tg_id}'

    # Оформляем текст в зависимости от языка пользователя
    if user_language == 'ru':
        ref_link = link(text='ссылка', text_link=ref_link)
        text = f"Ваша реферальная {ref_link}."
    else:
        ref_link = link(text='link', text_link=ref_link)
        text = f"Your referral {ref_link}."

    # Отправляем сообщение с реферальной ссылкой
    await send_func(message=message, text=text)


@router.message(Command("buy"))
async def buy(message: Message):
    tg_id = message.from_user.id

    # Получаем информацию о пользователе, проверяя наличие по tg_id
    user = await db(table=0, filters={1: ('==', tg_id)}, method=Method.COUNT, data=0)
    if not user:
        return

    # Получаем язык пользователя
    user_language = await db(table=0, filters={1: ('==', tg_id)}, data=3, method=Method.FIRST)

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
    transaction_id = command.args

    # Получаем язык пользователя
    user_language = await db(
        table=0,  # Таблица User
        filters={0: ('==', tg_id)},  # 0 соответствует 'tg_id' в COLUMNS
        data=1,  # 1 соответствует 'language' в COLUMNS
        method=Method.FIRST,
        operation=Func.RETURN
    )

    # Загружаем фразы на основе языка пользователя
    if user_language == 'eng':
        pass
    else:
        from text.phrases.ru_phrases.phrases_2 import phrases

    if not transaction_id:
        text = phrases[0]  # Отсутствует ID транзакции
    else:
        try:
            # Получаем дату транзакции
            date = await db(
                table=4,  # Таблица Transactions
                filters={10: ('==', transaction_id)},  # 10 соответствует 'transaction_id' в COLUMNS
                data=12,  # 12 соответствует 'date' в COLUMNS
                method=Method.FIRST,
                operation=Func.RETURN
            )

            if not date:
                text = phrases[4]  # Транзакция не найдена
            else:
                time_difference = datetime.now() - date
                if time_difference.total_seconds() > 3600:
                    text = phrases[1]  # Прошло больше часа с момента покупки
                else:
                    # Проверяем, был ли уже обработан возврат
                    refund_status = await db(
                        table=4,  # Таблица Transactions
                        filters={10: ('==', transaction_id)},
                        data=13,  # 13 соответствует 'refund' в COLUMNS
                        method=Method.FIRST,
                        operation=Func.RETURN
                    )
                    if refund_status:
                        text = phrases[5]  # Возврат уже был обработан
                    else:
                        # Обновляем статус возврата в базе данных
                        success_update = await db(
                            table=4,
                            filters={10: ('==', transaction_id)},
                            data={13: True},  # Устанавливаем 'refund' в True
                            operation=Func.UPDATE
                        )
                        if success_update:
                            # Осуществляем возврат средств через бота
                            await bot.refund_star_payment(user_id=tg_id, transaction_id=transaction_id)
                            text = phrases[2]  # Возврат успешно выполнен
                        else:
                            text = phrases[4]  # Ошибка при обновлении статуса возврата

        except TelegramBadRequest as error:
            if "CHARGE_ALREADY_REFUNDED" in error.message:
                text = phrases[3]  # Средства уже были возвращены
            else:
                text = phrases[4]  # Произошла ошибка при возврате

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
