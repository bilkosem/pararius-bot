from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from connectivity_bot.TelegramHandler import *

cached_addresses = []

config = {
    "city": ["amsterdam"],
    "price":{
        "from":0,
        "to":0
    },
    "room": "",
    "type": ""
}
xpaths = {
    "new": "//span[@class='listing-label listing-label--new']"

}
main_url = "https://www.pararius.com/apartments"



def configure_telegrambot(token, chat_id):
    TelegramBot.setToken(token)
    TelegramBot.setChatId(chat_id)

    TelegramBot.add_handler(CommandHandler('start', start), description="start desc")
    TelegramBot.add_handler(CommandHandler('help', TelegramBot.help), description="")
    TelegramBot.add_handler(MessageHandler(Filters.text, unknown))
    TelegramBot.add_handler(MessageHandler(Filters.command, unknown)) 
    TelegramBot.add_handler(MessageHandler(Filters.text, unknown_text))

    # How to get chatId: https://api.telegram.org/bot<YourBOTToken>/getUpdates
    TelegramBot.send_raw_message("dummy message")

    format = TelegramMessageFormat('Header','\ntailer','\n        ','/{}: {}')
    TelegramBot.add_format('help', format, constant_data=TelegramBot.command_desc)
    TelegramBot.send_formatted_message('help')
    new_advert_format = TelegramMessageFormat('New advert found','','\n        ','{}: {}')
    TelegramBot.add_format('new_advert',new_advert_format)

def sleep_for_seconds(sec):
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    print("Current Time:", current_time)
    time.sleep(sec) # retry after 10 minutes


def browse_query(query):
    driver.get(query)

    results = driver.find_elements(By.XPATH, xpaths['new'])
    for result in results:
        adress = result.find_element(By.XPATH, "./../../div[@class='listing-search-item__location']").text
        #link = result.find_element(By.XPATH, "./../../h2[@class='listing-search-item__title']")

        if adress in cached_addresses:
            continue
        else:
            # Do sth
            #notify()
            TelegramBot.send_formatted_message('new_advert',{'Address': adress})
            cached_addresses.append(adress)
    return 0


def build_queries():
    query_urls = []

    for city in config["city"]:
        url = main_url
        url += f'/{city}'
        if config["price"]["from"] != 0 and config["price"]["to"] != 0:
            url += f'/{config["price"]["from"]}-{config["price"]["to"]}'
        url += f'/{config["room"]}-rooms'
        url += f'/{config["type"]}'
        query_urls.append(url)
    
    return query_urls


def application():
    queries = build_queries()
    print(queries)
    for query in queries:
        browse_query(query)
    pass

if __name__ == "__main__":
    f = open(str(sys.argv[1]),'r')
    telegram_config = json.load(f)
    configure_telegrambot(telegram_config['Telegram']['Token'], telegram_config['Telegram']['ChatId'])


    TelegramBot.updater.start_polling()
    print("after start polling")
    
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome("D:\Downloads\chromedriver_win32 (1)\chromedriver.exe")
    while(True):
        try:
            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)
            print("Current Time:", current_time)
            application()
            sleep_for_seconds(10)
        except KeyboardInterrupt:
            print("keyboard interrupy")
            TelegramBot.updater.stop()
            break

    print("after while")