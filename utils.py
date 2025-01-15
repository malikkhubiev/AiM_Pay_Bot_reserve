import logging as log
from loader import *
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler
from time import time

log.basicConfig(level=log.DEBUG)
logger = log.getLogger(__name__)

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit=1):
        super().__init__()
        self.rate_limit = rate_limit
        self.user_timestamps = {}

    async def on_pre_process_message(self, message: Message, data: dict):
        user_id = message.from_user.id
        current_time = time()

        if user_id not in self.user_timestamps:
            self.user_timestamps[user_id] = current_time
            return
        
        last_time = self.user_timestamps[user_id]
        if current_time - last_time < self.rate_limit:
            await message.answer("Слишком много запросов. Попробуйте позже.")
            raise CancelHandler()

        self.user_timestamps[user_id] = current_time