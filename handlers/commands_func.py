from aiogram.exceptions import TelegramBadRequest

from database.db_operation import db


from text.msg_func import update_msg


from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice, PreCheckoutQuery

from consts import DEBUG, ADMINS
from traceback import print_exc

from bot import bot

from special.special_func import return_variable, get_user_language_phrases

import asyncio

from database.db_consts import Func, Method


router = Router()


@router.message(Command("save"))
async def save(message: Message):
    tg_id = message.from_user.id

    # Проверяем, существует ли пользователь
    user = await db(table=0, filters={1: ('==', tg_id)}, method=Method.COUNT, data=0)
    if not user:
        await start(message=message)
    # Получаем message_id
    sent_message_id = await db(table=3, filters={1: ('==', tg_id)}, data=4, method=Method.FIRST)

    # Пытаемся удалить старое сообщение
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=sent_message_id)
    except Exception as e:
        if DEBUG:
            print_exc()

    message_id, msg_id = await db(filters={1: ('==', tg_id)}, data=[2, 11], method=Method.FIRST)

    # Получаем сообщение для текущего этапа
    message_var = await return_variable(f'message_0_{message_id}')
    msg = message_var[msg_id]

    # Получаем медиафайл и расширение
    media_file = await return_variable(msg['media'])
    media_extension = media_file.split('.')[1]

    # Обновляем сообщение
    if 'keyboard' not in msg:
        msg['keyboard'] = 'basic_0'
    msg = await update_msg(msg=msg, user=message.from_user, new_media=True)

    # Отправляем сообщение с фото или другим медиа
    if media_extension in ['png', 'jpeg', 'jpg']:
        sent_message = await message.answer_photo(photo=msg['media'], caption=msg['text'],
                                                  reply_markup=msg['keyboard'])

    # Обновляем message_id в базе данных
    await db(table=3, filters={1: ('==', tg_id)}, data={4: sent_message.message_id}, operation=Func.UPDATE)

    # Ждем сутки (в секундах) и удаляем сообщение
    await del_message(sent_message, message)


@router.message(Command("start"))
async def start(message: Message, command: CommandObject):
    from text.messages.messages_0 import message_0_0

    tg_id = message.from_user.id
    # Поиск пользователя по tg_id
    user = await db(table=0, filters={1: ('==', tg_id)}, method=Method.COUNT, data=0)
    if user:
        await save(message=message)
    referral_link = command.args
    if referral_link and referral_link.isdigit() and await db(table=0, filters={1: ('==', int(referral_link))}, method=Method.COUNT,
                                            data=0):
        tokens = await db(table=3, filters={1: ('==', referral_link)}, data=8, method=Method.FIRST)
        await db(table=3, filters={1: ('==', referral_link)}, data={8: tokens + 3}, operation=Func.UPDATE)

    # Создаем новую запись пользователя
    await db(table=0, data={1: tg_id}, operation=Func.ADD)

    # Отправляем сообщение пользователю
    msg = await update_msg(msg=message_0_0[0], user=message.from_user, new_media=True)
    sent_message = await message.answer_photo(photo=msg['media'], caption=msg['text'], reply_markup=msg['keyboard'])

    # Создаем новую запись в таблице Game
    await db(table=3, data={1: tg_id, 4: sent_message.message_id}, operation=Func.ADD)

    # Удаляем сообщение пользователя
    await del_message(sent_message, message)


@router.message(Command("ads"))
async def get_ads(message: Message):
    from random import choice
    from text.messages.messages_1 import messages_1

    tg_id = message.from_user.id

    phrases = await get_user_language_phrases(tg_id=tg_id, data='phrases_ads')

    # Клавиатура с кнопкой закрытия
    Button = InlineKeyboardButton
    a_keyboard = InlineKeyboardMarkup(inline_keyboard=[[Button(text='❌', callback_data='close_ad')]])

    # Выбираем случайное сообщение из messages_1
    msg = await update_msg(msg=choice(messages_1), user=message.from_user, new_media=True)
    msg_timer, msg_text = msg['timer'], msg['text']

    # Отправляем начальное сообщение с таймером
    sent_message = await message.answer_photo(
        photo=msg['media'],
        caption=f"{phrases[0]}: {msg_timer}\n\n{msg_text}"
    )

    # Удаляем исходное сообщение пользователя
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    # Обновляем сообщение каждую секунду
    for i in range(msg_timer - 1, 0, -1):
        try:
            await sent_message.edit_caption(caption=f"{phrases[0]}: {i}\n\n{msg_text}")
            await asyncio.sleep(1)
        except Exception as e:
            if DEBUG:
                print_exc()
            return

    # По окончании таймера выводим окончательное сообщение с кнопкой закрытия
    await sent_message.edit_caption(caption=f'{msg_text}\n\n{phrases[2]}', reply_markup=a_keyboard)

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

    phrases = await get_user_language_phrases(tg_id=tg_id, data='phrases_balance')

    text = f'{phrases[0]}: {tokens}'
    # Отправляем сообщение пользователю
    await send_func(message=message, text=text)


@router.message(Command("ref"))
async def get_referral_link(message: Message):
    from special.decorate_text import link

    tg_id = message.from_user.id
    bot_username = (await bot.get_me()).username

    phrases = await get_user_language_phrases(tg_id=tg_id, data='phrases_referral')

    # Генерируем реферальную ссылку
    ref_link = f'https://t.me/{bot_username}?start={tg_id}'
    ref_link = link(text=phrases[0], text_link=ref_link)
    text = f"{phrases[1]} {ref_link}."

    # Отправляем сообщение с реферальной ссылкой
    await send_func(message=message, text=text)


@router.message(Command("buy"))
async def buy(message: Message):
    tg_id = message.from_user.id

    # Получаем информацию о пользователе, проверяя наличие по tg_id
    user = await db(table=0, filters={1: ('==', tg_id)}, method=Method.COUNT, data=0)
    if not user:
        return


    phrases = await get_user_language_phrases(tg_id=tg_id, data='phrases_buy')

    Button = InlineKeyboardButton
    a_keyboard = InlineKeyboardMarkup(inline_keyboard=[[Button(text=phrases[0], pay=True)],
                                                       [Button(text='❌', callback_data='close')]])
    sent_message = await message.answer_invoice(
        title=phrases[1],
        description=phrases[2],
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

    # Обновляем поле 'premium' (9) для пользователя
    await db(
        table=3,
        filters={1: ('==', tg_id)},
        data={9: 1},
        operation=Func.UPDATE
    )

    # Подтверждаем предварительный запрос оплаты
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def on_successful_payment(message: Message):
    from datetime import datetime

    tg_id = message.from_user.id

    # Пытаемся удалить сообщение об успешной оплате
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception as e:
        if DEBUG:
            print_exc()

    # Добавляем запись о транзакции в базу данных (таблица Transactions)
    await db(
        table=4,
        data={1: tg_id, 10: message.successful_payment.telegram_payment_charge_id, 13: datetime.now()},
        operation=Func.ADD
    )

    phrases = await get_user_language_phrases(tg_id=tg_id, data='phrases_successful_payment')

    text = f'{phrases[0]}: {message.successful_payment.telegram_payment_charge_id}.\n{phrases[1]}'

    # Отправляем сообщение с информацией о транзакции
    await send_func(message=message, text=text)


@router.message(Command("refund"))
async def refund(message: Message, command: CommandObject):
    from datetime import datetime


    tg_id = message.from_user.id
    transaction_id = command.args

    phrases = await get_user_language_phrases(tg_id=tg_id, data='phrases_refund')


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
                            # Осуществляем возврат средств
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


@router.message(Command("member"))
async def member(message: Message):
    from special.special_func import check_subscription
    from special.decorate_text import exp_bl


    """
    Обработчик команды /member.
    Проверяет подписку пользователя на несколько каналов и отправляет ответ.
    """
    tg_id = message.from_user.id  # ID пользователя, отправившего команду
    subscription_results = await check_subscription(tg_id)

    phrases = await get_user_language_phrases(tg_id=tg_id, data='phrases_member')

    # Проверка подписки на все каналы
    if all(subscription_results.values()):
        await send_func(message=message, text=phrases[0])
    else:
        # Сообщаем пользователю, на какие каналы он не подписан
        not_subscribed_channels = [channel for channel, subscribed in subscription_results.items() if not subscribed]
        not_subscribed_list = "\n".join(not_subscribed_channels)
        not_subscribed_list = exp_bl(not_subscribed_list)
        await send_func(message=message, text=f'{phrases[0]}\n{not_subscribed_list}\n')


@router.message(Command("info"))
async def info(message: Message):
    tg_id = message.from_user.id

    phrases = await get_user_language_phrases(tg_id=tg_id, data='phrases_info')

    # Отправляем сообщение с реферальной ссылкой
    await send_func(message=message, text=phrases)


@router.message(Command("code"))
async def code(message: Message, command: CommandObject):
    """
    Обработчик команды /code для работы с промокодами.

    Поддерживаемые команды:
    - /code create <код> <токены> <количество>: Создает заданное количество промокодов с указанным количеством токенов (доступно только для администратора).
    - /code delete <код>: Удаляет все промокоды с указанным кодом (доступно только для администратора).
    - /code <код>: Активирует промокод для пользователя, если он еще не был использован.

    Параметры:
    - message: Объект сообщения Telegram.
    - command: Объект команды, содержащий аргументы.
    """
    if command.args:
        args = command.args.split()
    else:
        args = list()
    tg_id = message.from_user.id

    # Получение фраз на основе языка пользователя
    phrases = await get_user_language_phrases(tg_id=tg_id, data='phrases_code')

    if len(args) >= 1:
        action = args[0]

        # Команда для создания промокодов
        if action == "create" and len(args) == 4 and tg_id in ADMINS:
            promo_code = args[1]
            value = int(args[2])
            count = int(args[3])

            # Создание указанного количества промокодов
            for _ in range(count):
                await db(table=1, data={1: '', 7: promo_code, 14: value}, operation=Func.ADD)
            await send_func(message=message, text=f"{phrases[0]} {count} {phrases[1]} {promo_code}, {phrases[2]} {value} {phrases[3]}.")

        # Команда для удаления промокодов
        elif action == "delete" and len(args) == 2 and tg_id in ADMINS:
            promo_code = args[1]

            # Удаление всех промокодов с указанным кодом
            await db(table=1, filters={7: ('==', promo_code)}, operation=Func.DELETE)
            await send_func(message=message, text=f"{phrases[4]} {promo_code} {phrases[5]}.")

        # Команда для активации промокода
        elif len(args) == 1:
            promo_code = args[0]

            # Проверка, использовал ли пользователь данный промокод
            user_code_exists = await db(table=1, filters={1: ('==', tg_id), 7: ('==', promo_code)}, method=Method.COUNT, data=0)
            if user_code_exists:
                await send_func(message=message, text=phrases[6])
                return

            # Поиск промокода в базе данных
            promo_code_entry = await db(table=1, filters={7: ('==', promo_code), 1: ('==', '')}, method=Method.FIRST, data=[0, 14])
            if promo_code_entry:
                promo_code_id, value = promo_code_entry

                # Проверка, если все одинаковые коды уже использованы
                all_codes_used = await db(table=1, filters={7: ('==', promo_code), 1: ('==', '')}, method=Method.COUNT, data=0) - 1
                if not all_codes_used:
                    # Удаление всех одинаковых промокодов, если они уже были использованы всеми
                    await db(table=1, filters={7: ('==', promo_code)}, operation=Func.DELETE)

                # Добавление токенов пользователю и пометка промокода
                await db(table=1, filters={0: ('==', promo_code_id)}, data={1: tg_id}, operation=Func.UPDATE)
                await send_func(message=message, text=f"{phrases[7]} {promo_code} {phrases[8]} {value} {phrases[3]}.")
            else:
                # Сообщение, если промокод не найден или уже использован
                await send_func(message=message, text=phrases[9])
        else:
            # Сообщение об ошибке в команде
            await send_func(message=message, text=phrases[10])
    else:
        # Сообщение об отсутствии аргументов
        await send_func(message=message, text=phrases[10])


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
