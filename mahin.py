import os
import asyncio
import nest_asyncio
from loader import *
from utils import *
from web_server import start_web_server

from config import (
    SERVER_URL,
    START_VIDEO_URL
)

nest_asyncio.apply()

async def start_polling():
    await dp.start_polling()

# Главное меню с кнопками
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    log.info(f"Получена команда /start от {message.from_user.id}")

    start_url = SERVER_URL + "/start"
    user_data = {
        "telegram_id": message.from_user.id,
        "username": message.from_user.username or message.from_user.first_name,
        "referrer_id": message.text.split()[1] if len(message.text.split()) > 1 else ""
    }
    await message.answer(f"user_data {user_data}")
    keyboard = InlineKeyboardMarkup(row_width=1)
    try:
        response = send_request(
            start_url,
            method="POST",
            json=user_data
        )
        await message.answer(f"response {response}")
        if response["type"] == "temp_user":
            await message.answer(f"temp")
            keyboard.add(
                InlineKeyboardButton("Начало работы", callback_data='getting_started'),
                InlineKeyboardButton("Документы", callback_data='pay_course'),
            )
            await message.answer(f"sendMessage")
            await bot.send_message(
                chat_id=message.chat.id,
                text="Добро пожаловать! Для начала работы с ботом вам нужно согласиться с политикой конфиденциальности и публичной офертой. Нажимая кнопку «Начало работы», вы подтверждаете своё согласие.",
                reply_markup=keyboard
            )
        elif response["type"] == "user":
            if response["to_show"] == "pay_course":
                keyboard.add(
                    InlineKeyboardButton("Оплатить курс", callback_data='pay_course'),
                )
            keyboard.add(
                InlineKeyboardButton("Заработать на новых клиентах", callback_data='earn_new_clients')
            )
            await bot.send_video(
                chat_id=message.chat.id,
                video=START_VIDEO_URL,
                caption="Добро пожаловать! Здесь Вы можете оплатить курс и заработать на привлечении новых клиентов.",
                reply_markup=keyboard
            )

    except RequestException as e:
        logger.error("Ошибка при запросе к серверу: %s", e)
        await bot.send_message(e.chat.id, "Ошибка при проверке регистрации. Пожалуйста, попробуйте позже.")
        return
    except KeyError:
        logger.warning("Пользователь не зарегистрирован в базе данных.")
        await bot.send_message(e.chat.id, "Сначала нажмите /start для регистрации.")
        return

@dp.chat_member_handler()
async def check_user_in_db(event: ChatMemberUpdated):
    try:
        # Проверяем, что пользователь присоединился к группе
        if event.new_chat_member.status == 'member':  # Пользователь присоединился
            telegram_id = event.new_chat_member.user.id
            
            # Проверяем, есть ли пользователь в базе данных
            check_user_url = SERVER_URL + "/check_user"
            user_data = {
                "telegram_id": telegram_id
            }
            try:
                response = send_request(
                    check_user_url,
                    method="POST",
                    json=user_data
                )
                
                # Если ответ пустой или нет такого пользователя, кикаем
                if response.get("user"):
                    user_id = response["user"]["id"]
                    log.info(f"Пользователь с ID {user_id} добавлен в группу")
                else:
                    user_id = telegram_id
                    await bot.kick_chat_member(event.chat.id, user_id)  # Кикаем пользователя
                    await bot.unban_chat_member(event.chat.id, user_id)  # Разбаниваем (чтобы не остаться заблокированным)
                    log.info(f"Пользователь с ID {user_id} был исключён из группы, так как не найден в базе данных")
                    return
            except RequestException as e:
                logger.error("Ошибка при запросе к серверу: %s", e)
                await bot.send_message(event.chat.id, "Ошибка при проверке регистрации. Пожалуйста, попробуйте позже.")
                return
            except KeyError:
                logger.warning("Пользователь не зарегистрирован в базе данных.")
                await bot.send_message(event.chat.id, "Сначала нажмите /start для регистрации.")
                return
    except Exception as e:
        logger.error(f"Ошибка при обработке события: {e}")

USE_RENDER = os.getenv("USE_RENDER", "false").lower() == "true"

if __name__ == "__main__":
    if USE_RENDER:
        # Render: запускаем веб-сервер
        asyncio.run(start_web_server())
    else:
        # Локально: запускаем polling
        asyncio.run(start_polling())