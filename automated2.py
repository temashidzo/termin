import time
import asyncio
import psutil
from helium import *
from selenium.webdriver import ChromeOptions
from telegram import Bot
from datetime import datetime

API_TOKEN = '7145016431:AAG3lyKT9PwtAbdX214izq5ZJApvRpU6DLY'
user_ids = [427509418, 156837559]
async def run_instance(config_line, user_ids, delay, line_number):
    user_ids = [427509418, 156837559]
    bot = Bot(token=API_TOKEN)  # Создаем экземпляр бота
    while True:
        start_time = datetime.now()
        print(f"Starting instance for line {line_number} at {start_time}")

        initial_cpu_usage = psutil.cpu_percent()
        initial_memory_usage = psutil.virtual_memory().used

        chrome_options = ChromeOptions()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        start_chrome('https://otv.verwalt-berlin.de/ams/TerminBuchen?lang=en', headless=True, options=chrome_options)

        actions = config_line.split('; ')
        for action in actions:
            exec(action.strip())

        time.sleep(15)  # Подождите, пока страница полностью загрузится или действия будут выполнены
        not_available_message = "There are currently"
        clickable_numbers = []
        if find_all(Text(not_available_message)):
            message = 'No dates for Palestine'
            success = False
        else:
            message = 'There are some available dates for Palestine'
            success = True
            available_dates_1_days = find_all(S("//div[contains(@class, 'ui-datepicker-group')][1]//table//a"))
            available_dates_1_month = find_all(S("//div[contains(@class, 'ui-datepicker-group')][1]//*[contains(@class, 'ui-datepicker-month')]"))[0].web_element.text
            available_dates_1_year = find_all(S("//div[contains(@class, 'ui-datepicker-group')][1]//*[contains(@class, 'ui-datepicker-year')]"))[0].web_element.text[:-5]
            available_dates_2_days = find_all(S("//div[contains(@class, 'ui-datepicker-group')][2]//table//a"))
            available_dates_2_month = find_all(S("//div[contains(@class, 'ui-datepicker-group')][2]//*[contains(@class, 'ui-datepicker-month')]"))[0].web_element.text
            available_dates_2_year = find_all(S("//div[contains(@class, 'ui-datepicker-group')][2]//*[contains(@class, 'ui-datepicker-year')]"))[0].web_element.text

            clickable_numbers_1 = [f"{date.web_element.text} {available_dates_1_month} {available_dates_1_year}" for date in available_dates_1_days if date.web_element.is_enabled()]
            clickable_numbers_2 = [f"{date.web_element.text} {available_dates_2_month} {available_dates_2_year}" for date in available_dates_2_days if date.web_element.is_enabled()]
            
            clickable_numbers = clickable_numbers_1 + clickable_numbers_2

        for user_id in user_ids:
            try:
                await bot.send_message(chat_id=user_id, text=message)
                if success:
                    for number in clickable_numbers:
                        await bot.send_message(chat_id=user_id, text=f"Available date: {number}")
            except Exception as e:
                print(f"Failed to send message to user {user_id}: {e}")

        final_cpu_usage = psutil.cpu_percent()
        final_memory_usage = psutil.virtual_memory().used

        cpu_usage = final_cpu_usage - initial_cpu_usage
        memory_usage = final_memory_usage - initial_memory_usage

        print(f"Instance completed at {datetime.now()}")
        print(f"Time taken: {datetime.now() - start_time}")
        print(f"CPU usage: {cpu_usage}")
        print(f"Memory usage: {memory_usage}")

        kill_browser()

        await asyncio.sleep(delay)  # Задержка перед следующим циклом

async def main():
    tasks = []
    delay = 3  # Задержка в секундах между итерациями

    with open('/Users/astonuser/Documents/Docs/PAFALL23/Applied Statistics/Test/Max_telegram/config.txt', 'r') as f:
        config_lines = f.readlines()                

    for index, line in enumerate(config_lines, start=1):
        tasks.append(run_instance(line.strip(), user_ids, delay, index))

    await asyncio.gather(*tasks)

asyncio.run(main())
