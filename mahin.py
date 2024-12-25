import os
import asyncio
import nest_asyncio
from loader import *
from utils import *
from web_server import start_web_server
from button_handlers import *

from config import (
    SERVER_URL,
    START_VIDEO_URL
)

nest_asyncio.apply()

async def start_polling():
    await dp.start_polling()

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