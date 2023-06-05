from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from connectivity_bot.telegram_wrapper import *
from logging.handlers import TimedRotatingFileHandler
import os
import signal
import telegram_interface
import itertools

cached_addresses = []

main_url = "https://www.pararius.com/apartments"
is_bot_enabled = True
is_first_cycle = True

def setup_logger(logger, log_config):

    log_dir = os.path.dirname(log_config['file'])
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    else:
        if log_config.get('clear',False) and os.path.isfile(log_config['file']) :
            os.remove(log_config['file'])

    logger = logging.getLogger(log_config.get('logger_name','pararius'))
    logger.setLevel(logging.DEBUG)

    rfh = TimedRotatingFileHandler(filename=log_config['file'],
                                   when='D',
                                   interval=1,
                                   backupCount=30)

    rfh.setLevel(log_config['level'])

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('[{}][{}][{} - {}][{}][{}]'.format('%(asctime)s',
        '%(filename)-21s','%(lineno)-3d','%(funcName)-24s','%(levelname)8s', '%(message)s'))
    formatter.converter = time.gmtime # Use the UTC Time
    rfh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(rfh)
    logger.addHandler(ch)

    logger.info('logger has been set')


def sleep_for_minutes(minute):
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    print("Current Time:", current_time)
    time.sleep(minute*60)


def browse_query(query):
    global is_first_cycle, cached_addresses
    driver.get(query)
    
    # Give at least 5 sec to load
    time.sleep(6)

    # Check if the captcha page is displayed
    is_captcha = driver.find_elements(By.ID, "_csnl_cp")
    if is_captcha:
        logger.error('Hit to Captcha !!!')
        TelegramBot.send_raw_message('Hit to Captcha !!!')
        raise ValueError('Hit to Captcha !!!')

    advertisements = []
    results = driver.find_elements(By.XPATH, "//span[@class='listing-label listing-label--new']")
    for result in results:
        adress = result.find_element(By.XPATH, "./../../div[@class=\"listing-search-item__sub-title'\"]").text
        advert_url = result.find_element(By.XPATH, "./../../h2[@class='listing-search-item__title']/a").get_attribute('href')
        advert_price = result.find_element(By.XPATH, "./../../div[@class='listing-search-item__price']").text
        advert_feature = result.find_element(By.XPATH, "./../../div[@class='listing-search-item__features']/ul").text.replace('\n',' | ')

        if adress in cached_addresses:
            continue
        else:
            message_dict = {'Address': adress, 'Price': advert_price, 'Feature': advert_feature, 'Link':advert_url}
            logger.info('New advertisement found: {}'.format(message_dict))
            advertisements.append(message_dict)
            cached_addresses.append(adress)
    return advertisements


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
    global is_first_cycle
    queries = build_queries()
    logger.debug(queries)

    browsed_advertisements = []
    for query in queries:

        advertisements = browse_query(query)
        browsed_advertisements.append(advertisements)

    browsed_ad_list = list(itertools.chain(*browsed_advertisements))

    if is_first_cycle:
        is_first_cycle = False
        logger.info('First cycle completed. Number of new advertisements that are just cached: {}'.format(len(browsed_ad_list)))
        return

    for ad in browsed_ad_list:
        TelegramBot.send_formatted_message('new_advert', ad)
        time.sleep(0.5)
    
    return  


if __name__ == "__main__":

    f = open(str(sys.argv[1]),'r')
    main_config = json.load(f)

    logger = logging.getLogger('pararius')
    setup_logger(logger, main_config['log'])

    f = open(main_config['telegram_config'],'r')
    telegram_config = json.load(f)

    telegram_interface.init_telegram_bot(telegram_config['token'], telegram_config['chat_id'])
    telegram_interface.start_telegram_bot()

    chrome_options = Options()
    if not main_config['enable_display']:
        chrome_options.add_argument('--headless=new')
        #chrome_options.add_argument("--remote-debugging-port=9222")  

    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(main_config['chrome_driver'], options=chrome_options)
    while(True):
        logger.debug('Iteration started')
        
        try:
            if not is_bot_enabled:
                continue


            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)
            print("Current Time:", current_time)
                
            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)
            print("Current Time:", current_time)
            application()
            driver.delete_all_cookies()
            sleep_for_minutes(main_config['polling_interval'])

        except ValueError as e:
            print(e)
            break
        except KeyboardInterrupt:
            break

    logger.info('Terminating')

    os.kill(os.getpid(), signal.SIGINT)