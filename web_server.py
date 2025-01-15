import os
from aiohttp import web
from loader import *
from utils import *

def web_server():
    async def handle(request):
        response_data = {"message": "pong"}
        return web.json_response(response_data)

    app = web.Application()
    app.router.add_route("HEAD", "/", handle)
    app.router.add_route("GET", "/", handle)
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

    log.info(f"Веб-сервер запущен на порту {PORT}")

    # Запуск бота с ожиданием завершения
    await executor.start_polling(dp, skip_updates=True)