from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from handlers import (
    start,
    getting_started,
    get_documents,
    get_public_offer,
    get_privacy_policy,
    handle_pay_command,
    send_referral_link,
    bind_card,
    generate_overview_report,
    generate_clients_report
)
from config import (
    TAX_INFO_IMG_URL,
    EARN_NEW_CLIENTS_VIDEO_URL,
)
from loader import *

@dp.callback_query_handler(lambda c: c.data == 'start')
async def process_start(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await start(callback_query.message)

@dp.callback_query_handler(lambda c: c.data == 'getting_started')
async def process_getting_started(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await getting_started(callback_query.message)

@dp.callback_query_handler(lambda c: c.data == 'documents')
async def process_documents(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await get_documents(callback_query.message)

@dp.callback_query_handler(lambda c: c.data == 'public_offer')
async def process_public_offer(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await get_public_offer(callback_query.message)

@dp.callback_query_handler(lambda c: c.data == 'privacy_policy')
async def process_privacy_policy(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await get_privacy_policy(callback_query.message)

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
        InlineKeyboardButton("Сформировать отчёт о заработке", callback_data='generate_report'),
        InlineKeyboardButton("Налоги", callback_data='tax_info'),
        InlineKeyboardButton("Назад", callback_data='start'),
    )

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

@dp.callback_query_handler(lambda c: c.data == 'get_referral')
async def process_get_referral(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await send_referral_link(callback_query.message, callback_query.from_user.id)

@dp.callback_query_handler(lambda c: c.data == 'bind_card')
async def process_get_referral(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bind_card(callback_query.message, callback_query.from_user.id)

@dp.callback_query_handler(lambda c: c.data == 'generate_report')
async def process_generate_report(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("Общая информация", callback_data='report_overview'),
        InlineKeyboardButton("Список привлечённых клиентов", callback_data='report_clients'),
        InlineKeyboardButton("Назад", callback_data='earn_new_clients')
    )

    await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text="Какой отчёт вы хотите сформировать?",
        reply_markup=keyboard
    )

@dp.callback_query_handler(lambda c: c.data == 'report_overview')
async def process_report_overview(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await generate_overview_report(callback_query.message, callback_query.from_user.id)

@dp.callback_query_handler(lambda c: c.data == 'report_clients')
async def process_report_clients(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await generate_clients_report(callback_query.message, callback_query.from_user.id)

@dp.callback_query_handler(lambda c: c.data == 'tax_info')
async def process_tax_info(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
 
    await bot.send_photo(
        chat_id=callback_query.message.chat.id,
        photo=TAX_INFO_IMG_URL,
        caption="Реферальные выплаты могут облагаться налогом. Рекомендуем зарегистрироваться как самозанятый."
    )

    info_text = """
<b>Как зарегистрироваться и выбрать вид деятельности для уплаты налогов:</b>

1. Информацию о способах регистрации и не только вы можете найти на официальном сайте <a href="https://npd.nalog.ru/app/">npd.nalog.ru/app</a>.
   
2. При выборе вида деятельности рекомендуем указать: «Реферальные выплаты» или «Услуги».

<i>Пока вы платите налоги, вы защищаете себя и делаете реферальные выплаты законными.</i>
"""
    await callback_query.message.answer(info_text, parse_mode=ParseMode.HTML)