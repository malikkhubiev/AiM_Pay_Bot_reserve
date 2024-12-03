import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
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

# Подключаем MemoryStorage
storage = MemoryStorage()

class UserStates(StatesGroup):
    enter_payout_amount = State()  # Состояние для ввода суммы выплаты

dp = Dispatcher(bot, storage=storage)

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
        tg_id = data.get("telegram_id")
        message_text = data.get("message")

        # Отправляем сообщение пользователю через Telegram
        if tg_id and message_text:
            await bot.send_message(chat_id=tg_id, text=message_text)
            return web.json_response({"status": "notification sent"}, status=200)
        return web.json_response({"error": "Invalid data"}, status=400)

    app = web.Application()
    app.router.add_route("HEAD", "/", handle)
    app.router.add_route("GET", "/", handle)
    app.router.add_post("/notify_user", notify_user)
    return app

async def start_web_server():
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

async def start_polling():
    await dp.start_polling()

# Главное меню с кнопками
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    logging.debug(f"Получена команда /start от {message.from_user.id}")

    # Мусор
    await message.answer(f"hey")

    telegram_id = str(message.from_user.id)
    username = message.from_user.username or message.from_user.first_name

    referrer_id = message.text.split()[1] if len(message.text.split()) > 1 else ""

    register_or_greet_url = SERVER_URL + "/greet"

    user_data = {
        "telegram_id": telegram_id,
        "username": username,
        "referrer_id": referrer_id
    }

    # Мусор
    await message.answer(f"{user_data} user_data")

    response = requests.post(register_or_greet_url, json=user_data).json()
    
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
    keyboard.add(InlineKeyboardButton("Заработать на новых клиентах", callback_data='earn_new_clients'))
    # referral_exists = response["has_referrals"]
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
        InlineKeyboardButton("Получить выплату", callback_data='get_payout'),
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


# Обработка кнопки "Получить реферальную ссылку"
@dp.callback_query_handler(lambda c: c.data == 'get_payout')
async def process_get_referral(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.message.chat.id, f"Вы нажали: {callback_query.data}")
    await get_payout(callback_query.message, callback_query.from_user.id, state)


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
    amount = float(COURSE_AMOUNT)  # Пример суммы, можно заменить
    
    # Мусор
    await message.answer(f"{amount} amount")

    # Шаг 1: Проверка, зарегистрирован ли пользователь
    check_user_url = SERVER_URL + "/check_user"

    # Мусор
    await message.answer(f"{check_user_url} check_user_url")

    user_data = {"telegram_id": telegram_id}
    # Мусор
    await message.answer(f"{user_data} user_data")

    try:
        response = requests.post(check_user_url, json=user_data).json()
        user_id = response["user"].id
        # Мусор
        await message.answer(f"{user_id} user_id")
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
    # Мусор
    await message.answer(f"{create_payment_url} create_payment_url")

    payment_data = {"telegram_id": telegram_id, "amount": amount}

    # Мусор
    await message.answer(f"{payment_data} payment_data")
    try:
        response = requests.post(create_payment_url, json=payment_data).json()
        payment_url = response.get("confirmation", {}).get("confirmation_url")
        # Мусор
        await message.answer(f"{payment_url} payment_url")

        if payment_url:
            await message.answer(f"Для оплаты курса, перейдите по ссылке: {payment_url}")
        else:
            logger.error("Ошибка: Confirmation URL отсутствует в ответе сервера.")
            await message.answer("Ошибка при создании ссылки для оплаты.")
    except requests.RequestException as e:
        logger.error("Ошибка при отправке запроса на сервер: %s", e)
        await message.answer("Ошибка при обработке платежа.")

@dp.message_handler(commands=['report'])
async def generate_report(message: types.Message, telegram_id: str):
    # Мусор
    await message.answer(f"generate_report")
    report_url = SERVER_URL + "/generate_report"
    user_data = {"telegram_id": telegram_id}

    # Мусор
    await message.answer(f"{telegram_id} telegram_id")
    await message.answer(f"{report_url} report_url")
    await message.answer(f"{user_data} user_data")

    try:
        response = requests.post(report_url, json=user_data).json()

        # Формируем текст отчета на основе данных из ответа
        username = response.get("username")
        referral_count = response.get("referral_count")
        total_payout = response.get("total_payout")
        current_balance = response.get("current_balance")

        # Мусор
        await message.answer(f"{username} username")
        await message.answer(f"{referral_count} referral_count")
        await message.answer(f"{total_payout} total_payout")
        await message.answer(f"{current_balance} current_balance")


        report = (
            f"<b>Отчёт для {username}:</b>\n\n"
            f"Привлечённые пользователи: {referral_count}\n"
            f"Общая количество когда-либо заработанных денег: {total_payout} руб.\n\n"
            f"Текущий баланс: {current_balance} руб.\n\n"
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
async def send_referral_link(message: types.Message, telegram_id: str):
    # Мусор
    await message.answer(f"send_referral_link")
    referral_url = SERVER_URL + "/get_referral_link"
    user_data = {"telegram_id": telegram_id}

    # Мусор
    await message.answer(f"{telegram_id} telegram_id")
    await message.answer(f"{referral_url} referral_url")
    await message.answer(f"{user_data} user_data")

    try:
        response = requests.post(referral_url, json=user_data).json()
        referral_link = response.get("referral_link")

        # Мусор
        await message.answer(f"{referral_link} referral_link")
    
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




# Реферальные выплаты

@dp.message_handler(Command("get_payout"))
async def get_payout(message: types.Message, telegram_id: str, state: FSMContext):
    """
    Обрабатывает запрос пользователя на выплату: показывает текущий баланс и запрашивает сумму для выплаты.
    """

    
    await message.answer(2)
    try:
        # Запрос баланса через FastAPI эндпоинт
        response = requests.get(f"{SERVER_URL}/get_balance/{telegram_id}")
        response.raise_for_status()
        data = response.json()
        # мусор
        await message.answer("data", data)
    
        balance = data.get("balance")
        # мусор
        await message.answer("balance", balance)

        if balance <= 0:
            await message.answer(
                "Ваш текущий баланс равен 0. Вы не можете запросить выплату."
            )
            return

        # Сообщаем пользователю его баланс и запрашиваем сумму для выплаты
        await message.answer(
            f"Ваш текущий баланс: {balance:.2f} RUB. "
            "Введите сумму, которую вы хотите вывести (не больше текущего баланса)."
        )

        # Сохраняем состояние пользователя для ожидания ввода суммы
        await state.update_data(balance=balance)  # Сохраняем баланс в состояние
        await UserStates.enter_payout_amount.set()
    except requests.RequestException as e:
        logger.error(f"Ошибка при получении баланса: {e}")
        await message.answer("Не удалось получить ваш баланс. Попробуйте позже.")

@dp.message_handler(state=UserStates.enter_payout_amount)
async def process_payout_amount(message: types.Message, state: FSMContext):
    """
    Обрабатывает сумму, введённую пользователем, и создаёт запрос на выплату.
    """
    user_data = await state.get_data()
    # мусор
    await message.answer("user_data", user_data)

    balance = user_data.get("balance")

    # мусор
    await message.answer("balance", balance)

    telegram_id = message.from_user.id
    
    # мусор
    await message.answer("telegram_id", telegram_id)

    try:
        amount = float(message.text)
        # мусор
        await message.answer("amount", amount)
        
        if amount <= 0:
            await message.answer("Сумма должна быть больше 0. Попробуйте ещё раз.")
            return

        if amount > balance:
            await message.answer(
                f"У вас недостаточно средств. Ваш текущий баланс: {balance:.2f} RUB. "
                "Введите сумму, которая меньше или равна вашему балансу."
            )
            return

        # Делаем запрос к FastAPI эндпоинту для создания выплаты
        response = requests.post(
            f"{SERVER_URL}/add_payout_toDb",
            json={"telegram_id": telegram_id, "amount": amount}
        )
        response.raise_for_status()
        payout_data = response.json()

        # мусор
        await message.answer("payout_data", payout_data)

        # Обработка ответа от FastAPI
        if payout_data["status"] == "ready_to_pay":
            await message.answer(
                f"Ваш запрос на выплату {amount:.2f} RUB принят. Выплата будет выполнена в ближайшее время."
            )
            payout_response = requests.post(
                f"{SERVER_URL}/make_payout",
                json={"telegram_id": telegram_id, "amount": amount}
            )
            payout_response.raise_for_status()
            payout_result = payout_response.json()

            # мусор
            await message.answer("payout_result", payout_result)

            if payout_result["status"] == "success":
                await message.answer(payout_result["message"])
            else:
                await message.answer(
                    f"Ошибка при выплате: {payout_result.get('message', 'Неизвестная ошибка')}"
                )
        elif payout_data["status"] == "awaiting_card":
            payout_response = requests.post(
                f"{SERVER_URL}/make_payout",
                json={"telegram_id": telegram_id, "amount": amount}
            )

            payout_response.raise_for_status()
            payout_result = payout_response.json()
            payment_url = payout_result["payment_url"]
            
            await message.answer(
                f"Ваш запрос на выплату {amount:.2f} RUB принят, но у вас не привязана карта. "
                "Пожалуйста, привяжите карту для получения выплаты. Перейдите по ссылке ниже."
            )
            await message.answer(f"Перейдите по ссылке для ввода данных карты: {payment_url}")
        else:
            await message.answer("Произошла ошибка. Попробуйте ещё раз позже.")
    except requests.RequestException as e:
        logger.error(f"Ошибка при запросе выплаты: {e}")
        await message.answer("Не удалось обработать ваш запрос. Попробуйте позже.")
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число.")

    # Завершаем состояние
    await state.finish()

USE_RENDER = os.getenv("USE_RENDER", "false").lower() == "true"

if __name__ == "__main__":
    if USE_RENDER:
        # Render: запускаем веб-сервер
        asyncio.run(start_web_server())
    else:
        # Локально: запускаем polling
        asyncio.run(start_polling())