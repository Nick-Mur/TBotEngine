from aiogram import BaseMiddleware
from aiogram.types import Update


class IgnoreOldMessagesMiddleware(BaseMiddleware):
    def __init__(self, bot_start_time):
        super().__init__()
        self.bot_start_time = bot_start_time

    async def __call__(self, handler, event: Update, data):
        message_date = None

        if event.message:
            message_date = event.message.date
        elif event.edited_message:
            message_date = event.edited_message.date
        # Добавьте другие типы событий, если необходимо

        if message_date and message_date < self.bot_start_time:
            return
        return await handler(event, data)
