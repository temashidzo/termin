from helium import *
from selenium.webdriver import ChromeOptions
import time
import random
from selenium.webdriver.support.ui import Select
from telegram import Bot
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
API_TOKEN = '7145016431:AAG3lyKT9PwtAbdX214izq5ZJApvRpU6DLY'

user_id = 156837559
message = 'Pidor'
# Отправка сообщения пользователю в телеграм-чате
async def send_message_to_user(user_id, message):
    bot = Bot(token=API_TOKEN)
    await bot.send_message(chat_id=user_id, text=message)

# Запуск асинхронной функции для отправки сообщения
import asyncio
asyncio.run(send_message_to_user(user_id, message))