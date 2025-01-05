import httpx
import uuid
from config import (
    GOOGLE_ANALYTICS_STEAM_ID,
    GOOGLE_ANALYTICS_API_SECRET_KEY
)

def send_event_to_ga4(telegram_id, event_category, event_action, event_label=None, event_value=None):
    # Получаем уникальный идентификатор пользователя (cid)
    cid = str(telegram_id)  # или можно использовать UUID: str(uuid.uuid4())

    # Ваш идентификатор потока данных GA4
    stream_id = GOOGLE_ANALYTICS_STEAM_ID

    # Формируем запрос
    url = "https://www.google-analytics.com/mp/collect"
    params = {
        "measurement_id": stream_id,
        "api_secret": GOOGLE_ANALYTICS_API_SECRET_KEY,  # Получите API секрет на странице настроек в GA4
        "client_id": cid,
        "events": [
            {
                "name": event_category,  # Категория события (например, "interaction")
                "params": {
                    "action": event_action,  # Действие (например, "click")
                    "label": event_label,  # Метка события
                    "value": event_value  # Значение события
                }
            }
        ]
    }
    
    # Отправляем запрос
    with httpx.Client() as client:
        response = client.post(url, json=params)
        if response.status_code == 204:
            print("Событие успешно отправлено в GA4.")
        else:
            print(f"Ошибка при отправке события: {response.status_code}, {response.text}")
