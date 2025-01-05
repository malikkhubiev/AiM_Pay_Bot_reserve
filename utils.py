from config import (
    SECRET_CODE
)
import logging as log
import httpx
from loader import *
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler
from time import time

log.basicConfig(level=log.DEBUG)
logger = log.getLogger(__name__)

async def send_request(url, method="GET", headers=None, **kwargs):
    if headers is None:
        headers = {}
    headers["X-Secret-Code"] = SECRET_CODE  # Добавляем заголовок

    async with httpx.AsyncClient() as client:
        try:
            # Выбор метода запроса
            if method.upper() == "POST":
                response = await client.post(url, headers=headers, **kwargs)
            elif method.upper() == "GET":
                response = await client.get(url, headers=headers, **kwargs)
            elif method.upper() == "PUT":
                response = await client.put(url, headers=headers, **kwargs)
            elif method.upper() == "DELETE":
                response = await client.delete(url, headers=headers, **kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # Проверяем статус ответа
            response.raise_for_status()  # Это автоматически вызывает исключение для ошибок статуса
            return response.json()  # Возвращаем JSON-ответ

        except httpx.RequestError as e:
            # Логирование ошибок запроса
            logger.error(f"Ошибка при выполнении запроса: {e}")
            return {"status": "error", "message": "Ошибка при подключении к серверу."}
        except httpx.HTTPStatusError as e:
            # Логирование ошибок HTTP-статуса
            logger.error(f"HTTP статус-код {e.response.status_code}: {e}")
            return {"status": "error", "message": f"Сервер вернул ошибку: {e.response.status_code}."}
        except Exception as e:
            # Логирование других ошибок
            logger.error(f"Неизвестная ошибка: {e}")
            return {"status": "error", "message": "Произошла ошибка."}

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