import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound
from datetime import datetime
from aiohttp import web
import nest_asyncio
from config import (
    API_TOKEN,
    COURSE_AMOUNT,
    REFERRAL_AMOUNT,
    SERVER_URL,
    GROUP_ID,
    TAX_INFO_IMG_URL,
    EARN_NEW_CLIENTS_VIDEO_URL,
    START_VIDEO_URL,
    REPORT_VIDEO_URL,
    REFERRAL_VIDEO_URL
)
import requests
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Установим базовый уровень логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Применяем nest_asyncio для повторного использования цикла событий
nest_asyncio.apply()

# Определение веб-сервера
def web_server():
    async def handle(request):
        # Проверка типа запроса
        response_data = {"message": "pong"}
        return web.json_response(response_data)
    
    async def notify_user(request):
        data = await request.json()
        telegram_id = data.get("telegram_id")
        message_text = data.get("message")

        # Отправляем сообщение пользователю через Telegram
        if telegram_id and message_text:
            await bot.send_message(chat_id=telegram_id, text=message_text)
            return web.json_response({"status": "notification sent"}, status=200)
        return web.json_response({"error": "Invalid data"}, status=400)

    app = web.Application()
    app.router.add_route("HEAD", "/", handle)
    app.router.add_route("GET", "/", handle)
    app.router.add_post("/notify_user", notify_user)
    return app

async def on_start_polling():
    # Настройка веб-сервера с использованием aiohttp
    app = web.AppRunner(web_server())
    await app.setup()

    # Привязка адреса и порта
    bind_address = "0.0.0.0"
    PORT = int(os.getenv("PORT", 8080))
    site = web.TCPSite(app, bind_address, PORT)
    await site.start()

    logging.info(f"Веб-сервер запущен на порту {PORT}")

    # Запуск бота с ожиданием завершения
    await executor.start_polling(dp, skip_updates=True)

# Главное меню с кнопками
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    # мусор
    await message.answer(f"start")

    telegram_id = str(message.from_user.id)
    username = message.from_user.username or message.from_user.first_name

    # мусор
    await message.answer(f"{telegram_id}: telegram_id")
    # мусор
    await message.answer(f"{username}: username")

    # мусор
    await message.answer(f"{message.text}: message.text")
    # мусор
    await message.answer(f"{message.text.split()}: message.text.split()")
    await message.answer(f"{len(message.text.split())}: len(message.text.split())")
    await message.answer(f"{message.text.split()[1]}: message.text.split()[1]")

    # Проверяем, передан ли реферальный ID
    referrer_id = None
    if len(message.text.split()) > 1:
        referrer_id = message.text.split()[1]

    # мусор
    await message.answer(referrer_id)

    register_or_greet_url = SERVER_URL + "/greet"

    # мусор
    await message.answer(register_or_greet_url)
    user_data = {
        "telegram_id": telegram_id,
        "username": username,
        "referrer_id": referrer_id or ""
    }

    # мусор
    await message.answer(f"{user_data}: user_data")

    response = requests.post(register_or_greet_url, json=user_data).json()
    
    # мусор
    await message.answer(f"{response}: response")

    await message.answer(response["message"])

    # Создаем основное меню с кнопками
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("Оплатить курс", callback_data='pay_course'),
    )

    # Проверка, есть ли хотя бы один реферал у пользователя
    telegram_id = str(message.from_user.id)
    check_referrals_url = SERVER_URL + "/check_referrals"
    user_data = {
        "telegram_id": telegram_id,
    }

    response = requests.post(check_referrals_url, json=user_data).json()
    referral_exists = response["has_referrals"]
    keyboard.add(InlineKeyboardButton("Заработать на новых клиентах", callback_data='earn_new_clients'))
    # Включить позже, а сверху выключить
    # if referral_exists:
    #     # Кнопка для заработка на клиентах, если есть хотя бы один реферал
    #     keyboard.add(InlineKeyboardButton("Заработать на новых клиентах", callback_data='earn_new_clients'))
    # else:
    #     # Кнопка, если пользователь еще не оплатил курс
    #     keyboard.add(InlineKeyboardButton("Заработать на новых клиентах (нужно оплатить курс)", callback_data='earn_new_clients_disabled'))
    # Включить позже

    # Отправка видео с приветствием и меню
    await bot.send_video(
        chat_id=message.chat.id,
        video=START_VIDEO_URL,
        caption="Добро пожаловать! Здесь Вы можете оплатить курс и заработать на привлечении новых клиентов.",
        reply_markup=keyboard
    )

@dp.callback_query_handler(lambda c: c.data == 'pay_course')
async def process_pay_course(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.answer("Здесь будет информация о платеже. Нажмите /pay для оплаты.")


@dp.callback_query_handler(lambda c: c.data == 'earn_new_clients')
async def process_earn_new_clients(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("Получить реферальную ссылку", callback_data='get_referral'),
        InlineKeyboardButton("Сформировать отчёт о заработке", callback_data='generate_report'),
        InlineKeyboardButton("Налоги", callback_data='tax_info')
    )

    # Отправка изображения
    await bot.send_video(
        chat_id=callback_query.message.chat.id,
        video=EARN_NEW_CLIENTS_VIDEO_URL,
        caption="Курс стоит 6000 рублей.\nЗа каждого привлечённого вами клиента вы заработаете 2000 рублей.\nПосле 3-х клиентов курс становится для Вас бесплатным.\nНачиная с 4-го клиента, вы начинаете зарабатывать на продвижении It-образования."
    )
    await bot.send_message(
        callback_query.message.chat.id,
        "Отправляйте рекламные сообщения в тематические чаты по изучению программирования, а также в телеграм-группы различных российских вузов и вы можете выйти на прибыль в 100.000 рублей после привлечения 50 клиентов.",
        reply_markup=keyboard
    )


# Обработка кнопки "Получить реферальную ссылку"
@dp.callback_query_handler(lambda c: c.data == 'get_referral')
async def process_get_referral(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await send_referral_link(callback_query.message, callback_query.from_user.id)


# Обработка кнопки "Сформировать отчёт о заработке"
@dp.callback_query_handler(lambda c: c.data == 'generate_report')
async def process_generate_report(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await generate_report(callback_query.message, callback_query.from_user.id)


# Обработка кнопки "Налоги"
@dp.callback_query_handler(lambda c: c.data == 'tax_info')
async def process_tax_info(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
 
    # Отправка изображения
    await bot.send_photo(
        chat_id=callback_query.message.chat.id,
        photo=TAX_INFO_IMG_URL,
        caption="Реферальные выплаты могут облагаться налогом. Рекомендуем зарегистрироваться как самозанятый."
    )

    # Отправка HTML-сообщения с инструкцией
    info_text = """
<b>Как зарегистрироваться и выбрать вид деятельности для уплаты налогов:</b>

1. Информацию о способах регистрации и не только вы можете найти на официальном сайте <a href="https://npd.nalog.ru/app/">npd.nalog.ru/app</a>.
   
2. При выборе вида деятельности рекомендуем указать: «Реферальные выплаты» или «Услуги».

<i>Пока вы платите налоги, вы защищаете себя и делаете реферальные выплаты законными.</i>
"""
    await callback_query.message.answer(info_text, parse_mode=ParseMode.HTML)

@dp.message_handler(commands=['pay'])
async def handle_pay_command(message: types.Message):
    telegram_id = str(message.from_user.id)
    amount = COURSE_AMOUNT  # Пример суммы, можно заменить
    description = "Оплата курса"
    
    # Шаг 1: Проверка, зарегистрирован ли пользователь
    check_user_url = SERVER_URL + "/check_user"
    user_data = {"telegram_id": telegram_id}
    
    try:
        response = requests.post(check_user_url, json=user_data).json()
        user_id = response.get("user_id")
    except requests.RequestException as e:
        logger.error("Ошибка при проверке пользователя: %s", e)
        await message.answer("Ошибка при проверке регистрации. Пожалуйста, попробуйте позже.")
        return
    except KeyError:
        logger.warning("Пользователь не зарегистрирован, запрос /pay отклонён.")
        await message.answer("Сначала нажмите /start для регистрации.")
        return

    # Шаг 2: Отправка запроса на создание платежа
    create_payment_url = SERVER_URL + "/create_payment"
    payment_data = {"user_id": user_id, "amount": amount}

    try:
        response = requests.post(create_payment_url, json=payment_data).json()
        payment_url = response.get("confirmation", {}).get("confirmation_url")
        
        if payment_url:
            await message.answer(f"Для оплаты курса, перейдите по ссылке: {payment_url}")
        else:
            logger.error("Ошибка: Confirmation URL отсутствует в ответе сервера.")
            await message.answer("Ошибка при создании ссылки для оплаты.")
    except requests.RequestException as e:
        logger.error("Ошибка при отправке запроса на сервер: %s", e)
        await message.answer("Ошибка при обработке платежа.")

@dp.message_handler(commands=['report'])
async def generate_report(message: types.Message):
    telegram_id = str(message.from_user.id)
    report_url = SERVER_URL + "/generate_report"
    user_data = {"telegram_id": telegram_id}

    try:
        response = requests.post(report_url, json=user_data).json()

        # Формируем текст отчета на основе данных из ответа
        username = response.get("username")
        referral_count = response.get("referral_count")
        total_payout = response.get("total_payout")

        report = (
            f"<b>Отчёт для {username}:</b>\n\n"
            f"Привлечённые пользователи: {referral_count}\n"
            f"Общая сумма потенциальных выплат: {total_payout} руб.\n\n"
        )

        await bot.send_video(
            chat_id=message.chat.id,
            video=REPORT_VIDEO_URL,
            caption=report,
            parse_mode=ParseMode.HTML
        )
    except requests.RequestException as e:
        logger.error("Ошибка при отправке запроса на сервер: %s", e)
        await message.answer("Ошибка при генерации отчета.")
    except KeyError:
        await message.answer("Пользователь не зарегистрирован. Пожалуйста, нажмите /start для регистрации.")

@dp.message_handler(commands=['referral'])
async def send_referral_link(message: types.Message):
    telegram_id = str(message.from_user.id)
    referral_url = SERVER_URL + "/get_referral_link"
    user_data = {"telegram_id": telegram_id}

    try:
        response = requests.post(referral_url, json=user_data).json()
        referral_link = response.get("referral_link")

        if referral_link:
            await bot.send_video(
                chat_id=message.chat.id,
                video=REFERRAL_VIDEO_URL,
                caption=(
                    f"Отправляю тебе реферальную ссылку:\n{referral_link}\n"
                    f"Зарабатывай, продвигая It - образование."
                )
            )
        else:
            await message.answer("Ошибка при генерации реферальной ссылки.")
    except requests.RequestException as e:
        logger.error("Ошибка при отправке запроса на сервер: %s", e)
        await message.answer("Ошибка при генерации реферальной ссылки.")
    except KeyError:
        await message.answer("Пользователь не зарегистрирован. Пожалуйста, нажмите /start для регистрации.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(on_start_polling())