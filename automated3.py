import asyncio
import multiprocessing
import psutil
import time
from datetime import datetime
from helium import *
from selenium.webdriver import ChromeOptions
from telegram import Bot

API_TOKEN = '7145016431:AAG3lyKT9PwtAbdX214izq5ZJApvRpU6DLY'  # Замените на ваш токен API Telegram
USER_IDS = [427509418, 156837559]  # список пользователей

async def main(config_line, process_num):
    bot = Bot(token=API_TOKEN)  # Создаем экземпляр бота один раз
    user_ids = [427509418, 156837559]
    
    start_time = datetime.now()
    print(f"Started process {process_num}", "\n")

    # Измеряем начальное использование ресурсов
    initial_cpu_usage = psutil.cpu_percent()
    initial_memory_usage = psutil.virtual_memory().used

    # Создаем и настраиваем окно браузера
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    start_chrome('https://otv.verwalt-berlin.de/ams/TerminBuchen?lang=en', headless=False, options=chrome_options)

    # Загрузка последовательности действий из файла конфигурации
    actions = config_line.split('; ')
    last_press_action = None
    for action in actions:
        if 'press' in action:
            last_press_action = action.strip()
            break

    # Получим элемент из последнего действия press
    element = last_press_action.split("'")[-2]

    # Выполнение последовательности действий
    for action in actions:
        exec(action.strip())  # Выполняем действие, убирая лишние пробелы и символы новой строки

    time.sleep(15)
    not_available_message_1 = "There is currently"
    not_available_message_2 = "There are currently"
    clickable_numbers = []
    if find_all(Text(not_available_message_1)) or find_all(Text(not_available_message_2)):
        message = 'No dates for ' + element
        success = False
    else:
        message = 'There are some available dates for ' + element
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

    # Код для отправки сообщений в телеграм и т.д.
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
    print(f"Starting instance {process_num} at", start_time)
    print("Instance completed at", end_time)
    print("Time taken:", end_time - start_time)
    print("CPU usage:", cpu_usage)
    print("Memory usage:", memory_usage, "\n")

    # Закрываем браузер
    kill_browser()

    # Ждем 1.5 минуты перед следующим запуском
    await asyncio.sleep(5)  # Используйте asyncio.sleep вместо time.sleep в асинхронном коде

# Функция, которая будет использоваться для запуска асинхронной функции main() в отдельном процессе
def run_async_main(config_line, process_num):
    asyncio.run(main(config_line, process_num))

if __name__ == "__main__":
    # Чтение строк из файла конфигурации
    with open('/Users/astonuser/Documents/Docs/PAFALL23/Applied Statistics/Test/Max_telegram/config.txt', 'r') as f:
        config_lines = f.readlines()

    # Создаем процессы для каждой строки из файла конфигурации
    processes = []
    for i, config_line in enumerate(config_lines, start=1):
        process = multiprocessing.Process(target=run_async_main, args=(config_line, i))
        processes.append(process)
        process.start()

    # Ждем завершения всех процессов
    for process in processes:
        process.join()
