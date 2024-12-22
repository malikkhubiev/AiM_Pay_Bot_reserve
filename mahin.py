import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
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
        tg_id = data.get("telegram_id")
        message_text = data.get("message")

        # Отправляем сообщение пользователю через Telegram
        if tg_id and message_text:
            await bot.send_message(chat_id=tg_id, text=message_text)
            return web.json_response({"status": "notification sent"}, status=200)
        return web.json_response({"error": "Invalid data"}, status=400)
    
    async def send_invite_link(request):
        data = await request.json()
        tg_id = data.get("telegram_id")
        # Получение пригласительной ссылки для группы
        invite_link = await bot.export_chat_invite_link(GROUP_ID)
        
        # Отправляем ссылку пользователю
        await bot.send_message(
            chat_id=tg_id,
            text=f"Поздравляем! Ваш платёж прошёл успешно, вы оплатили курс 🎉. Вот ссылка для присоединения к нашей группе: {invite_link}",
            parse_mode=ParseMode.MARKDOWN
        )
        return web.json_response({"status": "notification sent"}, status=200)

    app = web.Application()
    app.router.add_route("HEAD", "/", handle)
    app.router.add_route("GET", "/", handle)
    app.router.add_post("/notify_user", notify_user)
    app.router.add_post("/send_invite_link", send_invite_link)
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
                response = requests.post(check_user_url, json=user_data).json()
                
                # Если ответ пустой или нет такого пользователя, кикаем
                if response.get("user"):
                    user_id = response["user"]["id"]
                    logging.info(f"Пользователь с ID {user_id} добавлен в группу")
                else:
                    user_id = telegram_id
                    await bot.kick_chat_member(event.chat.id, user_id)  # Кикаем пользователя
                    await bot.unban_chat_member(event.chat.id, user_id)  # Разбаниваем (чтобы не остаться заблокированным)
                    logging.info(f"Пользователь с ID {user_id} был исключён из группы, так как не найден в базе данных")
                    return
            except requests.RequestException as e:
                logger.error("Ошибка при запросе к серверу: %s", e)
                await bot.send_message(event.chat.id, "Ошибка при проверке регистрации. Пожалуйста, попробуйте позже.")
                return
            except KeyError:
                logger.warning("Пользователь не зарегистрирован в базе данных.")
                await bot.send_message(event.chat.id, "Сначала нажмите /start для регистрации.")
                return
    except Exception as e:
        logger.error(f"Ошибка при обработке события: {e}")

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
    await message.answer(f"{response}")
    
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
    await handle_pay_command(callback_query.message, callback_query.from_user.id)

@dp.callback_query_handler(lambda c: c.data == 'earn_new_clients')
async def process_earn_new_clients(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("Получить реферальную ссылку", callback_data='get_referral'),
        InlineKeyboardButton("Привязать/изменить карту", callback_data='bind_card'),
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
@dp.callback_query_handler(lambda c: c.data == 'bind_card')
async def process_get_referral(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bind_card(callback_query.message, callback_query.from_user.id)

# Обработка кнопки "Получить реферальную ссылку"
@dp.callback_query_handler(lambda c: c.data == 'get_payout')
async def process_get_referral(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await get_payout(callback_query.message, callback_query.from_user.id)


# Обработка кнопки "Сформировать отчёт о заработке"
@dp.callback_query_handler(lambda c: c.data == 'generate_report')
async def process_generate_report(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    # Выбор типа отчёта
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("Общая информация", callback_data='report_overview'),
        InlineKeyboardButton("Список привлечённых клиентов", callback_data='report_clients')
    )

    await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text="Какой отчёт вы хотите сформировать?",
        reply_markup=keyboard
    )

# Обработка кнопки "Общая информация"
@dp.callback_query_handler(lambda c: c.data == 'report_overview')
async def process_report_overview(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await generate_overview_report(callback_query.message, callback_query.from_user.id)

# Обработка кнопки "Список привлечённых клиентов"
@dp.callback_query_handler(lambda c: c.data == 'report_clients')
async def process_report_clients(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await generate_clients_report(callback_query.message, callback_query.from_user.id)


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

async def send_invite(message: types.Message):
    # Отправить пригласительную ссылку
    invite_link = await bot.export_chat_invite_link(chat_id=message.chat.id)
    await message.reply(f"Привет! Пройди по этой ссылке, чтобы присоединиться к нашей группе: {invite_link}")

@dp.message_handler(commands=['pay'])
async def handle_pay_command(message: types.Message, telegram_id: str):
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
        await message.answer(f"{response} response")
        user_id = response["user"]["id"]
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

@dp.message_handler(commands=['generate_overview_report'])
async def generate_overview_report(message: types.Message, telegram_id: str):
    # Мусор
    await message.answer(f"generate_overview_report")
    report_url = SERVER_URL + "/generate_overview_report"
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
        paid_count = response.get("paid_count")
        paid_percentage = response.get("paid_percentage")

        # Мусор
        await message.answer(f"{username} username")
        await message.answer(f"{referral_count} referral_count")
        await message.answer(f"{total_payout} total_payout")
        await message.answer(f"{current_balance} current_balance")

        # Generate the report
        report = (
            f"<b>Отчёт для {username}:</b>\n\n"
            f"Привлечённые пользователи: {referral_count}\n"
            f"Оплатили курс: {paid_count} ({paid_percentage:.2f}%)\n"
            f"Общее количество заработанных денег: {total_payout:.2f} руб.\n"
            f"Текущий баланс: {current_balance:.2f} руб.\n\n"
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

@dp.message_handler(commands=['generate_clients_report'])
async def generate_clients_report(message: types.Message, telegram_id: str):
    # Мусор
    await message.answer(f"generate_clients_report")
    report_url = SERVER_URL + "/generate_clients_report"
    user_data = {"telegram_id": telegram_id}

    # Мусор
    await message.answer(f"{telegram_id} telegram_id")
    await message.answer(f"{report_url} report_url")
    await message.answer(f"{user_data} user_data")

    try:
        response = requests.post(report_url, json=user_data).json()

        # Формируем текст отчета на основе данных из ответа
        username = response.get("username")
        invited_list = response.get("invited_list")

        # Мусор
        await message.answer(f"{username} username")


        # Generate the report
        report = (
            f"<b>Отчёт для {username}:</b>\n"
        )

        await bot.send_video(
            chat_id=message.chat.id,
            video=REPORT_VIDEO_URL,
            caption=report,
            parse_mode=ParseMode.HTML
        )

        # Send the list of invited users
        if invited_list:
            await message.answer(f"{invited_list} invited_list есть")
            for invited in invited_list:
                await message.answer(f"{invited} invited перебор начался")
                user_status = "Оплатил" if invited["paid"] else "Не оплатил"
                user_info = (
                    f"<b>Пользователь:</b> {invited['username']}\n"
                    f"<b>Telegram ID:</b> {invited['telegram_id']}\n"
                    f"<b>Статус:</b> {user_status}\n\n"
                )
                await message.answer(f"{user_info} user_info")
                await bot.send_message(
                    chat_id=message.chat.id,
                    text=user_info,
                    parse_mode=ParseMode.HTML
                )

    except requests.RequestException as e:
        logger.error("Ошибка при отправке запроса на сервер: %s", e)
        await message.answer("Ошибка при генерации отчета.")
    except KeyError:
        await message.answer("Пользователь не зарегистрирован. Пожалуйста, нажмите /start для регистрации.")


@dp.message_handler(commands=['referral'])
async def bind_card(message: types.Message, telegram_id: str):
    bind_card_url = SERVER_URL + "/bind_card"
    user_data = {"telegram_id": telegram_id}
    try:
        response = requests.post(bind_card_url, json=user_data).json()
        if response.get("status") == "error":
            await message.answer(response.get("message"))
            return
        binding_url = response.get("binding_url")

        # Мусор
        await message.answer(f"{binding_url} binding_url")
    
        if binding_url:
            await message.answer(f"Перейдите по следующей ссылке для привязки карты: {binding_url}")
        else:
            await message.answer("Ошибка при генерации ссылки.")
    except requests.RequestException as e:
        logger.error("Ошибка при отправке запроса на сервер: %s", e)
        await message.answer("Ошибка при генерации ссылки.")
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

    
        if response["status"] == "success":
            referral_link = response.get("referral_link")
            # Мусор
            await message.answer(f"{referral_link} referral_link")

            await bot.send_video(
                chat_id=message.chat.id,
                video=REFERRAL_VIDEO_URL,
                caption=(
                    f"Отправляю тебе реферальную ссылку:\n{referral_link}\n"
                    f"Зарабатывай, продвигая It - образование."
                )
            )
        elif response["status"] == "error":
            await message.answer(response["message"])
        else:
            await message.answer("Ошибка при генерации ссылки")
    except requests.RequestException as e:
        logger.error("Ошибка при отправке запроса на сервер: %s", e)
        await message.answer("Ошибка при генерации реферальной ссылки.")
    except KeyError:
        await message.answer("Пользователь не зарегистрирован. Пожалуйста, нажмите /start для регистрации.")

# Реферальные выплаты
@dp.message_handler(commands=['get_payout'])
async def get_payout(message: types.Message, telegram_id: str):

    await message.answer(f"telegram_id {telegram_id}")

    user_data = {
        "telegram_id": telegram_id
    }

    # Запрос баланса и оплаты курса с сервера
    response = requests.post(f"{SERVER_URL}/isAbleToGetPayout", json=user_data)
    response.raise_for_status()
    data = response.json()
    balance = data.get("balance", 0)
    paid = data.get("paid", False)
    isBinded = data.get("isBinded", False)

    await message.answer(f"balance {balance}")
    await message.answer(f"paid {paid}")
    await message.answer(f"isBinded {isBinded}")

    if not(paid):
        await bot.send_message(
            message.chat.id, 
            "Вы не можете стать партнёром по реферальной программе, не оплатив курс"
        )
        return

    if not(isBinded):
        await bot.send_message(
            message.chat.id, 
            "Чтобы получить выплату, привяжите банковскую карту"
        )
        return

    if balance <= 0:
        await bot.send_message(
            message.chat.id, 
            "Ваш баланс равен 0. Вы не можете запросить выплату."
        )
        return

    # Просим пользователя ввести сумму в формате: "Выплата: 5000"
    await bot.send_message(
        message.chat.id,
        f"Ваш текущий баланс: {balance:.2f} RUB.\n"
        "Введите данные для выплаты в формате:\nВыплата: 5000"
    )

@dp.message_handler(lambda message: message.text.lower().startswith('выплата: '))
async def process_payout_amount(message: types.Message):
    # Получаем сумму из текста
    try:
        # Извлекаем данные после "Выплата: "
        text = message.text[len('Выплата: '):].strip()
        if not(text.isdigit()):
            await message.answer("Некорректный формат величины выплаты")
            return

        # Преобразуем сумму в число
        amount = float(text)

        # Проверка на валидность суммы
        if amount <= 0:
            await message.answer("Сумма должна быть больше 0. Попробуйте ещё раз.")
            return
        
        telegram_id = message.from_user.id
        await message.answer(f"telegram_id {telegram_id}")

        user_data = {
            "telegram_id": telegram_id
        }

        # Запрос баланса с сервера
        response = requests.post(f"{SERVER_URL}/isAbleToGetPayout", json=user_data)
        response.raise_for_status()
        data = response.json()
        await message.answer(f"data {data}")

        balance = data.get("balance", 0)
        paid = data.get("paid", False)
        await message.answer(f"balance {balance}")

        if not(paid):
            await bot.send_message(
                message.chat.id, 
                "Вы не можете стать партнёром по реферальной программе, не оплатив курс"
            )
            return

        if amount > balance or amount <= 0 or balance <= 0:
            await message.answer(
                f"У вас недостаточно средств. Ваш баланс: {balance:.2f} RUB. "
                "Введите сумму, которая меньше или равна вашему балансу. Сумма не должна быть отрицательной"
            )
            return

        # Делаем запрос к FastAPI эндпоинту для создания выплаты
        response = requests.post(
            f"{SERVER_URL}/add_payout_toDb",
            json={"telegram_id": telegram_id, "amount": amount}
        )
        response.raise_for_status()
        payout_data = response.json()
        await message.answer(f"payout_data {payout_data}")

        # Обработка ответа от FastAPI
        if payout_data["status"] == "ready_to_pay":
            await message.answer(
                f"Ваш запрос на выплату {amount:.2f} RUB принят. Выплата будет выполнена в ближайшее время."
            )
            payout_response = requests.post(
                f"{SERVER_URL}/make_payout",
                json={"telegram_id": telegram_id}
            )
            payout_response.raise_for_status()
            payout_result = payout_response.json()

            # мусор
            await message.answer(f"payout_result {payout_result}")

            if payout_result["status"] == "success":
                await message.answer(payout_result["message"])
            else:
                await message.answer(
                    f"Ошибка при выплате: {payout_result.get('message', 'Неизвестная ошибка')}"
                )
        else:
            await message.answer(payout_data["reason"])

    except ValueError:
        await message.answer("Некорректный формат данных.")

@dp.message_handler(commands=["start"])
async def send_offer_link(message: types.Message):
    await message.answer("Скачайте оферту по ссылке: https://yourdomain.com/offer")

USE_RENDER = os.getenv("USE_RENDER", "false").lower() == "true"

if __name__ == "__main__":
    if USE_RENDER:
        # Render: запускаем веб-сервер
        asyncio.run(start_web_server())
    else:
        # Локально: запускаем polling
        asyncio.run(start_polling())