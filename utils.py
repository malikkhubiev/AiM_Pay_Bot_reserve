from config import (
    SECRET_CODE
)
import logging as log
import requests as req
from requests.exceptions import RequestException
from loader import *
# Установим базовый уровень логирования
log.basicConfig(level=log.DEBUG)
logger = log.getLogger(__name__)

def send_request(url, method="GET", headers=None, **kwargs):
    if headers is None:
        headers = {}
    headers["X-Secret-Code"] = SECRET_CODE  # Добавляем заголовок
    try:
        if method.upper() == "POST":
            response = req.post(url, headers=headers, **kwargs)
        elif method.upper() == "GET":
            response = req.get(url, headers=headers, **kwargs)
        elif method.upper() == "PUT":
            response = req.put(url, headers=headers, **kwargs)
        elif method.upper() == "DELETE":
            response = req.delete(url, headers=headers, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        # Проверяем статус ответа
        response.raise_for_status()
        return response.json()  # Возвращаем JSON-ответ
    except RequestException as e:
        # Логирование ошибок
        logger.error(f"HTTP запрос завершился с ошибкой: {e}")
        return None