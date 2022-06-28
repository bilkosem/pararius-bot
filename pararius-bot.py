from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from connectivity_bot.TelegramHandler import *
import os
import signal
cached_addresses = []

main_url = "https://www.pararius.com/apartments"
is_bot_enabled = True

def configure_telegrambot(token, chat_id):
    TelegramBot.setToken(token)
    TelegramBot.setChatId(chat_id)

    TelegramBot.add_handler(CommandHandler('start', start), description="start application")
    TelegramBot.add_handler(CommandHandler('stop', stop), description="stop application")
    TelegramBot.add_handler(CommandHandler('kill', TelegramBot.kill), description="kill application")
    TelegramBot.add_handler(CommandHandler('help', TelegramBot.help), description="")
    TelegramBot.add_handler(MessageHandler(Filters.text, unknown))
    TelegramBot.add_handler(MessageHandler(Filters.command, unknown)) 
    TelegramBot.add_handler(MessageHandler(Filters.text, unknown_text))

    # How to get chatId: https://api.telegram.org/bot<YourBOTToken>/getUpdates

    format = TelegramMessageFormat('Header','\ntailer','\n        ','/{}: {}')
    TelegramBot.add_format('help', format, constant_data=TelegramBot.command_desc)
    #TelegramBot.send_formatted_message('help')
    new_advert_format = TelegramMessageFormat('New advert found','','\n        ','{}: {}')
    TelegramBot.add_format('new_advert',new_advert_format)


def start(update: Update, context: CallbackContext):
    global is_bot_enabled
    update.message.reply_text("Starting the bot...")
    is_bot_enabled = True


def stop(update: Update, context: CallbackContext):
    global is_bot_enabled
    update.message.reply_text("Stopping the bot...")
    is_bot_enabled = False


def sleep_for_minutes(minute):
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    print("Current Time:", current_time)
    time.sleep(minute*60)


def browse_query(query):
    driver.get(query)

    # Check if the captcha page is displayed
    is_captcha = driver.find_elements(By.ID, "_csnl_cp")
    if is_captcha or not is_captcha:
        TelegramBot.send_raw_message('Hit to Captcha !!!')
        raise ValueError('Hit to Captcha !!!')

    results = driver.find_elements(By.XPATH, "//span[@class='listing-label listing-label--new']")
    for result in results:
        adress = result.find_element(By.XPATH, "./../../div[@class='listing-search-item__location']").text
        advert_url = result.find_element(By.XPATH, "./../../h2[@class='listing-search-item__title']/a").get_attribute('href')
        advert_price = result.find_element(By.XPATH, "./../../div[@class='listing-search-item__price']").text
        advert_feature = result.find_element(By.XPATH, "./../../div[@class='listing-search-item__features']/ul").text.replace('\n',' | ')
        print(f"Address found {adress}")

        if adress in cached_addresses:
            continue
        else:
            message_dict = {'Address': adress, 'Price': advert_price, 'Feature': advert_feature, 'Link':advert_url}
            print(message_dict)
            TelegramBot.send_formatted_message('new_advert', message_dict)
            cached_addresses.append(adress)


def build_queries():
    query_urls = []

    for city in main_config['query']["city"]:
        url = main_url
        url += f'/{city}'

        if main_config['query']["price"]["from"] != 0 and main_config['query']["price"]["to"] != 0:
            url += f'/{main_config["query"]["price"]["from"]}-{main_config["query"]["price"]["to"]}'

        if main_config["query"]["room"] == "":
            url += f'/{main_config["query"]["room"]}-rooms'
        
        url += f'/{main_config["query"]["type"]}'
        query_urls.append(url)
    
    return query_urls


def application():
    queries = build_queries()
    print(queries)
    for query in queries:
        browse_query(query)


if __name__ == "__main__":
    # TODO: Add logging
    f = open(str(sys.argv[1]),'r')
    main_config = json.load(f)

    f = open(main_config['telegram_config'],'r')
    telegram_config = json.load(f)

    configure_telegrambot(telegram_config['token'], telegram_config['chat_id'])
    TelegramBot.updater.start_polling()
    
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)

    if not main_config['enable_display']:
        chrome_options.add_argument('--headless')
        chrome_options.add_argument("--remote-debugging-port=9222")  
    from webdriver_manager.chrome import ChromeDriverManager

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    #driver = webdriver.Chrome(main_config['chrome_driver'], options=chrome_options)
    while(True):
        print('starting a cycle')
        try:
            if not is_bot_enabled:
                continue

            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)
            print("Current Time:", current_time)
            application()
                
            sleep_for_minutes(main_config['polling_interval'])
        except ValueError as e:
            print(e)
            break
        except KeyboardInterrupt:
            TelegramBot.updater.stop()
            break

    print('Terminating bot')
    os.kill(os.getpid(), signal.SIGINT)