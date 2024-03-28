import time
import asyncio
import psutil
from helium import *
from selenium.webdriver import ChromeOptions
from telegram import Bot
from datetime import datetime

API_TOKEN = '7145016431:AAG3lyKT9PwtAbdX214izq5ZJApvRpU6DLY'

async def main():
    user_ids = [427509418, 156837559]  # список пользователей

    while True:
        start_time = datetime.now()
        print("Starting instance at", start_time)

        # Измеряем начальное использование ресурсов
        initial_cpu_usage = psutil.cpu_percent()
        initial_memory_usage = psutil.virtual_memory().used

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
        press('*unresolved nationality (Palestinians and Kurds)')
        time.sleep(2)
        click(S('select#xi-sel-423'))
        press('no')
        click(S('select#xi-sel-426'))
        press('one')
        click(S('select#xi-sel-427'))
        press('no')

        # Запуск процедуры бронирования
        click('Aufenthaltsge')
        time.sleep(3)
        wait_until(Text("Permission to reside").exists)
        click('Permission to reside')
        write('Gasel', into='Please enter your surname')
        time.sleep(2)
        click('Next')
        time.sleep(5)
        click('Next')
        time.sleep(12)

        not_available_message = "There are currently"
        if find_all(Text(not_available_message)):
            message = 'No dates'
            success = False
        else:
            message = 'There are some available dates for Palestine'
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

        # Измеряем конечное использование ресурсов
        final_cpu_usage = psutil.cpu_percent()
        final_memory_usage = psutil.virtual_memory().used

        # Вычисляем разницу
        cpu_usage = final_cpu_usage - initial_cpu_usage
        memory_usage = final_memory_usage - initial_memory_usage

        end_time = datetime.now()
        print("Instance completed at", end_time)
        print("Time taken:", end_time - start_time)
        print("CPU usage:", cpu_usage)
        print("Memory usage:", memory_usage)
        print("Success:", success)

        # Закрываем браузер
        kill_browser()

        # Ждем 1.5 минуты перед следующим запуском
        time.sleep(1)


# Запуск асинхронной функции для выполнения скрипта
asyncio.run(main())