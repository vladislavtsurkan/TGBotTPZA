from aiogram import Bot
from aiogram.dispatcher import Dispatcher

from os import getenv

TOKEN = getenv('BOT_TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
