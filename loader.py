from aiogram import Bot, Dispatcher
from aiogram.utils import executor
from aiogram.types import ParseMode, ChatInviteLink, Message, InlineKeyboardMarkup, InlineKeyboardButton, ChatMemberUpdated
from aiogram import types
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from config import (
    API_TOKEN
)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)