from helium import *
import time
import asyncio
from selenium.webdriver import ChromeOptions
from telegram import Bot
from datetime import datetime


API_TOKEN = '7145016431:AAG3lyKT9PwtAbdX214izq5ZJApvRpU6DLY'

async def main():
    user_ids = [427509418, 156837559]  # список пользователей

    while True:
        start_time = datetime.now()
        print("Starting instance at", start_time)

        # Создаем и настраиваем окно браузера
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        start_chrome('https://otv.verwalt-berlin.de/ams/TerminBuchen?lang=en', headless=False, options=chrome_options)

        # Клик по кнопке для перехода к бронированию
        click('Book Appointment')
        scroll_down(num_pixels=150)
        click('I hereby')
        # Ваш код для клика по кнопке согласия
        click('NEXT')

        # Выбор языка и других опций
        click(S('select#xi-sel-400'))
        press('Russian')
        click(S('select#xi-sel-422'))
        press('one')
        click(S('select#xi-sel-427'))
        press('no')

        # Запуск процедуры бронирования
        click('Transfer')
        click('Transfer of a Blue')
        time.sleep(5)
        click('Next')
        time.sleep(12)

        not_available_message = "There are currently"
        if find_all(Text(not_available_message)):
            message = 'No dates'
            success = False
        else:
            message = 'There are some available dates'
            success = True

        # Отправка сообщения каждому пользователю в телеграм-чате
        for user_id in user_ids:
            try:
                bot = Bot(token=API_TOKEN)
                await bot.send_message(chat_id=user_id, text=message)
                print(f"Message sent to user {user_id} successfully")
            except Exception as e:
                print(f"Failed to send message to user {user_id}:", e)
                success = False

        end_time = datetime.now()
        print("Instance completed at", end_time)
        print("Time taken:", end_time - start_time)
        print("Success:", success)

        # Закрываем браузер
        kill_browser()

        # Ждем 1.5 минуты перед следующим запуском


# Запуск асинхронной функции для выполнения скрипта
asyncio.run(main())
