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
    bot = Bot(token=API_TOKEN)  # Создаем экземпляр бота один раз

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
        start_chrome('https://otv.verwalt-berlin.de/ams/TerminBuchen?lang=en', headless=True, options=chrome_options)

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
        time.sleep(15)

        not_available_message = "There are currently"
        clickable_numbers = []
        if find_all(Text(not_available_message)):
            message = 'No dates for Palestine'
            success = False
        else:
            message = 'There are some available dates for Palestine'
            success = True
            # Найти все элементы с классом 'ui-state-default ui-state-active', которые содержат кликабельные числа
            available_dates_1_days = find_all(S("//div[contains(@class, 'ui-datepicker-group')][1]//table//a"))

            available_dates_1_month = find_all(S("//div[contains(@class, 'ui-datepicker-group')][1]//*[contains(@class, 'ui-datepicker-month')]"))[0].web_element.text
            available_dates_1_year = find_all(S("//div[contains(@class, 'ui-datepicker-group')][1]//*[contains(@class, 'ui-datepicker-year')]"))[0].web_element.text[:-5]
            
            available_dates_2_days = find_all(S("//div[contains(@class, 'ui-datepicker-group')][2]//table//a"))
            available_dates_2_month = find_all(S("//div[contains(@class, 'ui-datepicker-group')][2]//*[contains(@class, 'ui-datepicker-month')]"))[0].web_element.text
            available_dates_2_year = find_all(S("//div[contains(@class, 'ui-datepicker-group')][2]//*[contains(@class, 'ui-datepicker-year')]"))[0].web_element.text
            # Извлечь текст из этих элементов и добавить в список
            clickable_numbers_1 = [f"{date.web_element.text} {available_dates_1_month} {available_dates_1_year}" for date in available_dates_1_days if date.web_element.is_enabled()]
            clickable_numbers_2 = [f"{date.web_element.text} {available_dates_2_month} {available_dates_2_year}" for date in available_dates_2_days if date.web_element.is_enabled()]
            
            clickable_numbers = clickable_numbers_1 + clickable_numbers_2

        # Отправка сообщения каждому пользователю в телеграм-чате
        for user_id in user_ids:
            try:
                await bot.send_message(chat_id=user_id, text=message)
                print(f"Message sent to user {user_id} successfully")
                if success:
                    for number in clickable_numbers:
                        await bot.send_message(chat_id=user_id, text=f"Available dates: {number}")
                        print(f"Date {number} sent to user {user_id} successfully")
            except Exception as e:
                print(f"Failed to send message to user {user_id}:", e)

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
        print("Memory usage:", memory_usage, "\n")

        # Закрываем браузер
        kill_browser()

        # Ждем 1.5 минуты перед следующим запуском
        await asyncio.sleep(1)  # Используйте asyncio.sleep вместо time.sleep в асинхронном коде

# Запуск асинхронной функции для выполнения скрипта
asyncio.run(main())