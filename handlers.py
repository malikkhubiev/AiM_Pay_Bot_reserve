from utils import log
from config import (
    COURSE_AMOUNT,
    SERVER_URL,
    START_VIDEO_URL,
    REPORT_VIDEO_URL,
    REFERRAL_VIDEO_URL,
    EARN_NEW_CLIENTS_VIDEO_URL,
    TAX_INFO_IMG_URL
)
from utils import *
from loader import *

# Кэш для хранения ссылок
links_cache = {}

# Функция для инициализации словаря кэша, если его ещё нет
def init_user_cache(telegram_id: str):
    if telegram_id not in links_cache:
        links_cache[telegram_id] = {
            'invite_link': None,
            'referral_link': None
        }

@dp.message_handler(commands=['start'])
async def start(message: types.Message, telegram_id: str = None, username: str = None):
    log.info(f"Получена команда /start от {telegram_id}")

    if not(telegram_id):
        telegram_id = message.from_user.id
    if not(username):
        username = message.from_user.username or message.from_user.first_name
    referrer_id = message.text.split(' ')[1] if len(message.text.split(' ')) > 1 else None

    if referrer_id and not(referrer_id.isdigit()):
        referrer_id = None

    await message.answer(f"referrer_id {referrer_id}")

    start_url = SERVER_URL + "/start"
    user_data = {
        "telegram_id": telegram_id,
        "username": username,
        "referrer_id": referrer_id
    }
    await message.answer(f"user_data {user_data}")
    keyboard = InlineKeyboardMarkup(row_width=1)

    response = await send_request(
        start_url,
        method="POST",
        json=user_data
    )
    await message.answer(f"response {response}")

    if response["status"] == "success":
        if response["type"] == "temp_user":
            await message.answer(f"temp")
            keyboard.add(
                InlineKeyboardButton("Начало работы", callback_data='getting_started'),
                InlineKeyboardButton("Документы", callback_data='documents'),
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
            else:
                keyboard.add(
                    InlineKeyboardButton("Получить ссылку", callback_data='get_invite_link'),
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
    elif response["status"] == "error":
        await message.answer(response["message"])

async def getting_started(message: types.Message, telegram_id: str, u_name: str = None):
    log.info(f"Получена команда /getting_started от {telegram_id}")

    await message.answer(f"hey")

    getting_started_url = SERVER_URL + "/getting_started"
    user_data = {
        "telegram_id": telegram_id
    }
    await message.answer(f"{user_data} user_data")

    response = await send_request(
        getting_started_url,
        method="POST",
        json=user_data
    )
    await message.answer(f"{response}")

    if response["status"] == "success":
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            InlineKeyboardButton("Оплатить курс", callback_data='pay_course'),
            InlineKeyboardButton("Заработать на новых клиентах", callback_data='earn_new_clients')
        )
        await bot.send_video(
            chat_id=message.chat.id,
            video=START_VIDEO_URL,
            caption="Добро пожаловать! Здесь Вы можете оплатить курс и заработать на привлечении новых клиентов.",
            reply_markup=keyboard
        )
    elif response["status"] == "error":
        await message.answer(response["message"])

async def get_documents(message: types.Message, telegram_id: str, u_name: str = None):
    log.info(f"Получена команда /get_documents от {telegram_id}")
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("Публичная оферта", callback_data='public_offer'),
        InlineKeyboardButton("Политика Конфиденциальности", callback_data='privacy_policy'),
        InlineKeyboardButton("Назад", callback_data='start'),
    )
    await bot.send_message(
        chat_id=message.chat.id,
        text="Внимательно прочитайте следующие документы.",
        reply_markup=keyboard
    )

async def get_public_offer(message: types.Message, telegram_id: str, u_name: str = None):
    log.info(f"Получена команда /get_public_offer от {telegram_id}")
    public_offer_url = SERVER_URL + "/offer"
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("Назад", callback_data='documents')
    )
    await bot.send_message(
        chat_id=message.chat.id,
        text=f"Для ознакомления с Публичной офертой перейдите по ссылке: {public_offer_url}",
        reply_markup=keyboard
    )

async def get_privacy_policy(message: types.Message, telegram_id: str, u_name: str = None):
    log.info(f"Получена команда /get_privacy_policy от {telegram_id}")
    privacy_url = SERVER_URL + "/privacy"
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("Назад", callback_data='documents')
    )
    await bot.send_message(
        chat_id=message.chat.id,
        text=f"Для ознакомления с Политикой конфиденциальности перейдите по ссылке: {privacy_url}",
        reply_markup=keyboard
    )

async def handle_pay_command(message: types.Message, telegram_id: str, u_name: str = None):
    amount = float(COURSE_AMOUNT)  # Пример суммы, можно заменить
    
    await message.answer(f"{amount} amount")

    # Шаг 1: Проверка, зарегистрирован ли пользователь
    check_user_url = SERVER_URL + "/check_user"

    await message.answer(f"{check_user_url} check_user_url")

    user_data = {"telegram_id": telegram_id}
    await message.answer(f"{user_data} user_data")

    response = await send_request(
        check_user_url,
        method="POST",
        json=user_data
    )

    if response["status"] == "success":
        await message.answer(f"{response} response")
        user_id = response["user"]["id"]
        
        await message.answer(f"{user_id} user_id")

        # Шаг 2: Отправка запроса на создание платежа
        create_payment_url = SERVER_URL + "/create_payment"
        await message.answer(f"{create_payment_url} create_payment_url")

        payment_data = {
            "telegram_id": telegram_id
        }

        await message.answer(f"{payment_data} payment_data")
        response = await send_request(
            create_payment_url,
            method="POST",
            json=user_data
        )

        if response["status"] == "success":
            payment_url = response.get("confirmation", {}).get("confirmation_url")
            
            await message.answer(f"{payment_url} payment_url")

            if payment_url:
                await message.answer(f"Для оплаты курса, перейдите по ссылке: {payment_url}")
            else:
                logger.error("Ошибка: Confirmation URL отсутствует в ответе сервера.")
                await message.answer("Ошибка при создании ссылки для оплаты.")
        elif response["status"] == "error":
            await message.answer(response["message"])
    elif response["status"] == "error":
        await message.answer(response["message"])


async def generate_overview_report(message: types.Message, telegram_id: str, u_name: str = None):
    await message.answer(f"generate_overview_report")
    overview_report_url = SERVER_URL + "/generate_overview_report"
    user_data = {"telegram_id": telegram_id}

    await message.answer(f"{telegram_id} telegram_id")
    await message.answer(f"{overview_report_url} report_url")
    await message.answer(f"{user_data} user_data")

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("Назад", callback_data='generate_report')
    )

    response = await send_request(
        overview_report_url,
        method="POST",
        json=user_data
    )

    if response["status"] == "success":
        # Формируем текст отчета на основе данных из ответа
        username = response.get("username")
        referral_count = response.get("referral_count")
        total_payout = response.get("total_payout")
        paid_count = response.get("paid_count")
        paid_percentage = response.get("paid_percentage")

        
        await message.answer(f"{username} username")
        await message.answer(f"{referral_count} referral_count")
        await message.answer(f"{total_payout} total_payout")

        report = (
            f"<b>Отчёт для {username}:</b>\n\n"
            f"Привлечённые пользователи: {referral_count}\n"
            f"Оплатили курс: {paid_count} ({paid_percentage:.2f}%)\n"
            f"Общее количество заработанных денег: {total_payout:.2f} руб.\n"
        )

        await bot.send_video(
            chat_id=message.chat.id,
            video=REPORT_VIDEO_URL,
            caption=report,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard
        )
    elif response["status"] == "error":
        await message.answer(response["message"])

async def generate_clients_report(message: types.Message, telegram_id: str, u_name: str = None):
    await message.answer(f"generate_clients_report")
    clients_report_url = SERVER_URL + "/generate_clients_report"
    user_data = {"telegram_id": telegram_id}

    await message.answer(f"{telegram_id} telegram_id")
    await message.answer(f"{clients_report_url} report_url")
    await message.answer(f"{user_data} user_data")

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("Назад", callback_data='generate_report')
    )

    response = await send_request(
        clients_report_url,
        method="POST",
        json=user_data
    )

    if response["status"] == "success":
        # Формируем текст отчета на основе данных из ответа
        username = response.get("username")
        invited_list = response.get("invited_list")

        await message.answer(f"{username} username")
        await message.answer(f"{invited_list} invited_list")

        report = (
            f"<b>Отчёт для {username}:</b>\n"
        )

        await bot.send_video(
            chat_id=message.chat.id,
            video=REPORT_VIDEO_URL,
            caption=report,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard
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
    elif response["status"] == "error":
        await message.answer(response["message"])

async def bind_card(message: types.Message, telegram_id: str, u_name: str = None):
    bind_card_url = SERVER_URL + "/bind_card"
    user_data = {"telegram_id": telegram_id}
    response = await send_request(
        bind_card_url,
        method="POST",
        json=user_data
    )
    if response["status"] == "success":
        binding_url = response["binding_url"]
        await message.answer(f"{binding_url} binding_url")
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            InlineKeyboardButton("Назад", callback_data='earn_new_clients')
        )
        text = ""
        if binding_url:
            text = f"Перейдите по следующей ссылке для привязки карты: {binding_url}"
        else:
            text = "Ошибка при генерации ссылки."
        await bot.send_message(
            chat_id=message.chat.id,
            text=text,
            reply_markup=keyboard
        )
    elif response["status"] == "error":
        await message.answer(response["message"])
        return

async def send_referral_link(message: types.Message, telegram_id: str, u_name: str = None):
    await message.answer(f"send_referral_link")
    init_user_cache(telegram_id)

    if links_cache[telegram_id]['referral_link'] is not None:
        await message.answer(f"ИЗ кэша")
        return links_cache[telegram_id]['referral_link']
    
    referral_url = SERVER_URL + "/get_referral_link"
    user_data = {"telegram_id": telegram_id}

    await message.answer(f"{telegram_id} telegram_id")
    await message.answer(f"{referral_url} referral_url")
    await message.answer(f"{user_data} user_data")

    response = await send_request(
        referral_url,
        method="POST",
        json=user_data
    ) 

    text = ""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("Назад", callback_data='earn_new_clients')
    )

    if response["status"] == "success":
        referral_link = response.get("referral_link")
        links_cache[telegram_id]['referral_link'] = referral_link
        
        await message.answer(f"{referral_link} referral_link")

        await bot.send_video(
            chat_id=message.chat.id,
            video=REFERRAL_VIDEO_URL,
            caption=(
                f"Отправляю тебе реферальную ссылку:\n{referral_link}\n"
                f"Зарабатывай, продвигая It - образование."
            ),
            reply_markup=keyboard
        )

    elif response["status"] == "error":
        text = response["message"]
    else:
        text = "Ошибка при генерации ссылки"
    await bot.send_message(
        chat_id=message.chat.id,
        text=text,
        reply_markup=keyboard
    )

async def send_invite_link(message: types.Message, telegram_id: str, u_name: str = None):
    await message.answer(f"send_invite_link")
    init_user_cache(telegram_id)

    if links_cache[telegram_id]['invite_link'] is not None:
        await message.answer(f"ИЗ кэша")
        return links_cache[telegram_id]['invite_link']

    invite_url = SERVER_URL + "/get_invite_link"
    user_data = {"telegram_id": telegram_id}

    await message.answer(f"{user_data} user_data")

    response = await send_request(
        invite_url,
        method="POST",
        json=user_data
    ) 

    text = ""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("Назад", callback_data='earn_new_clients')
    )

    if response["status"] == "success":
        invite_link = response.get("invite_link")
        links_cache[telegram_id]['invite_link'] = invite_link
        
        await message.answer(f"{invite_link} invite_link")

        await bot.send_video(
            chat_id=message.chat.id,
            video=REFERRAL_VIDEO_URL,
            caption=(
                f"Вот ссылка для присоединения к нашей группе. Обращайтесь с ней очень аккуратно. Она одноразовая и если вы воспользуетесь единственным шансом неверно, исправить ничего не получится: {invite_link}"
            ),
            reply_markup=keyboard
        )

    elif response["status"] == "error":
        text = response["message"]
    else:
        text = "Ошибка при генерации ссылки"
    await bot.send_message(
        chat_id=message.chat.id,
        text=text,
        reply_markup=keyboard
    )

async def earn_new_clients(message: types.Message, telegram_id: str, u_name: str = None):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("Получить реферальную ссылку", callback_data='get_referral'),
        InlineKeyboardButton("Привязать/изменить карту", callback_data='bind_card'),
        InlineKeyboardButton("Сформировать отчёт о заработке", callback_data='generate_report'),
        InlineKeyboardButton("Налоги", callback_data='tax_info'),
        InlineKeyboardButton("Документы", callback_data='documents'),
        InlineKeyboardButton("Назад", callback_data='start'),
    )

    await bot.send_video(
        chat_id=message.chat.id,
        video=EARN_NEW_CLIENTS_VIDEO_URL,
        caption="Курс стоит 6000 рублей.\nЗа каждого привлечённого вами клиента вы заработаете 2000 рублей.\nПосле 3-х клиентов курс становится для Вас бесплатным.\nНачиная с 4-го клиента, вы начинаете зарабатывать на продвижении It-образования."
    )
    await bot.send_message(
        message.chat.id,
        "Отправляйте рекламные сообщения в тематические чаты по изучению программирования, а также в телеграм-группы различных российских вузов и вы можете выйти на прибыль в 100.000 рублей после привлечения 50 клиентов.",
        reply_markup=keyboard
    )

async def generate_report(message: types.Message, telegram_id: str, u_name: str = None):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("Общая информация", callback_data='report_overview'),
        InlineKeyboardButton("Список привлечённых клиентов", callback_data='report_clients'),
        InlineKeyboardButton("Назад", callback_data='earn_new_clients')
    )
    await bot.send_message(
        chat_id=message.chat.id,
        text="Какой отчёт вы хотите сформировать?",
        reply_markup=keyboard
    )

async def get_tax_info(message: types.Message, telegram_id: str, u_name: str = None):
    await bot.send_photo(
        chat_id=message.chat.id,
        photo=TAX_INFO_IMG_URL,
        caption="Реферальные выплаты могут облагаться налогом. Рекомендуем зарегистрироваться как самозанятый."
    )
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("Назад", callback_data='earn_new_clients')
    )

    info_text = """
    <b>Как зарегистрироваться и выбрать вид деятельности для уплаты налогов:</b>

    1. Информацию о способах регистрации и не только вы можете найти на официальном сайте <a href="https://npd.nalog.ru/app/">npd.nalog.ru/app</a>.
    
    2. При выборе вида деятельности рекомендуем указать: «Реферальные выплаты» или «Услуги».

    <i>Пока вы платите налоги, вы защищаете себя и делаете реферальные выплаты законными.</i>
    """
    await bot.send_message(
        chat_id=message.chat.id,
        text=info_text,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard
    )