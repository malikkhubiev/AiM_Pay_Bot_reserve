
# @dp.callback_query_handler(lambda c: c.data == 'start')
# async def process_start(callback_query: types.CallbackQuery):
#     await bot.answer_callback_query(callback_query.id)
#     await start(callback_query.message, callback_query.from_user.id, callback_query.from_user.username)

# @dp.callback_query_handler(lambda c: c.data == 'getting_started')
# async def process_getting_started(callback_query: types.CallbackQuery):
#     await bot.answer_callback_query(callback_query.id)
#     await getting_started(callback_query.message, callback_query.from_user.id)

# @dp.callback_query_handler(lambda c: c.data == 'documents')
# async def process_documents(callback_query: types.CallbackQuery):
#     await bot.answer_callback_query(callback_query.id)
#     await get_documents(callback_query.message, callback_query.from_user.id)

# @dp.callback_query_handler(lambda c: c.data == 'public_offer')
# async def process_public_offer(callback_query: types.CallbackQuery):
#     await bot.answer_callback_query(callback_query.id)
#     await get_public_offer(callback_query.message, callback_query.from_user.id)

# @dp.callback_query_handler(lambda c: c.data == 'privacy_policy')
# async def process_privacy_policy(callback_query: types.CallbackQuery):
#     await bot.answer_callback_query(callback_query.id)
#     await get_privacy_policy(callback_query.message, callback_query.from_user.id)

# @dp.callback_query_handler(lambda c: c.data == 'pay_course')
# async def process_pay_course(callback_query: types.CallbackQuery):
#     await bot.answer_callback_query(callback_query.id)
#     await handle_pay_command(callback_query.message, callback_query.from_user.id)

# @dp.callback_query_handler(lambda c: c.data == 'earn_new_clients')
# async def process_earn_new_clients(callback_query: types.CallbackQuery):
#     await bot.answer_callback_query(callback_query.id)


# @dp.callback_query_handler(lambda c: c.data == 'get_referral')
# async def process_get_referral(callback_query: types.CallbackQuery):
#     await bot.answer_callback_query(callback_query.id)
#     await send_referral_link(callback_query.message, callback_query.from_user.id)

# @dp.callback_query_handler(lambda c: c.data == 'bind_card')
# async def process_get_referral(callback_query: types.CallbackQuery):
#     await bot.answer_callback_query(callback_query.id)
#     await bind_card(callback_query.message, callback_query.from_user.id)

# @dp.callback_query_handler(lambda c: c.data == 'generate_report')
# async def process_generate_report(callback_query: types.CallbackQuery):
#     await bot.answer_callback_query(callback_query.id)

# @dp.callback_query_handler(lambda c: c.data == 'report_overview')
# async def process_report_overview(callback_query: types.CallbackQuery):
#     await bot.answer_callback_query(callback_query.id)
#     await generate_overview_report(callback_query.message, callback_query.from_user.id)

# @dp.callback_query_handler(lambda c: c.data == 'report_clients')
# async def process_report_clients(callback_query: types.CallbackQuery):
#     await bot.answer_callback_query(callback_query.id)
#     await generate_clients_report(callback_query.message, callback_query.from_user.id)

# @dp.callback_query_handler(lambda c: c.data == 'tax_info')
# async def process_tax_info(callback_query: types.CallbackQuery):
#     await bot.answer_callback_query(callback_query.id)
 