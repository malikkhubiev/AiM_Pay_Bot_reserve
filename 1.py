import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor

bot = Bot(token="YOUR_BOT_TOKEN")
dp = Dispatcher(bot)

tracking_id = "UA-XXXXXXXXX-X"  # Ваш Tracking ID в Google Analytics

# Функция для отправки события в Google Analytics
def send_event_to_google_analytics(telegram_id, event_category, event_action, event_label=""):
    payload = {
        "v": "1",                  # Версия
        "tid": tracking_id,        # Ваш Tracking ID в Google Analytics
        "cid": telegram_id,            # Уникальный ID пользователя (можно использовать user_id)
        "t": "event",              # Тип события
        "ec": event_category,      # Категория события (например, "Button")
        "ea": event_action,        # Действие события (например, "Click")
        "el": event_label          # Метка события (например, "Referral Link")
    }
    requests.post("https://www.google-analytics.com/collect", data=payload)

# Создание кнопок
def create_inline_buttons():
    keyboard = InlineKeyboardMarkup(row_width=1)
    referral_button = InlineKeyboardButton("Получить реферальную ссылку", callback_data="get_referral")
    help_button = InlineKeyboardButton("Посмотреть помощь", callback_data="help")
    keyboard.add(referral_button, help_button)
    return keyboard

# Обработчик команды /start
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Привет! Выберите действие:", reply_markup=create_inline_buttons())

# Обработчик кнопки "Получить реферальную ссылку"
@dp.callback_query_handler(lambda c: c.data == "get_referral")
async def process_referral(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    
    # Отправка события в Google Analytics
    send_event_to_google_analytics(user_id, "Button", "Click", "Referral Link")

    # Ваш код для получения и отправки реферальной ссылки
    referral_link = f"https://t.me/your_bot?start={user_id}"
    await bot.send_message(callback_query.from_user.id, f"Ваша реферальная ссылка: {referral_link}")

# Обработчик кнопки "Посмотреть помощь"
@dp.callback_query_handler(lambda c: c.data == "help")
async def process_help(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    
    # Отправка события в Google Analytics
    send_event_to_google_analytics(user_id, "Button", "Click", "Help")

    # Ваш код для отправки информации о помощи
    await bot.send_message(callback_query.from_user.id, "Как я могу помочь? Напишите ваш запрос.")
    
if __name__ == "__main__":
    executor.start_polling(dp)
