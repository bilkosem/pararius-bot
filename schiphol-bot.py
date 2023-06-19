import time
from connectivity_bot.telegram_wrapper import *
from logging.handlers import TimedRotatingFileHandler
import os
import signal
import telegram_interface
import itertools

is_bot_enabled = True

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

def application():

    time.sleep(1)
    
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


    while(True):
        
        try:
            if not is_bot_enabled:
                continue

            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)
            application()

        except Exception as e:
            logger.error(e, exc_info=True)
            TelegramBot.send_raw_message('Error: {}'.format(e))
            break
        except KeyboardInterrupt:
            break

    logger.info('Terminating')
    TelegramBot.send_raw_message('Terminating...')
    os.kill(os.getpid(), signal.SIGINT)