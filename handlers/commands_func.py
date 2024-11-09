from aiogram.exceptions import TelegramBadRequest

from database.db_operation import db
from resources.keyboards import close_ad_keyboard, close_keyboard, language_keyboard

from utils.msg_func import update_msg

from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    LabeledPrice,
    PreCheckoutQuery,
)

from app.consts import DEBUG, ADMINS, OWNER
from traceback import print_exc

from app.bot import bot

from settings.special_func import return_variable, get_user_language_phrases

import asyncio

from database.core.db_consts import Func, Method, Tables, Columns, Operators

from resources.buttons import *

router = Router()

sent_messages = list()


@router.message(Command("save"))
async def save(message: Message) -> None:
    """
    Обработчик команды /save.

    Сохраняет текущее состояние пользователя и отправляет обновленное сообщение.
    Если пользователь не существует, инициирует процедуру регистрации через функцию start.
    """
    tg_id: int = message.from_user.id

    # Проверяем, существует ли пользователь в базе данных
    user = await db(
        table=Tables.USER,
        filters={Columns.TG_ID: (Operators.EQ, tg_id)},
        method=Method.COUNT,
        data=Columns.ID,
    )
    if not user:
        await start(message=message)

    # Получаем идентификатор отправленного сообщения
    sent_message_id = await db(
        table=Tables.GAME,
        filters={Columns.TG_ID: (Operators.EQ, tg_id)},
        data=Columns.SENT_MESSAGE_ID,
        method=Method.FIRST,
    )

    # Пытаемся удалить старое сообщение пользователя
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=sent_message_id)
    except Exception:
        pass

    # Получаем идентификаторы текущего сообщения и его части
    message_id, msg_id = await db(
        filters={Columns.TG_ID: (Operators.EQ, tg_id)},
        data=[Columns.MESSAGE_ID, Columns.MSG_ID],
        method=Method.FIRST,
    )

    # Получаем содержимое сообщения для текущего этапа
    message_var = await return_variable(f"message_0_{message_id}")
    msg = message_var[msg_id]

    # Получаем медиафайл и его расширение
    media_file = await return_variable(msg["media"])
    media_extension = media_file.split(".")[1]

    # Обновляем сообщение для отправки
    if "keyboard" not in msg:
        msg["keyboard"] = "basic_0"
    msg = await update_msg(msg=msg, user=message.from_user, new_media=True)

    # Отправляем сообщение с медиафайлом
    if media_extension in ["png", "jpeg", "jpg"]:
        sent_message = await message.answer_photo(
            photo=msg["media"], caption=msg["text"], reply_markup=msg["keyboard"]
        )
    sent_messages.append((sent_message.message_id, tg_id))

    # Обновляем идентификатор отправленного сообщения в базе данных
    await db(
        table=Tables.GAME,
        filters={Columns.TG_ID: (Operators.EQ, tg_id)},
        data={Columns.SENT_MESSAGE_ID: sent_message.message_id},
        operation=Func.UPDATE,
    )

    # Ожидаем сутки и удаляем сообщение
    await del_message(sent_message, message)


@router.message(Command("start"))
async def start(message: Message, command: CommandObject) -> None:
    """
    Обработчик команды /start.

    Регистрирует нового пользователя или обновляет данные существующего.
    Обрабатывает реферальные ссылки и начисляет бонусные токены рефереру.
    Отправляет приветственное сообщение и сохраняет его идентификатор.
    """
    from resources.messages.messages_0 import message_0_0

    tg_id: int = message.from_user.id

    # Проверяем, существует ли пользователь в базе данных
    user = await db(
        table=Tables.USER,
        filters={Columns.TG_ID: (Operators.EQ, tg_id)},
        method=Method.COUNT,
        data=Columns.ID,
    )
    if user:
        await save(message=message)
        return

    referral_link = command.args
    if (
        referral_link
        and referral_link.isdigit()
        and await db(
            table=Tables.USER,
            filters={Columns.TG_ID: (Operators.EQ, int(referral_link))},
            method=Method.COUNT,
            data=Columns.ID,
        )
    ):
        tokens = await db(
            table=Tables.GAME,
            filters={Columns.TG_ID: (Operators.EQ, int(referral_link))},
            data=Columns.TOKENS,
            method=Method.FIRST,
        )
        await db(
            table=Tables.GAME,
            filters={Columns.TG_ID: (Operators.EQ, int(referral_link))},
            data={Columns.TOKENS: tokens + 3},
            operation=Func.UPDATE,
        )

    # Создаем новую запись пользователя
    await db(table=Tables.USER, data={Columns.TG_ID: tg_id}, operation=Func.ADD)

    # Отправляем приветственное сообщение пользователю
    msg = await update_msg(msg=message_0_0[0], user=message.from_user, new_media=True)
    sent_message = await message.answer_photo(
        photo=msg["media"], caption=msg["text"], reply_markup=msg["keyboard"]
    )
    sent_messages.append((sent_message.message_id, tg_id))

    # Создаем новую запись в таблице Game
    await db(
        table=Tables.GAME,
        data={Columns.TG_ID: tg_id, Columns.SENT_MESSAGE_ID: sent_message.message_id},
        operation=Func.ADD,
    )

    # Удаляем исходное сообщение пользователя
    await del_message(sent_message, message)


@router.message(Command("ads"))
async def get_ads(message: Message) -> None:
    """
    Обработчик команды /ads.

    Отправляет пользователю рекламное сообщение с таймером.
    После завершения таймера предлагает пользователю закрыть сообщение.
    """
    from random import choice
    from resources.messages.messages_1 import messages_1

    tg_id: int = message.from_user.id

    phrases = await get_user_language_phrases(tg_id=tg_id, data="phrases_ads")

    # Выбираем случайное рекламное сообщение
    msg = await update_msg(
        msg=choice(messages_1), user=message.from_user, new_media=True
    )
    msg_timer, msg_text = msg["timer"], msg["text"]

    # Отправляем начальное сообщение с таймером
    sent_message = await message.answer_photo(
        photo=msg["media"],
        caption=f"{phrases[0]}: {msg_timer}\n\n{msg_text}",
    )

    # Удаляем исходное сообщение пользователя
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    # Обновляем сообщение каждую секунду
    for i in range(msg_timer - 1, 0, -1):
        try:
            await sent_message.edit_caption(
                caption=f"{phrases[0]}: {i}\n\n{msg_text}"
            )
            await asyncio.sleep(1)
        except Exception:
            return

    # По окончании таймера добавляем кнопку закрытия
    await sent_message.edit_caption(
        caption=f"{msg_text}\n\n{phrases[2]}", reply_markup=close_ad_keyboard
    )

    # Ждем 24 часа и удаляем сообщение
    await asyncio.sleep(24 * 60 * 60)
    try:
        await bot.delete_message(
            chat_id=sent_message.chat.id, message_id=sent_message.message_id
        )
    except Exception:
        if DEBUG:
            print_exc()


@router.message(Command("balance"))
async def get_balance(message: Message) -> None:
    """
    Обработчик команды /balance.

    Отправляет пользователю информацию о текущем балансе токенов.
    """
    tg_id: int = message.from_user.id

    # Получаем количество токенов пользователя
    tokens = await db(
        table=Tables.GAME,
        filters={Columns.TG_ID: (Operators.EQ, tg_id)},
        data=Columns.TOKENS,
        method=Method.FIRST,
    )

    phrases = await get_user_language_phrases(tg_id=tg_id, data="phrases_balance")

    text = f"{phrases[0]}: {tokens}"
    # Отправляем сообщение пользователю
    await send_func(message=message, text=text)


@router.message(Command("ref"))
async def get_referral_link(message: Message) -> None:
    """
    Обработчик команды /ref.

    Генерирует и отправляет пользователю его реферальную ссылку.
    """
    from utils.decorate_text import link

    tg_id: int = message.from_user.id
    bot_username = (await bot.get_me()).username

    phrases = await get_user_language_phrases(tg_id=tg_id, data="phrases_referral")

    # Генерируем реферальную ссылку
    ref_link = f"https://t.me/{bot_username}?start={tg_id}"
    ref_link = link(text=phrases[0], text_link=ref_link)
    text = f"{phrases[1]} {ref_link}."

    # Отправляем сообщение с реферальной ссылкой
    await send_func(message=message, text=text)


@router.message(Command("buy"))
async def buy(message: Message) -> None:
    """
    Обработчик команды /buy.

    Отправляет пользователю счет на оплату для приобретения премиум доступа.
    """
    tg_id: int = message.from_user.id

    # Проверяем, существует ли пользователь
    user = await db(
        table=Tables.USER,
        filters={Columns.TG_ID: (Operators.EQ, tg_id)},
        method=Method.COUNT,
        data=Columns.ID,
    )
    if not user:
        return

    phrases = await get_user_language_phrases(tg_id=tg_id, data="phrases_buy")

    Button = InlineKeyboardButton
    a_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [Button(text=phrases[0], pay=True)],
            [close_btn],
        ]
    )
    sent_message = await message.answer_invoice(
        title=phrases[1],
        description=phrases[2],
        prices=[LabeledPrice(label="XTR", amount=1)],
        provider_token="",
        payload="no_ads",
        currency="XTR",
        reply_markup=a_keyboard,
    )

    await del_message(sent_message, message)


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery) -> None:
    """
    Обработчик предварительного запроса оплаты.

    Обновляет статус премиум доступа пользователя и подтверждает платеж.
    """
    tg_id: int = pre_checkout_query.from_user.id

    # Обновляем статус премиум доступа в базе данных
    await db(
        table=Tables.GAME,
        filters={Columns.TG_ID: (Operators.EQ, tg_id)},
        data={Columns.PREMIUM: 1},
        operation=Func.UPDATE,
    )

    # Подтверждаем предварительный запрос оплаты
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def on_successful_payment(message: Message) -> None:
    """
    Обработчик успешного платежа.

    Сохраняет информацию о транзакции и уведомляет пользователя.
    """
    from datetime import datetime

    tg_id: int = message.from_user.id

    # Добавляем запись о транзакции в базу данных
    await db(
        table=Tables.TRANSACTIONS,
        data={
            Columns.TRANSACTIONS_ID: message.successful_payment.telegram_payment_charge_id,
            Columns.DATE: datetime.now(),
        },
        operation=Func.ADD,
    )

    phrases = await get_user_language_phrases(
        tg_id=tg_id, data="phrases_successful_payment"
    )

    text = f"{phrases[0]}: {message.successful_payment.telegram_payment_charge_id}.\n{phrases[1]}"

    # Отправляем сообщение с информацией о транзакции
    await send_func(message=message, text=text)


@router.message(Command("refund"))
async def refund(message: Message, command: CommandObject) -> None:
    """
    Обработчик команды /refund.

    Позволяет пользователю запросить возврат средств за последние 60 минут после покупки.
    """
    from datetime import datetime

    tg_id: int = message.from_user.id
    transaction_id = command.args

    phrases = await get_user_language_phrases(tg_id=tg_id, data="phrases_refund")

    if not transaction_id:
        text = phrases[0]  # Отсутствует ID транзакции
    else:
        try:
            # Получаем дату транзакции
            date = await db(
                table=Tables.TRANSACTIONS,
                filters={Columns.TRANSACTIONS_ID: (Operators.EQ, transaction_id)},
                data=Columns.DATE,
                method=Method.FIRST,
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
                        table=Tables.GAME,
                        filters={Columns.TG_ID: (Operators.EQ, tg_id)},
                        data=Columns.REFUND,
                        method=Method.FIRST,
                    )
                    if refund_status:
                        text = phrases[5]  # Возврат уже был обработан
                    else:
                        # Обновляем статус возврата в базе данных
                        success_update = await db(
                            table=Tables.GAME,
                            filters={Columns.TG_ID: (Operators.EQ, tg_id)},
                            data={Columns.REFUND: True},
                            operation=Func.UPDATE,
                        )
                        # Обновляем статус премиум доступа
                        await db(
                            table=Tables.GAME,
                            filters={Columns.TG_ID: (Operators.EQ, tg_id)},
                            data={Columns.PREMIUM: 0},
                            operation=Func.UPDATE,
                        )
                        if success_update:
                            # Осуществляем возврат средств
                            await bot.refund_star_payment(
                                user_id=tg_id,
                                telegram_payment_charge_id=transaction_id,
                            )
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
async def member(message: Message) -> None:
    """
    Обработчик команды /member.

    Проверяет подписку пользователя на обязательные каналы и уведомляет о результате.
    """
    from settings.special_func import check_subscription
    from utils.decorate_text import exp_bl

    tg_id: int = message.from_user.id
    subscription_results = await check_subscription(tg_id)

    phrases = await get_user_language_phrases(tg_id=tg_id, data="phrases_member")

    # Проверка подписки на все каналы
    if all(subscription_results.values()) and True in subscription_results.values():
        await send_func(message=message, text=phrases[0])
    else:
        # Список каналов, на которые пользователь не подписан
        not_subscribed_channels = [
            channel
            for channel, subscribed in subscription_results.items()
            if not subscribed
        ]
        not_subscribed_list = "\n".join(not_subscribed_channels)
        not_subscribed_list = exp_bl(not_subscribed_list)
        await send_func(
            message=message,
            text=f"{phrases[1]}\n{not_subscribed_list}\n",
        )


@router.message(Command("info"))
async def info(message: Message) -> None:
    """
    Обработчик команды /info.

    Отправляет пользователю информационное сообщение.
    """
    tg_id: int = message.from_user.id

    phrases = await get_user_language_phrases(tg_id=tg_id, data="phrases_info")

    # Отправляем информационное сообщение
    await send_func(message=message, text=phrases)


@router.message(Command("code"))
async def code(message: Message, command: CommandObject) -> None:
    """
    Обработчик команды /code для работы с промокодами.

    Поддерживает создание, удаление и активацию промокодов.
    """
    if command.args:
        args = command.args.split()
    else:
        args = []
    tg_id: int = message.from_user.id

    phrases = await get_user_language_phrases(tg_id=tg_id, data="phrases_code")

    if len(args) >= 1:
        action = args[0]

        # Создание промокодов (только для администраторов)
        if action == "create" and len(args) == 4 and tg_id in ADMINS:
            promo_code = args[1]
            value = int(args[2])
            count = int(args[3])

            # Создаем указанное количество промокодов
            for _ in range(count):
                await db(
                    table=Tables.PROMO,
                    data={
                        Columns.TG_ID: "",
                        Columns.CODE: promo_code,
                        Columns.VALUE: value,
                    },
                    operation=Func.ADD,
                )
            await send_func(
                message=message,
                text=f"{phrases[0]} {count} {phrases[1]} {promo_code}, {phrases[2]} {value} {phrases[3]}.",
            )

        # Удаление промокодов (только для администраторов)
        elif action == "delete" and len(args) == 2 and tg_id in ADMINS:
            promo_code = args[1]

            # Удаляем все промокоды с указанным кодом
            await db(
                table=Tables.PROMO,
                filters={Columns.CODE: (Operators.EQ, promo_code)},
                operation=Func.DELETE,
            )
            await send_func(
                message=message,
                text=f"{phrases[4]} {promo_code} {phrases[5]}.",
            )

        # Активация промокода пользователем
        elif len(args) == 1:
            promo_code = args[0]

            # Проверяем, использовал ли пользователь этот промокод ранее
            user_code_exists = await db(
                table=Tables.PROMO,
                filters={
                    Columns.TG_ID: (Operators.EQ, tg_id),
                    Columns.CODE: (Operators.EQ, promo_code),
                },
                method=Method.COUNT,
                data=Columns.ID,
            )
            if user_code_exists:
                await send_func(message=message, text=phrases[6])
                return

            # Поиск доступного промокода
            promo_code_entry = await db(
                table=Tables.PROMO,
                filters={
                    Columns.CODE: (Operators.EQ, promo_code),
                    Columns.TG_ID: (Operators.EQ, ""),
                },
                method=Method.FIRST,
                data=[Columns.ID, Columns.VALUE],
            )
            if promo_code_entry:
                promo_code_id, value = promo_code_entry

                # Проверяем, остались ли доступные промокоды с этим кодом
                all_codes_used = (
                    await db(
                        table=Tables.PROMO,
                        filters={
                            Columns.CODE: (Operators.EQ, promo_code),
                            Columns.TG_ID: (Operators.EQ, ""),
                        },
                        method=Method.COUNT,
                        data=Columns.ID,
                    )
                    - 1
                )
                if not all_codes_used:
                    # Удаляем все использованные промокоды
                    await db(
                        table=Tables.PROMO,
                        filters={Columns.CODE: (Operators.EQ, promo_code)},
                        operation=Func.DELETE,
                    )

                # Обновляем промокод, связывая его с пользователем
                await db(
                    table=Tables.PROMO,
                    filters={Columns.ID: (Operators.EQ, promo_code_id)},
                    data={Columns.TG_ID: tg_id},
                    operation=Func.UPDATE,
                )
                await send_func(
                    message=message,
                    text=f"{phrases[7]} {promo_code} {phrases[8]} {value} {phrases[3]}.",
                )
            else:
                # Промокод не найден или уже использован
                await send_func(message=message, text=phrases[9])
        else:
            # Неверный формат команды
            await send_func(message=message, text=phrases[10])
    else:
        # Отсутствуют аргументы команды
        await send_func(message=message, text=phrases[10])


@router.message(Command("shutdown"))
async def shutdown(message: Message) -> None:
    """
    Обработчик команды /shutdown.

    Отключает бота и завершает все сессии. Доступно только владельцу бота.
    """
    from main import on_shutdown

    tg_id: int = message.from_user.id

    # Проверяем, что команду отправил владелец бота
    if tg_id != OWNER:
        return

    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception:
        pass

    # Отправляем уведомление всем пользователям перед отключением
    if not DEBUG:
        for _, user_id in sent_messages:
            try:
                phrase = await get_user_language_phrases(
                    tg_id=user_id, data="phrases_bot_end"
                )
                await bot.send_message(user_id, phrase, reply_markup=close_keyboard)
                await asyncio.sleep(0.1)
            except Exception:
                pass

    time_sleep = 5
    await asyncio.sleep(time_sleep)
    await on_shutdown()


@router.message(Command("language"))
async def language(message: Message) -> None:
    """
    Обработчик команды /lang.

    Отправляет пользователю сообщение с выбором языка.
    """
    from settings.special_func import get_user_language_phrases  # Импортируйте при необходимости

    tg_id = message.from_user.id

    phrase = await get_user_language_phrases(tg_id=tg_id, data="phrases_language")
    await send_func(message=message, text=phrase, keyboard=language_keyboard)



async def send_func(
    message: Message, text: str, keyboard: InlineKeyboardMarkup = close_keyboard
) -> None:
    """
    Вспомогательная функция для отправки сообщений пользователю.

    Отправляет сообщение и планирует его удаление через 24 часа.
    """

    sent_message = await message.answer(text=text, reply_markup=keyboard)

    await del_message(sent_message, message)


async def del_message(sent_message: Message, message: Message) -> None:
    """
    Вспомогательная функция для удаления сообщений.

    Удаляет исходное сообщение пользователя и отправленное ботом сообщение через 24 часа.
    """
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception:
        pass

    await asyncio.sleep(24 * 60 * 60)

    try:
        await bot.delete_message(
            chat_id=sent_message.chat.id, message_id=sent_message.message_id
        )
    except Exception:
        pass
