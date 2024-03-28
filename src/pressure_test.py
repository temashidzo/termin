from helium import *
from selenium.webdriver import ChromeOptions
import time
import random
from multiprocessing import Process, Manager

def run_script(return_dict, process_id):
    start_time = time.time()
    
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    
    browser = start_chrome('https://otv.verwalt-berlin.de/ams/TerminBuchen?lang=en', headless=True, options=chrome_options)

    
    click('Book Appointment')

    
    scroll_down(num_pixels=150)

    
    click('I hereby')
    click('NEXT')


    click(S('select#xi-sel-400'))
    press('Alb')


    click(S('select#xi-sel-422'))
    press('one')

    kill_browser()
    
    end_time = time.time()
    duration = end_time - start_time
    return_dict[process_id] = duration
    print(f"Process {process_id} finished in {duration} seconds.")

if __name__ == "__main__":
    manager = Manager()
    return_dict = manager.dict()
    
    processes = []
    number_of_processes = 20  # Вы можете изменить это число, чтобы запустить больше процессов
    
    for i in range(number_of_processes):
        process = Process(target=run_script, args=(return_dict, i))
        process.start()
        processes.append(process)
    
    for process in processes:
        process.join()
    
    durations = return_dict.values()
    if durations:
        average_time = sum(durations) / len(durations)
        max_time = max(durations)
        min_time = min(durations)
        print(f"Average time per instance: {average_time} seconds")
        print(f"Max time: {max_time} seconds")
        print(f"Min time: {min_time} seconds")
